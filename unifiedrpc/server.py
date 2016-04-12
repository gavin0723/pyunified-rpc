# encoding=utf8
# The unified RPC server

""" The unified RPC server
    Author: lipixun
    Created Time : 四  4/ 7 16:18:23 2016

    File Name: handler.py
    Description:

"""

import logging

from threading import Lock, Event

from unifiedrpc.content.parser import default as createDefaultContentParser
from unifiedrpc.content.builder import default as createDefaultContentBuilder
from unifiedrpc.content.container import PlainContentContainer

from errors import *
from definition import *
from protocol.execution import EndpointExecutionStage

class Server(object):
    """The unified RPC server
    """
    logger = logging.getLogger('unifiedrpc.server')

    GLOCK = Lock()

    # The default values for this server
    DEFAULT_REQUEST_ENCODING        = 'utf-8'
    DEFAULT_RESPONSE_MIMETYPE       = 'text/plain'
    DEFAULT_RESPONSE_ENCODING       = 'utf-8'           # utf-8 instead of utf8 for ie compitable
    DEFAULT_CONTENT_CONTAINER       = PlainContentContainer

    def __init__(self, services, adapters, configs = None, stage = None):
        """Create a new Server
        """
        self._services = services
        self._adapters = adapters
        self._configs = configs or {}
        self._stage = stage or EndpointExecutionStage()
        # Attach the adapters
        for adapter in self._adapters:
            adapter.attach(self)
        # Initialize the flags
        self._started = False
        self._stopEvent = Event()
        # Set the defaults if missing
        if not CONFIG_REQUEST_ENCODING in self._configs:
            self._configs[CONFIG_REQUEST_ENCODING] = self.DEFAULT_REQUEST_ENCODING
        if not CONFIG_REQUEST_CONTENT_PARSER in self._configs:
            self._configs[CONFIG_REQUEST_CONTENT_PARSER] = createDefaultContentParser()
        if not CONFIG_RESPONSE_MIMETYPE in self._configs:
            self._configs[CONFIG_RESPONSE_MIMETYPE] = self.DEFAULT_RESPONSE_MIMETYPE
        if not CONFIG_RESPONSE_ENCODING in self._configs:
            self._configs[CONFIG_RESPONSE_ENCODING] = self.DEFAULT_RESPONSE_ENCODING
        if not CONFIG_RESPONSE_CONTENT_CONTAINER in self._configs:
            self._configs[CONFIG_RESPONSE_CONTENT_CONTAINER] = self.DEFAULT_CONTENT_CONTAINER
        if not CONFIG_RESPONSE_CONTENT_BUILDER in self._configs:
            self._configs[CONFIG_RESPONSE_CONTENT_BUILDER] = createDefaultContentBuilder()

    @property
    def started(self):
        """Get if the adapter is started
        """
        return self._started

    @property
    def stopEvent(self):
        """The stop event
        """
        return self._stopEvent

    @property
    def services(self):
        """Get the services
        """
        return self._services

    @property
    def adapters(self):
        """Get the adapters
        """
        return self._adapters

    def start(self):
        """Start the server
        Returns:
            Nothing
        """
        with self.GLOCK:
            # Check flag
            if self._started:
                raise ValueError('Server is already started')
            if not self._services:
                raise ValueError('Require services')
            if not self._adapters:
                raise ValueError('Require adapters')
            # Start adapters
            for adapter in self._adapters:
                adapter.start()
            # Set flags
            self._started = True
            self._stopEvent.clear()

    def stop(self):
        """Stop the server
        """
        with self.GLOCK:
            # Check flag
            if not self._started:
                raise ValueError('Server is not started')
            # Stop adapters
            for adapter in self.adapters:
                adapter.stop()
            # Set flags
            self._started = False
            self._stopEvent.set()

    def wait(self, timeout = None):
        """Wait for the server stopped
        """
        self._stopEvent.wait()

    def forever(self):
        """Start the server and run forever
        """
        # Start the server
        self.start()
        # Wait for the server stopped forever
        self.wait()

class GeventServer(Server):
    """The gevent server
    """
    @classmethod
    def waits(cls, servers, timeout = None):
        """Wait for multiple services
        """
        import gevent
        gevent.wait([ x.stopEvent for x in servers ], timeout)
