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

from werkzeug.routing import Map
from werkzeug.wrappers import Response as WKResponse
from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed

from unifiedrpc.errors import *
from unifiedrpc.adapters import Adapter
from unifiedrpc.protocol import Service
from unifiedrpc.definition import CONFIG_REQUEST_ENCODING, CONFIG_REQUEST_CONTENT_PARSER, CONFIG_SESSION_MANAGER, \
    CONFIG_RESPONSE_CONTENT_CONTAINER, CONFIG_RESPONSE_CONTENT_BUILDER
from unifiedrpc.protocol.context import context, Context, setContext, clearContext

from util import getContentType
from errors import ERROR_BINDINGS
from request import WebRequest
from response import WebResponse
from dispatch import WebDispatchResult
from definition import ENDPOINT_CHILDREN_WEBENDPOINT_KEY, STARTUP_SHUTDOWN_HANDLER_NAME

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

    DEFAULT_REQUEST_ENCODING    = 'utf8'

    def __init__(self, host = '0.0.0.0', port = 8080, configs = None, stage = None):
        """Create a new WebAdapter
        Parameters:
            host                        The bind host
            port                        The bind port
            configs                     The adapter configs
            stage                       The execution stage
        """
        # Check parameters
        if not isinstance(host, basestring):
            raise TypeError('Invalid parameter host, require string type actually got [%s]' % type(host).__name__)
        if not isinstance(port, int):
            raise TypeError('Invalid parameter port, require int type actually got [%s]' % type(port).__name__)
        # Set basic attributes
        self._host = host
        self._port = port
        self._urlMapper = None       # A werkzeug.routing.Map object
        # Super
        super(WebAdapter, self).__init__(configs, stage)
        # Add handlers
        self._stage.addPreRequest(self._onExecutionPreRequest, 10000)
        self._stage.addErrorHandler(self._onExecutionError)

    def __start__(self):
        """Start
        """
        urlRules = []
        # Start services and build up the url rules
        for service in self._server.services:
            hasWebEndpoint = False
            # Get endpoints
            for endpoint in service.endpoints.itervalues():
                # Get web endpoints
                webs = endpoint.children.get(ENDPOINT_CHILDREN_WEBENDPOINT_KEY)
                if webs:
                    # Good
                    for webEndpoint in webs:
                        urlRules.append(webEndpoint.getUrlRule(endpoint))
                    # Set flag
                    hasWebEndpoint = True
            # Start the service
            if hasWebEndpoint:
                self.logger.debug('Start up the service [%s] for web', service.name)
                handler = service.startups.get(STARTUP_SHUTDOWN_HANDLER_NAME)
                if handler:
                    handler(service, self)
        # Set the map
        self._urlMapper = Map(urlRules)

    def __stop__(self):
        """Close current adapter
        """
        self._urlMapper = None
        # Start services and build up the url rules
        for service in self._server.services:
            hasWebEndpoint = False
            # Get endpoints
            for endpoint in service.endpoints.itervalues():
                # Get web endpoints
                webs = endpoint.children.get(ENDPOINT_CHILDREN_WEBENDPOINT_KEY)
                if webs:
                    hasWebEndpoint = True
                    break
            # Start the service
            if hasWebEndpoint:
                self.logger.debug('Shut down the service [%s] for web', service.name)
                handler = service.shutdowns.get(STARTUP_SHUTDOWN_HANDLER_NAME)
                if handler:
                    handler(service, self)

    def __call__(self, environ, startResponse):
        """The WSGI entry
        Parameters:
            environ                     The environment
            startResponse               The callback method to start response
        Returns:
            Yield or list of string for http response content
        """
        setContext(Context(server = self._server, adapter = self))
        try:
            endpointExecutionContext = None
            # The normal http processing
            execution = context.execution()
            # Parse the request
            context.request = self.REQUEST_CLASS(environ)
            if context.request.content and context.request.content.mimeType:
                # Get the default encoding if not specified
                if not context.request.content.encoding:
                    context.request.content.encoding = execution.getConfig(CONFIG_REQUEST_ENCODING, self.DEFAULT_REQUEST_ENCODING)
                # Parse the content data
                context.request.content.data = execution.getConfig(CONFIG_REQUEST_CONTENT_PARSER).parse(context)
            # Get session
            sessionManager = execution.getConfig(CONFIG_SESSION_MANAGER)
            if sessionManager:
                context.session = sessionManager.get(context.request)
            # Dispatch, find the service and endpoint
            webEndpoint, endpoint, urlParams = self.dispatch(context.request)
            if webEndpoint:
                # Found the endpoint
                # Create the params
                params = {}
                if urlParams:
                    params.update(urlParams)
                if context.request.params:
                    params.update(context.request.params)
                # Set the result
                context.dispatchResult = WebDispatchResult(
                    webEndpoint,
                    endpoint,
                    params,
                    endpoint.bound if isinstance(endpoint.bound, Service) else None,
                    )
                # Update the execution
                execution = context.execution()
            # Generate the response
            context.response = self.RESPONSE_CLASS()
            # Call the execution
            endpointExecutionContext = execution.getEndpointExecutionContext()
            endpointExecutionContext()
            # Complete the response
            if not context.response.content.container:
                context.response.content.container = context.response.getContentContainer(context.request, context.response, execution)
            if not context.response.content.builder:
                context.response.content.builder = context.response.getContentBuilder(context.request, context.response, execution)
            if not context.response.encoding:
                context.response.encoding = context.response.getEncoding(context.request, context.response, execution)
            if not context.response.mimeType:
                context.response.mimeType = context.response.getMimeType(context.request, context.response, execution)
            # Set session
            if sessionManager:
                sessionManager.set(context.session, context.response)
            # Create the container and builder
            container = context.response.content.container()
            if context.response.content.executionResult:
                container.setValue(context.response.content.executionResult)
            if context.response.content.error:
                container.setRPCError(context.response.content.error)
            # Dump the container and set headers
            containerValues, containerHeaders = container.dump()
            if containerHeaders:
                context.response.headers.update(containerHeaders)
            # Create the response
            responseValue = context.response.content.builder.build(context.response, containerValues)
            response = WKResponse(
                status = context.response.status,
                headers = context.response.headers,
                response = responseValue,
                content_type =  getContentType(context.response.mimeType, context.response.encoding)
                )
            # Send header and body
            for _v in response(environ, startResponse):
                yield _v
        except Exception as error:
            # Error happened
            if not type(error) in ERROR_BINDINGS:
                # Log the error with details
                self.logger.exception('Failed to handle http request')
                # Create a internal server error
                status = 500
                error = InternalServerError(ERRCODE_UNDEFINED, reason = 'Undefined error occurred')
            elif isinstance(error, HTTPException):
                # The http exception
                status = error.code
                self.logger.error(str(error))
            else:
                # A http error
                status = ERROR_BINDINGS[type(error)]
                self.logger.error(str(error))
            # Return error without container and builder
            response = WKResponse(status = status, response = [])
            # Send header and body
            for _v in response(environ, startResponse):
                yield _v
        finally:
            # Call the finalize
            try:
                if not endpointExecutionContext:
                    endpointExecutionContext = context.execution().getEndpointExecutionContext()
                endpointExecutionContext.finalize()
            except:
                self.logger.exception('Failed to call the finalize')
            # Clear the context
            clearContext()

    def dispatch(self, request):
        """Dispatch the request for current context
        Returns:
            WebEndpoint, Parameters
        """
        if not self._urlMapper:
            return None, None, None
        # Map the url
        try:
            urlAdapter = self._urlMapper.bind_to_environ(request.environ)
            (webEndpoint, endpoint), params = urlAdapter.match()
            # Done
            return webEndpoint, endpoint, params
        except NotFound:
            # Not found
            raise NotFoundError(ERRCODE_NOTFOUND_ENDPOINT_NOT_FOUND, reason = 'Endpoint not found')
        except MethodNotAllowed:
            # Method not allowed
            raise MethodNotAllowedError(reason = 'Method isn\'t allowed for the endpoint')

    def _onExecutionPreRequest(self):
        """On execution pre-request
        """
        # Select the
        webEndpoint, params = context.dispatchResult.webEndpoint, context.dispatchResult.parameters
        # Check it
        if webEndpoint.allowedMultiParams:
            if webEndpoint.allowedMultiParams == '*':
                # All parameters should be array
                for key in params.iterkeys():
                    value = params[key]
                    if not isinstance(value, (list, tuple)):
                        params[key] = (value, )
            elif isinstance(webEndpoint.allowedMultiParams, (list, tuple)):
                # The listed parameter should be array
                for key in params.keys():
                    value = params[key]
                    if key in webEndpoint.allowedMultiParams:
                        # Must be array
                        if not isinstance(value, (tuple, list)):
                            params[key] = (value, )
                    elif isinstance(value, (tuple, list)):
                        # Must not be array
                        if len(value) == 0:
                            del params[key]
                        elif len(value) == 1:
                            params[key] = value[0]
                        else:
                            raise BadRequestError
            else:
                # Unsupported value
                raise ValueError('Unsupported allowedMultiParams value [%s]' % webEndpoint.allowedMultiParams)
        else:
            # Unwrap all parameters out of array
            for key in params.keys():
                value = params[key]
                if isinstance(value, (tuple, list)):
                    # Must not be array
                    if len(value) == 0:
                        del params[key]
                    elif len(value) == 1:
                        params[key] = value[0]
                    else:
                        raise BadRequestError
        # Set parameters
        context.dispatchResult.parameters = params

    def _onExecutionError(self, error, handled):
        """On execution error
        """
        if not handled:
            # Set error
            if not type(error) in ERROR_BINDINGS:
                status = 500
                error = InternalServerError(ERRCODE_UNDEFINED, reason = 'Undefined error occurred')
            else:
                status = ERROR_BINDINGS[type(error)]
            context.response.status = status
            context.response.content.error = error
        # Handled
        return True

