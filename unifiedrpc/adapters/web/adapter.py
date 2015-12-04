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

from gevent import pywsgi

from werkzeug.routing import Map
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wrappers import Response as WKResponse, Response as WKResponse
from werkzeug.datastructures import Headers
from werkzeug.http import HTTP_STATUS_CODES

from unifiedrpc import context, contextspace
from unifiedrpc.adapters import Adapter
from unifiedrpc.protocol import Context, Request, Response, Dispatcher
from unifiedrpc.protocol.request import RequestContent
from unifiedrpc.errors import *
from unifiedrpc.definition import CONFIG_REQUEST_ENCODING

from definition import ENDPOINT_CHILDREN_WEBENDPOINT_KEY, \
        CONFIG_SESSION_MANAGER
from request import WebRequest
from response import WebResponse
from util import getContentType

STAGE_BEFORE_REQUEST    = 0
STAGE_BEFORE_DISPATCH   = 1
STAGE_BEFORE_RESPONSE   = 2
STAGE_BEFORE_HANDLER    = 3
STAGE_BEFORE_SETVALUE   = 4
STAGE_BEFORE_FORMATING  = 5
STAGE_BEFORE_RESPOND    = 6
STAGE_DONE              = 7

# Bind errors to http status code
ERROR_BINDINGS = {
    BadRequestError:                400,
    BadRequestParameterError:       400,
    BadRequestBodyError:            400,
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
    RESPONSE_CLASS      = WebResponse

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
        # Set basic attributes
        self.host = host
        self.port = port
        self.endpoints = {}         # A dict, key is web endpoint id, value is (WebEndpoint, Endpoint) object
        self.urlMapper = None       # A werkzeug.routing.Map object
        # Session
        self.sessionManager = configs.get(CONFIG_SESSION_MANAGER)
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
        # Here, we create a context space
        with contextspace(self.server, self):
            # The context variable is available in this context
            self.server.initContext(context)
            stage = STAGE_BEFORE_REQUEST
            try:
                # Parse the rqequest
                context.request = self.REQUEST_CLASS(environ)
                # Parse the request content stream if have one
                if context.request.content and context.request.content.mimeType:
                    # Get the default encoding if not specified
                    if not context.request.content.encoding:
                        encoding = self.configs.get(CONFIG_REQUEST_ENCODING)
                        if not encoding:
                            encoding = context.server.configs.get(CONFIG_REQUEST_ENCODING, context.server.DEFAULT_REQUEST_ENCODING)
                        context.request.content.encoding = encoding
                    # Parse the content data
                    context.request.content.data = context.components.contentParser.parse(context)
                # Get session
                if self.sessionManager:
                    context.session = self.sessionManager.get(context.request)
                # Dispatch
                stage = STAGE_BEFORE_DISPATCH
                context.dispatcher = self.dispatch()
                # Create the response object
                stage = STAGE_BEFORE_RESPONSE
                context.response = self.RESPONSE_CLASS()
                context.server.initResponse(context)
                # TODO: Set the response by adapter and endpoint config
                # Invoke the endpoint
                stage = STAGE_BEFORE_HANDLER
                value = context.dispatcher.endpoint.pipeline(context)
                # Set session
                if self.sessionManager:
                    if context.shouldCleanSession:
                        self.sessionManager.clean(context.response)
                    else:
                        self.sessionManager.set(context.session, context.response)
                # Check the value, if it is a response object, then just return
                if isinstance(value, WKResponse):
                    # Skip all following steps
                    return value(environ, startResponse)
                # Set the value to container
                stage = STAGE_BEFORE_SETVALUE
                context.response.container.setValue(value)
                # Build context
                stage = STAGE_BEFORE_FORMATING
                context.response.content = context.components.contentBuilder.build(context)
                # Return the response
                stage = STAGE_BEFORE_RESPOND
                return context.response(environ, startResponse)
                # Well, done
                stage = STAGE_DONE
            except Exception as error:
                # Error happened
                # Check error type
                if not type(error) in ERROR_BINDINGS:
                    # Log the error with details
                    self.logger.exception('Failed to handle http request')
                    # Create a internal server error
                    status = 500
                    error = InternalServerError(ERRCODE_UNDEFINED)
                else:
                    # A http error
                    status = ERROR_BINDINGS[type(error)]
                    self.logger.error(str(error))
                # Check stage
                if stage <= STAGE_BEFORE_RESPONSE:
                    # Create the response
                    try:
                        context.response = self.RESPONSE_CLASS(status = status)
                        context.server.initResponse(context)
                    except:
                        # Failed to initialize the response, will use the default response
                        self.logger.exception('Failed to initialize the response when handling error')
                        return WKResponse(status = status)(environ, startResponse)
                else:
                    # Set the response status
                    context.response.status_code = status
                # Set the error response
                try:
                    context.response.container.setError(error.code, error.reason, error.detail)
                except:
                    # Failed to set error to container
                    self.logger.exception('Failed to set error to container when handling error')
                    return WKResponse(status = status)(environ, startResponse)
                # Format value
                try:
                    context.response.content = context.components.contentBuilder.build(context)
                except:
                    # Failed to build content
                    self.logger.exception('Failed to build content when handling error')
                    return WKResponse(status = status)(environ, startResponse)
                # Return the response
                try:
                    return context.response(environ, startResponse)
                except:
                    # Failed to respond
                    self.logger.exception('Failed to respond when handling error')
                    return WKResponse(status = status)(environ, startResponse)

    def dispatch(self):
        """Dispatch the request for current context
        Returns:
            Dispatcher object
        """
        # Check parameters
        if not self.endpoints or not self.urlMapper:
            raise NotFoundError
        # Map the url
        try:
            urlAdapter = self.urlMapper.bind_to_environ(context.request.environ)
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
        if context.request.params:
            params.update(context.request.params)
        # NOTE:
        #   Here, we don't check if the parameters are fit since there may have other processors to change the params
        #   We leave this to the place right before invoking endpoint itself
        # Return the dispatcher
        return Dispatcher(endpoint, params, endpointID = endpoint.id, webEndpointID = webEndpointID, urlParams = urlParams, webEndpoint = webEndpoint)

    def getWebEndpointsFromService(self, service):
        """Get web endpoints from service
        """
        endpoints = service.getEndpoints()
        if endpoints:
            for endpoint in endpoints:
                webEndpoints = endpoint.children.get(ENDPOINT_CHILDREN_WEBENDPOINT_KEY)
                if webEndpoints:
                    for webEndpoint in webEndpoints.itervalues():
                        yield webEndpoint, endpoint

    def addService(self, service):
        """Add a service
        """
        hasWebEndpoint = False
        for webEndpoint, endpoint in self.getWebEndpointsFromService(service):
            hasWebEndpoint = True
            # Add this web endpoint
            if webEndpoint.id in self.endpoints:
                raise ValueError('Web endpoint id [%s] duplicated' % webEndpoint.id)
            self.endpoints[webEndpoint.id] = (webEndpoint, endpoint)
            # Add url rule
            if not self.urlMapper:
                self.urlMapper = Map([ webEndpoint.getUrlRule() ])
            else:
                self.urlMapper.add(webEndpoint.getUrlRule())
        # Boot up service
        if hasWebEndpoint:
            service.bootup(self)

    def removeService(self, service):
        """Remove a service
        """
        if not isinstance(service, (tuple, list)):
            service = (service, )
        # Removed services
        removedServices = []
        for srv in service:
            # Remove endpoints
            hasWebEndpoint = False
            for webEndpoint, endpoint in self.getWebEndpointsFromService(srv):
                hasWebEndpoint = True
                if webEndpoint.id in self.endpoints:
                    del self.endpoints[webEndpoint.id]
            if hasWebEndpoint:
                removedServices.append(srv)
        # Rebuild url rules
        urlRules = []
        for webEndpoint, endpoint in self.endpoints.itervalues():
            urlRules.append(webEndpoint.getUrlRule())
        self.urlMapper = Map(urlRules)
        # Shutdown service
        if removedServices:
            for srv in removedServices:
                srv.shutdown(self)

    def cleanServices(self, services):
        """Clean all service
        """
        self.removeService(services)

    def startAsync(self):
        """Start asynchronously
        """
        # Generate url routing rules for the existing endpoints
        urlRules = []
        for webEndpoint, endpoint in self.endpoints.itervalues():
            urlRules.append(webEndpoint.getUrlRule())
        self.urlMapper = Map(urlRules)

    def close(self):
        """Close current adapter
        """
        self.urlMapper = None

class GeventWebAdapter(WebAdapter):
    """The gevent web adapter
    This is a gevent-bound web adapter which should be used in gevent rpc server
    """
    def __init__(self, name, host, port, **configs):
        """Create a new GeventWebAdapter
        """
        self.geventWSGIServer = None
        # Super
        super(GeventWebAdapter, self).__init__(name, host, port, **configs)

    @property
    def started(self):
        """Tell if this adapter is started or not
        """
        return not self.geventWSGIServer is None

    def startAsync(self):
        """Start asynchronously
        """
        # Super
        super(GeventWebAdapter, self).startAsync()
        # Start gevent wsgi server
        # Get logger
        serverLogger = logging.getLogger('unifiedrpc.adapter.web.gevent')
        geventWSGIServer = pywsgi.WSGIServer(
            (self.host, self.port),
            self,       # The application callable object
            log = GeventLogAdapter(serverLogger, logging.INFO),
            error_log = GeventLogAdapter(serverLogger, logging.ERROR)
            )
        geventWSGIServer.start()
        # Good, started
        self.geventWSGIServer = geventWSGIServer
        # Log it
        self.logger.info('Gevent WSGI server starts service at %s:%d', self.host, self.port)

    def close(self):
        """Close current adapter
        """
        if not self.geventWSGIServer:
            raise ValueError('Adapter hasn\'t started')
        self.geventWSGIServer.close()
        self.geventWSGIServer = None
        # Super
        super(GeventWebAdapter, self).close()

class GeventLogAdapter(pywsgi.LoggingLogAdapter):
    """The gevent log adapter
    """
    def write(self, msg):
        """Write the message
        """
        super(GeventLogAdapter, self).write(msg.strip())

