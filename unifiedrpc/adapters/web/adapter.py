# encoding=utf8
# The web RPC adapter

"""The web RPC adapter

The known configs:

    request.encoding                    The default request encoding to use
    response.mimeType                   The default response mime type to use
    response.encoding                   The default response encoding to use
    cookie.secret                       The cookie secret string to use

"""

import logging
import traceback

from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wrappers import Response as WKResponse
from werkzeug.datastructures import Headers
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.utils import get_content_type

from unifiedrpc.adapters import Adapter
from unifiedrpc.protocol import Context, Request, Response, Dispatch
from unifiedrpc.protocol.request import RequestContent
from unifiedrpc.errors import *
from unifiedrpc.definition import CONFIG_REQUEST_ENCODING

from definition import ENDPOINT_CHILDREN_WEBENDPOINT_KEY
from request import WebRequest

# Bind errors to http status code
ERROR_BINDINGS = {
    BadRequestError:                400,
    BadRequestParameterError:       400,
    BadRequestContentError:         400,
    UnauthorizedError:              401,
    ForbiddenError:                 403,
    NotFoundError:                  404,
    NotAcceptableError:             406,
    RequestTimeoutError:            408,
    LengthRequiredError:            411,
    RequestEntityTooLargeError:     413,
    UnsupportedMediaTypeError:      415,
    InternalServerError:            500,
}

class WebAdapter(Adapter):
    """The web adapter
    This is the basic web adapter class, also a WSGI compatible class
    NOTE:
        This adapter doesn't implement the 'startAsync' and 'close' method, so it couldn't be
        used instanced directly to insert into rpc server
    """
    type = 'web'
    logger = logging.getLogger('unifiedrpc.adapter.web')

    REQUEST_CLASS       = WebRequest

    def __init__(self, name, host, port, **configs):
        """Create a new WebAdapter
        Parameters:
            name                        The adapter name
            host                        The bound host
            port                        The bound port
            configs                     The adapter configs
        """
        # Check parameters
        if not isinstance(host, basestring):
            raise TypeError('Invalid parameter host, require string type actually got [%s]' % type(host).__name__)
        if not isinstance(port, int):
            raise TypeError('Invalid parameter port, require int type actually got [%s]' % type(port).__name__)
        # Set
        self.host = host
        self.port = port
        self.endpoints = None       # A dict, key is web endpoint id, value is (WebEndpoint, Endpoint) object
        self.urlMapper = None       # A werkzeug.routing.Map object
        self.onRequestCallback = None
        self.onErrorCallback = None
        # Super
        super(WebAdapter, self).__init__(name, **configs)

    def __call__(self, environ, startResponse):
        """The WSGI entry
        Parameters:
            environ                     The environment
            startResponse               The callback method to start response
        Returns:
            Yield or list of string for http response content
        """
        try:
            context = self.onRequest((environ, startResponse))
            return self.respond(context)
        except Exception as error:
            # Report the error
            self.onError(error, traceback.format_exc(), 'Failed to complete the WSGI call')
            # Under this circumstance, the response should be a simple 500 error
            try:
                startResponse('500 %s' % HTTP_STATUS_CODES[500], [ ]) # Respond 500 with no header
            except Exception as innerError:
                # Report this error
                self.onError(innerError, traceback.format_exc(), 'Failed to call startResponse when handling a critical error')
            # Return nothing
            return tuple()

    def parseRequest(self, incoming, context):
        """Parse the request, set the context
        """
        environ, startResponse = incoming
        # Parse the request
        rawRequest = self.REQUEST_CLASS(environ, startResponse)
        # Check the encoding
        if not rawRequest.requestContent.encoding:
            encoding = self.configs.get(CONFIG_REQUEST_ENCODING)
            if not encoding:
                encoding = context.server.configs.get(CONFIG_REQUEST_ENCODING, context.server.DEFAULT_REQUEST_ENCODING)
            rawRequest.requestContent.encoding = encoding
        # Create the protocol request
        request = Request(
            headers = rawRequest.headers,
            params = rawRequest.queryParams,
            content = rawRequest.requestContent,
            accept = rawRequest.acceptContent,
            raw = rawRequest
            )
        # Set the context
        context.request = request

    def initResponse(self, incoming, context):
        """Initialize the response, set the context
        """
        # Create the protocol response, and set the context
        context.response = Response()

    def dispatch(self, context):
        """Dispatch the request
        """
        # Check parameters
        if not self.endpoints or not self.urlMapper:
            raise NotFoundError
        # Map the url
        try:
            urlAdapter = self.urlMapper.bind_to_environ(context.request.raw.environ)
            webEndpointID, urlParams = urlAdapter.match()
        except NotFound:
            raise NotFoundError
        # Get the endpoint
        res = self.endpoints.get(webEndpointID)
        if not res:
            raise NotFoundError
        webEndpoint, endpoint = res
        # Create the params
        params = {}
        if urlParams:
            params.update(urlParams)
        if context.request.raw.queryParams:
            params.update(context.request.raw.queryParams)
        # NOTE:
        #   Here, we don't check if the parameters are fit since there may have other processors to change the params
        #   We leave this to the place right before invoking endpoint itself
        # Set the dispatcher
        context.dispatch = Dispatch(
            endpoint,
            params,
            endpointID = endpoint.id,
            webEndpointID = webEndpointID,
            urlParams = urlParams,
            webEndpoint = webEndpoint
            )

    def onRequest(self, incoming):
        """On request
        Parameters:
            incoming                        The incoming (envion, startResponse)
        Returns:
            response content or None
        """
        cb = self.onRequestCallback
        if not cb:
            raise RuntimeError('Request callback not found')
        # Done
        return cb(incoming, self)

    def onError(self, error, traceback = None, message = None):
        """On process error
        """
        cb = self.onErrorCallback
        if not cb:
            raise RuntimeError('Error callback not found')
        # Done
        return cb(error, self, traceback, message)

    def handleError(self, error, traceback, incoming, context):
        """Handle the request error
        Parameters:
            error                       The error object
            traceback                   The traceback string
            incoming                    The incoming parameters
            context                     The context
        Returns:
            Nothing
        """
        environ, startResponse = incoming
        # Check error bindings
        if type(error) in ERROR_BINDINGS:
            # Good, found it
            context.response.status = ERROR_BINDINGS[type(error)]
        elif isinstance(error, HTTPException):
            # A werkzeug http exception
            context.response.werkzeug = error.get_response(context.request.raw.environ)
        else:
            # Treat as internal server error
            context.response.status = 500

    def setEndpoints(self, endpoints):
        """Set the endpoints
        """
        totalWebEndpoints = {}      # A dict of endpoint
        urlRules = []               # A list of url routing rules
        for endpoint in endpoints:
            # Get the web endpoint
            webEndpoints = endpoint.children.get(ENDPOINT_CHILDREN_WEBENDPOINT_KEY)
            if webEndpoints:
                for webEndpoint in webEndpoints.itervalues():
                    # Good, lets add this endpoint
                    if webEndpoint.id in totalWebEndpoints:
                        raise ValueError('Web endpoint id [%s] duplicated' % webEndpoint.id)
                    totalWebEndpoints[webEndpoint.id] = (webEndpoint, endpoint)
                    # Get the methods
                    if not webEndpoint.method:
                        methods = None
                    elif isinstance(webEndpoint.method, basestring):
                        methods = (webEndpoint.method, )
                    else:
                        methods = webEndpoint.method
                    # Add the rule
                    urlRules.append(Rule(webEndpoint.path, endpoint = webEndpoint.id, methods = methods, host = webEndpoint.host, subdomain = webEndpoint.subdomain))
        # Done
        self.endpoints = totalWebEndpoints
        self.urlMapper = Map(urlRules)

    def respond(self, context = None):
        """Respond the request
        Parameters:
            context                             The Context object
        Returns:
            Nothing
        NOTE:
            Call this method out of __call__ method context will cause response headers to be returned
        """
        if not context:
            context = Context.current()
        # Create the response object
        if not hasattr(context.response, 'werkzeug'):
            response = WKResponse(
                context.response.content,
                status = context.response.status,
                headers = context.response.headers.items(),
                content_type = get_content_type(context.response.mimeType, context.response.encoding)
                )
        else:
            # NOTE: This is a little tricky to directly use the werkzeug response when error occurred
            response = context.response.werkzeug
        # Check if the request has already responded
        if hasattr(context, 'responded') and context.responded:
            # Responded, get the response content, only return the content without calling startResponse again
            app_iter, status, headers = response.get_wsgi_response(context.request.environ)
            return app_iter
        else:
            # Respond
            context.responded = True
            return response(context.request.raw.environ, context.request.raw.startResponse)

    def startAsync(self, onRequestCallback, onErrorCallback, endpoints):
        """Start asynchronously
        """
        # Set endpoints
        self.setEndpoints(endpoints)
        # Set callback
        self.onRequestCallback = onRequestCallback
        self.onErrorCallback = onErrorCallback

    def close(self):
        """Close current adapter
        """
        self.endpoints = None
        self.urlMapper = None
        self.onRequestCallback = None
        self.onErrorCallback = None

