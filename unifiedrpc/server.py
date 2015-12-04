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

    def initContext(self, context):
        """Initialize the context
        """
        context.components.contentParser = self.contentParser
        context.components.contentBuilder = self.contentBuilder

    def initResponse(self, context):
        """Initialize the response
        Parameters:
            context                             The Context object
        Returns:
            Nothing
        """
        # Get the response mime type
        if not context.response.mimeType:
            context.response.mimeType = self.getResponseMimeType(context)
        # Get the response encoding
        if not context.response.encoding:
            context.response.encoding = self.getResponseEncoding(context)
        # Get the response container
        if not context.response.container:
            context.response.container = self.getResponseContainer(context)

    def getResponseMimeType(self, context):
        """Get the response mimeType
        """
        # Get the raw mime type(s)
        rawMimeType = None
        if context.dispatcher and context.dispatcher.endpoint:
            rawMimeType = context.dispatcher.endpoint.configs.get(CONFIG_RESPONSE_MIMETYPE)
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
            if context.dispatcher and context.dispatcher.endpoint:
                encoding = context.dispatcher.endpoint.configs.get(CONFIG_RESPONSE_ENCODING)
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
        if context.dispatcher and context.dispatcher.endpoint:
            containerClass = context.dispatcher.endpoint.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
        if not containerClass:
            containerClass = context.adapter.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
            if not containerClass:
                containerClass = self.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
                if not containerClass:
                    containerClass = self.CONTENT_CONTAINER_CLASS
        # Done
        return containerClass()

    def addService(self, service):
        """Add a service
        NOTE:
            All services should be added before start the server
        """
        if service.name in self.services:
            raise ValueError('Service name [%s] duplicated' % service.name)
        # Add service
        self.services[service.name] = service
        # Add service to adapters
        for adapter in self.adapters.itervalues():
            adapter.addService(service)

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
            # Remove service
            service = self.services.pop(name)
            # Remove service from adapters
            for adapter in self.adapters.itervalues():
                adapter.removeService(service)

    def cleanServices(self):
        """Clean the services
        NOTE:
            Clean service after started the service will not take effect
        """
        # Remove services
        services = self.services
        self.services = {}
        # Remove services from adapters
        for adapter in self.adapters.itervalues():
            adapter.cleanServices(services)

    def addAdapter(self, adapter):
        """Add a adapter
        NOTE:
            All adapters should be added before start the server
        """
        if adapter.name in self.adapters:
            raise ValueError('Adapter name [%s] duplicated' % adapter.name)
        # Add adapter
        adapter.server = self
        self.adapters[adapter.name] = adapter
        # Add services
        for service in self.services.itervalues():
            adapter.addService(service)

    def removeAdapter(self, name):
        """Remove a adapter
        NOTE:
            Remove adapters after started the service will not take effect
        """
        if name in self.adapters:
            # Remove adapter from adapters
            adapter = self.adapters.pop(name)
            # Shutdown adapter
            adapter.server = None
            if adapter.started:
                adapter.close()
            # Clean services
            adapter.cleanServices(self.services.values())

    def cleanAdapters(self):
        """Clean the adapters
        NOTE:
            Clean adapters after started the service will not take effect
        """
        for name in self.adapters.keys():
            # Remove it
            self.removeAdapter(name)

    def startAsync(self):
        """Start the server asynchronously
        """
        # Start all adapters
        for adapter in self.adapters.itervalues():
            adapter.startAsync()

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
