# encoding=utf8
# The unified RPC server

"""The unified RPC server

Known configs:

    request.encoding                    The default request charset, utf8 by default
    response.encoding                   The default response charset, utf8 by default
    response.mimeType                   The default response mimetype, None by default

"""

import logging

from protocol import Runtime
from unifiedrpc.content.parser.aggregate import AggregateContentParser
from unifiedrpc.content.builder.automatic import AutomaticContentBuilder
from unifiedrpc.content.container.plain import PlainContentContainer

from definition import *
from errors import *

class Server(object):
    """The unified RPC server
    """
    logger = logging.getLogger('unifiedrpc.server')

    # The default values for this server
    DEFAULT_REQUEST_ENCODING        = 'utf-8'
    DEFAULT_RESPONSE_MIMETYPE       = 'text/plain'
    DEFAULT_RESPONSE_ENCODING       = 'utf-8'
    DEFAULT_CONTENT_CONTAINER       = PlainContentContainer
    DEFAULT_CONTENT_PARSER          = AggregateContentParser
    DEFAULT_CONTENT_BUILDER         = AutomaticContentBuilder

    def __init__(self, services, **configs):
        """Create a new Server
        """
        self.services = {}
        for service in services:
            if service.name in self.services:
                raise ValueError('Conflict service [%s] found' % service.name)
            self.services[service.name] = service
        self.configs = configs
        # Set the defaults if missing
        if not CONFIG_REQUEST_ENCODING in self.configs:
            self.configs[CONFIG_REQUEST_ENCODING] = self.DEFAULT_REQUEST_ENCODING
        if not CONFIG_REQUEST_CONTENT_PARSER in self.configs:
            self.configs[CONFIG_REQUEST_CONTENT_PARSER] = self.DEFAULT_CONTENT_PARSER.default()
        if not CONFIG_RESPONSE_MIMETYPE in self.configs:
            self.configs[CONFIG_RESPONSE_MIMETYPE] = self.DEFAULT_RESPONSE_MIMETYPE
        if not CONFIG_RESPONSE_ENCODING in self.configs:
            self.configs[CONFIG_RESPONSE_ENCODING] = self.DEFAULT_RESPONSE_ENCODING
        if not CONFIG_RESPONSE_CONTENT_CONTAINER in self.configs:
            self.configs[CONFIG_RESPONSE_CONTENT_CONTAINER] = self.DEFAULT_CONTENT_CONTAINER
        if not CONFIG_RESPONSE_CONTENT_BUILDER in self.configs:
            self.configs[CONFIG_RESPONSE_CONTENT_BUILDER] = self.DEFAULT_CONTENT_BUILDER.default()

    def createRuntime(self, adapters, enabledServices = None, **_configs):
        """Create a new runtime
        """
        # Set adapters
        namedAdapters = {}
        for adapter in adapters:
            if adapter.name in namedAdapters:
                raise ValueError('Conflict adapter [%s] found' % adapter.name)
            namedAdapters[adapter.name] = adapter
        # Get enabled services
        if enabledServices:
            services = {}
            for name in enabledServices:
                if name in self.services:
                    services[name] = self.services[name]
        else:
            services = self.services
        if not services:
            raise ValueError('Require service to start')
        # Merge configs
        configs = dict(self.configs)
        configs.update(_configs)
        # Create runtime
        return Runtime(self, services, namedAdapters, **configs)

    def startAsync(self, adapters, enabledServices = None, **configs):
        """Start the server asynchronously
        Returns:
            Runtime object
        """
        runtime = self.createRuntime(adapters, enabledServices, **configs)
        runtime.startAsync()
        return runtime

    def start(self, adapters, enabledServices = None, **configs):
        """Start the server
        Returns:
            Runtime object
        """
        runtime = self.createRuntime(adapters, enabledServices, **configs)
        runtime.start()
        return runtime