class GeventWebAdapter(WebAdapter):
    """The gevent web adapter
    This is a gevent-bound web adapter which should be used in gevent rpc server
    """
    def __init__(self, name, host, port, **configs):
        """Create a new GeventWebAdapter
        """
        self.server = None
        # Super
        super(GeventWebAdapter, self).__init__(name, host, port, **configs)

    def startAsync(self, onRequestCallback, onErrorCallback, endpoints):
        """Start asynchronously
        """
        if not onRequestCallback:
            raise ValueError('Require parameter onRequestCallback')
        if self.server:
            raise ValueError('Adapter has already started')
        # Super
        super(GeventWebAdapter, self).startAsync(onRequestCallback, onErrorCallback, endpoints)
        # Start gevent wsgi server
        from gevent import pywsgi
        # Get logger
        serverLogger = logging.getLogger('unifiedrpc.adapter.web.gevent')
        self.server = pywsgi.WSGIServer(
            (self.host, self.port),
            self,       # The application callable object
            log = pywsgi.LoggingLogAdapter(serverLogger, logging.INFO),
            error_log = pywsgi.LoggingLogAdapter(serverLogger, logging.ERROR),
            )
        self.server.start()
        # Log it
        self.logger.info('Gevent WSGI server starts service at %s:%d', self.host, self.port)

    def close(self):
        """Close current adapter
        """
        if not self.server:
            raise ValueError('Adapter hasn\'t started')
        self.server.close()
        self.server = None
        # Super
        super(GeventWebAdapter, self).close()
