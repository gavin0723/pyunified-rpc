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
from werkzeug.wrappers import Response as WKResponse

from unifiedrpc import context, contextspace, CONFIG_SESSION_MANAGER
from unifiedrpc.adapters import Adapter
from unifiedrpc.protocol.runtime import ServiceAdapterRuntime
from unifiedrpc.errors import *
from unifiedrpc.definition import CONFIG_REQUEST_ENCODING

from definition import ENDPOINT_CHILDREN_WEBENDPOINT_KEY
from request import WebRequest
from response import WebResponse
from caller import ResponseFinalBuildCaller, ParameterValueSelectionCaller
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
        self.runtimes = {}          # A dict, key is service name, value is WebServiceAdapterRuntime
        self.urlMapper = None       # A werkzeug.routing.Map object
        self.runtime = None
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
        stage = None
        # Here, we create a context space
        with contextspace(self.runtime, self):
            try:
                stage = STAGE_BEFORE_REQUEST
                # Parse the rqequest
                context.request = self.REQUEST_CLASS(environ)
                # Parse the request content stream if have one
                if context.request.content and context.request.content.mimeType:
                    # Get the default encoding if not specified
                    if not context.request.content.encoding:
                        context.request.content.encoding = context.request.getDefinedEncoding(context)
                    # Parse the content data
                    context.request.content.data = context.components.contentParser.parse(context)
                # Get session
                if self.sessionManager:
                    context.session = self.sessionManager.get(context.request)
                # Dispatch the request
                stage = STAGE_BEFORE_DISPATCH
                endpoint, params, webEndpoint = self.dispatch()
                context.endpoint = endpoint
                context.params = params
                context.webEndpoint = webEndpoint
                # Create the response object
                stage = STAGE_BEFORE_RESPONSE
                context.response = self.RESPONSE_CLASS()
                # Invoke the endpoint
                stage = STAGE_BEFORE_HANDLER
                response = context.endpoint(context, [
                    (ResponseFinalBuildCaller(), 10000),
                    (ParameterValueSelectionCaller(), 20000),
                    ])
                return response(environ, startResponse)
                # Done
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
                    return WKResponse(
                        status = status,
                        headers = context.response.headers,
                        response = (context.response.content, ) if isinstance(context.response.content, basestring) else context.response.content,
                        content_type = getContentType(context.response.mimeType, context.response.encoding)
                        )(environ, startResponse)
                except:
                    # Failed to respond
                    self.logger.exception('Failed to respond when handling error')
                    return WKResponse(status = status)(environ, startResponse)

    def dispatch(self):
        """Dispatch the request for current context
        Returns:
            ActiveEndpoint, parameters, WebEndpoint
        """
        # Check parameters
        if not self.endpoints or not self.urlMapper:
            raise NotFoundError
        # Map the url
        try:
            urlAdapter = self.urlMapper.bind_to_environ(context.request.environ)
            webEndpointID, urlParams = urlAdapter.match()
        except NotFound:
            # Not found
            raise NotFoundError(ERRCODE_NOTFOUND_ENDPOINT_NOT_FOUND)
        # Get the endpoint
        res = self.endpoints.get(webEndpointID)
        if not res:
            raise NotFoundError(ERRCODE_NOTFOUND_ENDPOINT_NOT_FOUND)
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
        return endpoint, params, webEndpoint

    def attach(self, serviceRuntime):
        """Attach a service
        Returns:
            ServiceAdapterRuntime
        """
        # Check name
        if serviceRuntime.service.name in self.runtimes:
            raise ValueError('Conflict service [%s]' % serviceRuntime.service.name)
        # Attach this service
        for webEndpoint, endpoint in self.getEndpointsFromService(serviceRuntime.service):
            # Add this web endpoint
            if webEndpoint.id in self.endpoints:
                raise ValueError('Web endpoint id [%s] duplicated' % webEndpoint.id)
            self.endpoints[webEndpoint.id] = (webEndpoint, endpoint)
            # Add url rule
            if not self.urlMapper:
                self.urlMapper = Map([ webEndpoint.getUrlRule() ])
            else:
                self.urlMapper.add(webEndpoint.getUrlRule())
        # Create runtime and add
        runtime = WebServiceAdapterRuntime(self, serviceRuntime)
        self.runtimes[serviceRuntime.service.name] = runtime
        # Done
        return runtime

    def startAsync(self, runtime):
        """Start asynchronously
        """
        self.runtime = runtime
        # Generate url routing rules for the existing endpoints
        urlRules = []
        for webEndpoint, endpoint in self.endpoints.itervalues():
            urlRules.append(webEndpoint.getUrlRule())
        self.urlMapper = Map(urlRules)

    def shutdown(self):
        """Close current adapter
        """
        self.urlMapper = None
        self.endpoints = {}
        self.runtimes = {}

    @classmethod
    def getEndpointsFromService(cls, service):
        """Get  endpoints from service
        """
        if service.activeEndpoints:
            for endpoint in service.activeEndpoints.itervalues():
                webEndpoints = endpoint.endpoint.children.get(ENDPOINT_CHILDREN_WEBENDPOINT_KEY)
                if webEndpoints:
                    for webEndpoint in webEndpoints.itervalues():
                        yield webEndpoint, endpoint

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

    def startAsync(self, runtime):
        """Start asynchronously
        """
        if self._started:
            raise ValueError('Adapter has already started')
        # Super
        super(GeventWebAdapter, self).startAsync(runtime)
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
        self._started = True
        self._closed = False
        # Log it
        self.logger.info('Gevent WSGI server starts service at %s:%d', self.host, self.port)

    def shutdown(self):
        """Close current adapter
        """
        if not self._started:
            raise ValueError('Adapter hasn\'t started')
        self.geventWSGIServer.close()
        self.geventWSGIServer = None
        self._started = False
        self._closed = True
        # Super
        super(GeventWebAdapter, self).close()

class GeventLogAdapter(pywsgi.LoggingLogAdapter):
    """The gevent log adapter
    """
    def write(self, msg):
        """Write the message
        """
        super(GeventLogAdapter, self).write(msg.strip())

class WebServiceAdapterRuntime(ServiceAdapterRuntime):
    """Web service adapter runtime
    """
    def shutdown(self):
        """Shutdown this service adapter
        """
        # Super
        super(WebServiceAdapterRuntime, self).Shutdown()
        # Remove endpoint
        for webEndpoint, endpoint in self.adapter.getEndpointsFromService(serviceRuntime.service):
            if webEndpoint.id in self.endpoints:
                del self.endpoints[webEndpoint.id]
        # Refresh url rules
        self.urlMapper = Map([ x.getUrlRule() for (x, y) in self.endpoints.itervalues() ])
        # Remove runtime from adapter
        with Adapter.GLOCK:
            if self.serviceRuntime.service.name in self.adapter.runtimes:
                del self.adapter.runtimes[self.serviceRuntime.service.name]