class GeventWebAdapter(WebAdapter):
    """The gevent web adapter
    This is a gevent-bound web adapter which should be used in gevent rpc server
    """
    logger = logging.getLogger('unifiedrpc.adapter.web.gevent')

    def __init__(self, *args, **kwargs):
        """Create a new GeventWebAdapter
        """
        self._geventWSGIServer = None
        # Super
        super(GeventWebAdapter, self).__init__(*args, **kwargs)

    def __start__(self):
        """Start
        """
        from gevent import pywsgi
        # Define the log adapter
        class GeventLogAdapter(pywsgi.LoggingLogAdapter):
            """The gevent log adapter
            """
            def write(self, msg):
                """Write the message
                """
                super(GeventLogAdapter, self).write(msg.strip())
        # Super
        super(GeventWebAdapter, self).__start__()
        # Start gevent wsgi server
        geventWSGIServer = pywsgi.WSGIServer(
            (self._host, self._port),
            self,       # The application callable object
            log = GeventLogAdapter(self.logger, logging.INFO),
            error_log = GeventLogAdapter(self.logger, logging.ERROR)
            )
        geventWSGIServer.start()
        # Good, started
        self._geventWSGIServer = geventWSGIServer
        # Log it
        self.logger.info('Gevent WSGI server starts service at [%s:%d]', self._host, self._port)

    def __stop__(self):
        """Close current adapter
        """
        # Super
        super(GeventWebAdapter, self).__stop__()
        # Stop
        self._geventWSGIServer.close()
        self._geventWSGIServer = None
