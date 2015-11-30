# encoding=utf8
# The unified RPC server

"""The unified RPC server

Known configs:

    request.encoding                    The default request charset, utf8 by default
    response.encoding                   The default response charset, utf8 by default
    response.mimeType                   The default response mimetype, None by default

"""

import logging
import threading
import traceback

from protocol import Context, Request, Response
from discover import ServiceEndpointDiscover
from content.parser.aggregate import AggregateContentParser
from content.builder.automatic import AutomaticContentBuilder
from content.container.plain import PlainContentContainer

from definition import *
from errors import *

class Server(object):
    """The unified RPC server
    """
    logger = logging.getLogger('unifiedrpc.server')

    DEFAULT_REQUEST_ENCODING        = 'utf-8'
    DEFAULT_RESPONSE_MIMETYPE       = 'text/plain'
    DEFAULT_RESPONSE_ENCODING       = 'utf-8'

    EVENT_CLASS                     = threading.Event

    CONTENT_CONTAINER_CLASS         = PlainContentContainer

    def __init__(self, adapters = None, services = None, contentParser = None, contentBuilder = None, **configs):
        """Create a new Server
        """
        self.adapters = {}
        self.services = {}
        # Add adapters
        if adapters:
            for adapter in adapters:
                self.addAdapter(adapter)
        # Add services
        if services:
            for service in services:
                self.addService(service)
        # Set the content parser and builder
        self.contentParser = contentParser or AggregateContentParser.default()
        self.contentBuilder = contentBuilder or AutomaticContentBuilder.default()
        # Set the config
        self.configs = configs
        # Set the closed event
        self.closedEvent = self.EVENT_CLASS()

    def onRequest(self, incoming, adapter):
        """On a request incoming
        Parameters:
            incoming                            The incoming request, any kind of object
            adapter                             The adapter to handle this request
        Returns:
            The context object
        """
        # Clean and create new context
        Context.cleanCurrent()
        context = Context(server = self, adapter = adapter)
        # Start processing
        try:
            try:
                # Prepare the context
                self.prepareContext(context, incoming)
            except:
                # Here, we're trying to safe init the response in order to let the whole framework correctly generate the error response
                self.safeInitResponse(context)
                # Re-raise the exception
                raise
            # Set the context
            Context.setCurrent(context)
            # Parse the request content stream if have one
            if context.request.content and context.request.content.mimeType:
                context.request.content.data = self.contentParser.parse(context)
            # Invoke the endpoint
            value = self.executeEndpoint(context)
            context.response.container.setValue(value)
        except Exception as error:
            # The very common error handling
            self.onRequestError(error, traceback.format_exc(), incoming, adapter, context)
        finally:
            self.contentBuilder.build(context)
            # Return the context
            return context

    def onError(self, error, adapter, tbString = None, message = None):
        """On error callback
        Parameters:
            error                               The error object
            adapter                             The adapter
            tbString                            The traceback message
            message                             The additional message
                                                NOTE:
                                                    This parameter may not be a string but a dict or other data type
        Returns:
            Nothing
        NOTE:
            This method MUST NEVER raise any exception
        """
        # Log it
        self.logger.error('Error occurred with adapter [%s@%s@%s]: %s\n%s\nMessage:%s',
            adapter.name,
            adapter.type,
            type(adapter).__name__,
            error,
            tbString or '',
            message or ''
            )

    def prepareContext(self, context, incoming):
        """Prepare the context
        Parameters:
            incoming                            The incoming request, any kind of object
        Returns:
            Context object
        """
        # Parse the request
        self.parseRequest(incoming, context)
        # Dispatch
        self.dispatch(context)
        # Initialize the response
        self.initResponse(incoming, context)

    def parseRequest(self, incoming, context):
        """Parse the request
        Parameters:
            incoming                            The incoming request, any kind of object
            context                             The Context object
        Returns:
            Nothing
        """
        # Call the adapter to parse the request
        return context.adapter.parseRequest(incoming, context)

    def initResponse(self, incoming, context):
        """Initialize the response
        Parameters:
            adapter                             The adapter to handle this request
            context                             The Context object
        Returns:
            Nothing
        """
        # Call the adapter to initialize the response
        context.adapter.initResponse(incoming, context)
        # Get the response mime type
        if not context.response.mimeType:
            context.response.mimeType = self.getResponseMimeType(context)
        # Get the response encoding
        if not context.response.encoding:
            context.response.encoding = self.getResponseEncoding(context)
        # Get the response container
        if not context.response.container:
            context.response.container = self.getResponseContainer(context)

    def safeInitResponse(self, context):
        """Safely initialize the response
        Parameters:
            context                             The Context object
        Returns:
            Nothing
        NOTE:
            This method will NEVER raise any exception and the initialization should be successful all the time
        """
        try:
            mimeType = self.getResponseMimeType(context)
        except:
            mimeType = self.DEFAULT_RESPONSE_MIMETYPE
        try:
            encoding = self.getResponseEncoding(context)
        except:
            encoding = self.DEFAULT_RESPONSE_ENCODING
        try:
            container = self.getResponseContainer(context)
        except:
            container = self.CONTENT_CONTAINER_CLASS()
        # Set them
        if not context.response:
            # Create the whole response
            context.response = Response(mimeType = mimeType, encoding = encoding, container = container)
        else:
            if not context.response.mimeType:
                context.response.mimeType = mimeType
            if not context.response.encoding:
                context.response.encoding = encoding
            if not context.response.container:
                context.response.container = container

    def getResponseMimeType(self, context):
        """Get the response mimeType
        """
        # Get the raw mime type(s)
        rawMimeType = None
        if context.dispatch and context.dispatch.endpoint:
            rawMimeType = context.dispatch.endpoint.configs.get(CONFIG_RESPONSE_MIMETYPE)
        if not rawMimeType:
            rawMimeType = context.adapter.configs.get(CONFIG_RESPONSE_MIMETYPE)
            if not rawMimeType:
                rawMimeType = self.configs.get(CONFIG_RESPONSE_MIMETYPE)
        # Get the allowed mime types array from raw mime type(s)
        if isinstance(rawMimeType, basestring):
            allowedMimeTypes = [ rawMimeType.lower() ]
        elif isinstance(rawMimeType, (tuple, list)):
            allowedMimeTypes = [ x.lower() for x in rawMimeType ]
        else:
            allowedMimeTypes = None
        # NOTE:
        #   Pay attention to the value of allowedMimeTypes:
        #       - None means no limitation, in this case the server will prefer to choose the one which server supported
        #       - [] means donot allowed any mime types. If this value has been set, the server will return as DEFAULT_RESPONSE_MIMETYPE regardless of
        #         accept of request
        mimeType = None
        # Check the accepted mime types
        if isinstance(allowedMimeTypes, (tuple, list)) and len(allowedMimeTypes) == 0:
            # Use the default one
            mimeType = self.DEFAULT_RESPONSE_MIMETYPE
        else:
            if context.request.accept and context.request.accept.mimeTypes:
                # Select the first allowed accept mime types
                for acceptValue in context.request.accept.mimeTypes:
                    acceptMimeType = acceptValue.value.lower().strip()
                    if acceptMimeType == '*/*':
                        # Use the first accept content type the server supported
                        if not allowedMimeTypes or self.DEFAULT_RESPONSE_MIMETYPE in allowedMimeTypes:
                            mimeType = self.DEFAULT_RESPONSE_MIMETYPE
                        else:
                            mimeType = allowedMimeTypes[0]
                        break
                    elif self.contentBuilder.isSupportMimeType(acceptMimeType):
                        mimeType = acceptMimeType
                        break
                if not mimeType:
                    raise NotAcceptableError
            else:
                # Select the first allowed mime types
                if not allowedMimeTypes or self.DEFAULT_RESPONSE_MIMETYPE in allowedMimeTypes:
                    mimeType = self.DEFAULT_RESPONSE_MIMETYPE
                else:
                    mimeType = allowedMimeTypes[0]
        # Done
        return mimeType

    def getResponseEncoding(self, context):
        """Get the response encoding
        """
        # How to choose the encoding:
        #   - If header accept-encoding is set, will use this value
        #   - If header accept-charset is set, will use this value
        #   - Otherwise will use the encoding defined in endpoint / adapter / server / server default
        if context.request.accept and context.request.accept.encodings:
            encoding = context.request.accept.encodings[0].value.lower()
        elif context.request.accept and context.request.accept.charsets:
            encoding = context.request.accept.charsets[0].value.lower()
        else:
            encoding = None
            if context.dispatch and context.dispatch.endpoint:
                encoding = context.dispatch.endpoint.configs.get(CONFIG_RESPONSE_ENCODING)
            if not encoding:
                encoding = context.adapter.configs.get(CONFIG_RESPONSE_ENCODING)
                if not encoding:
                    encoding = self.configs.get(CONFIG_RESPONSE_ENCODING, self.DEFAULT_RESPONSE_ENCODING)
        # Done
        return encoding

    def getResponseContainer(self, context):
        """Get the response container
        """
        containerClass = None
        if context.dispatch and context.dispatch.endpoint:
            containerClass = context.dispatch.endpoint.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
        if not containerClass:
            containerClass = context.adapter.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
            if not containerClass:
                containerClass = self.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
                if not containerClass:
                    containerClass = self.CONTENT_CONTAINER_CLASS
        # Done
        return containerClass()

    def dispatch(self, context):
        """Dispatch the request
        Parameters:
            adapter                             The adapter to handle this request
            context                             The Context object
        Returns:
            Nothing
        """
        # Call the adapter to dispatch the request
        return context.adapter.dispatch(context)

    def executeEndpoint(self, context):
        """Execute the endpoint
        Parameters:
            context                             The Context object
        Returns:
            The returned value
        """
        return context.dispatch.endpoint.pipeline(context)

    def onRequestError(self, error, tbString, incoming, adapter, context):
        """On a process error
        This method should handle the error (Such as print log, send error event, generate error response) and
        set context object properly
        Parameters:
            error                               The exception object
            tbString                            The traceback message
            incoming                            The incoming object
            adapter                             The adapter object
            context                             The Context object
        Returns:
            Nothing
        NOTE:
            This method MUST NOT raise any exceptions
        """
        try:
            # Set the error meta data
            if isinstance(error, RPCError):
                if not error.code is None or error.reason or error.detail:
                    context.response.container.setError(error.code, error.reason, error.detail)
                # Check if it is a internal server error, thus should call on error
                if isinstance(error, InternalServerError):
                    self.onError(error, adapter, tbString)
            else:
                # An unexpected error, set as internal server error and call on error
                context.response.container.setError(ERRCODE_UNDEFINED, 'Internal Server Error')
                self.onError(error, adapter, tbString)
            # Handle the error
            return adapter.handleError(error, tbString, incoming, context)
        except Exception as innerError:
            # Report the error
            self.onError(innerError, adapter, traceback.format_exc(), message = {
                'reason': 'Failed',
                'error': error,
                'traceback': tbString,
                })

    def addService(self, service):
        """Add a service
        NOTE:
            All services should be added before start the server
        """
        if service.name in self.services:
            raise ValueError('Service name [%s] duplicated' % service.name)
        self.services[service.name] = service

    def addServices(self, services):
        """Add services
        """
        for service in services:
            self.addService(service)

    def removeService(self, name):
        """Remove a service
        NOTE:
            Remove service after started the service will not take effect
        """
        if name in self.services:
            del self.services[name]

    def cleanServices(self):
        """Clean the services
        NOTE:
            Clean service after started the service will not take effect
        """
        self.services = {}

    def addAdapter(self, adapter):
        """Add a adapter
        NOTE:
            All adapters should be added before start the server
        """
        if adapter.name in self.adapters:
            raise ValueError('Adapter name [%s] duplicated' % adapter.name)
        self.adapters[adapter.name] = adapter

    def removeAdapter(self, name):
        """Remove a adapter
        NOTE:
            Remove adapters after started the service will not take effect
        """
        if name in self.adapters:
            del self.adapters[name]

    def cleanAdapters(self):
        """Clean the adapters
        NOTE:
            Clean adapters after started the service will not take effect
        """
        self.adapters = {}

    def startAsync(self):
        """Start the server asynchronously
        """
        # Discover endpoints
        srvEndpoints = []       # A list of tuple(service, endpoints)
        for service in self.services.itervalues():
            endpoints = service.getEndpoints()
            if endpoints:
                srvEndpoints.append((service, endpoints))
        # Run it
        for adapter in self.adapters.itervalues():
            adapter.startAsync(self.onRequest, self.onError, srvEndpoints)

    def start(self):
        """Start the server
        """
        self.startAsync()
        # Wait forever
        self.closedEvent.clear()
        self.closedEvent.wait()

    def close(self):
        """Close the server
        """
        for adapter in self.adapters.itervalues():
            adapter.close()
        self.closedEvent.set()

class GeventServer(Server):
    """The GeventServer
    """
    @property
    def EVENT_CLASS(self):
        """Get the event class
        """
        from gevent.event import Event
        return Event
