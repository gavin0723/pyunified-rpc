# encoding=utf8

""" Rabbitmq client
    Author: lipixun
    Created Time : Sat 14 Nov 2015 07:37:24 PM CST

    File Name: __init__.py
    Description:

        A rabbitmq client based on haigha which provides the following features:

            - Auto re-connection (With auto re-declaration)
            - Standalone publish channel and publish interface

"""

import logging
import time

from haigha.connections.rabbit_connection import RabbitConnection
from haigha.message import Message

class RabbitMQClient(object):
    """The rabbitmq client
    """
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.client')

    def __init__(self, host, port, transport = None, user = None, password = None, vhost = '/', connectTimeout = None, heartbeat = None, onConnected = None, onDisconnected = None, onClosed = None):
        """Create a new RabbitMQClient
        NOTE:
            The difference between onDisconnected and onClosed:
                - onDisconnected        When the connection is disconnected unexpectedly
                - onClosed              When the connection is disconnected expectedly
        """
        self.host = host
        self.port = port
        self.transport = transport
        self.user = user
        self.password = password
        self.vhost = vhost
        self.connectTimeout = connectTimeout
        self.onConnectedCallback = onConnected
        self.onDisconnectedCalback = onDisconnected
        self.onClosedCallback = onClosed
        self._closing = False
        # Create the connection
        self.connection = self.getConnection()
        self.pubChannel = None

    def dispatch(self, method, *args, **kwargs):
        """Dispatch a new method
        """
        raise NotImplementedError

    def getConnection(self):
        """Get a connection
        """
        return RabbitConnection(
            host = self.host,
            port = self.port,
            vhost = self.vhost,
            user = self.user,
            password = self.password,
            transport = self.transport,
            connect_timeout = self.connectTimeout,
            open_cb = self.onConnected,
            close_cb = self.onClosed
            )

    def close(self):
        """Close this client
        """
        if not self._closing:
            # Close
            self._closing = True
            self.connection.close()

    def onConnected(self):
        """On connection connected
        """
        self.logger.info('Connected to [%s:%s]', self.host, self.port)
        # Declare the channel
        self.pubChannel = self.connection.channel()
        # Invoke the connected callback
        try:
            if self.onConnectedCallback:
                self.onConnectedCallback()
        except:
            self.logger.exception('An error occurred when invoking connected callback')

    def onClosed(self):
        """On connection closed
        """
        # Set states
        self.connection = None
        self.pubChannel = None
        # Handle the disconnection event
        if self._closing:
            # A expected closed
            self.logger.info('Closed')
            try:
                if self.onClosedCallback:
                    self.onClosedCallback()
            except:
                self.logger.exception('An error occurred when invoking closed callback')
        else:
            # An unexpected closed
            self.logger.warn('Unexpectedly disconnected, will re-connect in 5s')
            # Dispatch reconnect method
            self.dispatch(self.reconnect)
            try:
                if self.onDisconnectedCalback:
                    self.onDisconnectedCalback()
            except:
                self.logger.exception('An error occurred when invoking disconnected callback')

    def reconnect(self):
        """The auto re-connect method, should not be used directly by user / developer
        """
        # Sleep for 5s before create new connection
        while True:
            time.sleep(5)
            try:
                self.connection = self.getConnection()
                break
            except:
                self.logger.exception('An error occurred when re-connect, will re-connect in 5s')

    def publish(self, msg, exchange, routingKey, mandatory = False, immediate = False, ticket = None):
        """Publish a message
        """
        if not self.pubChannel:
            raise NotConnectedError
        # Publish
        return self.pubChannel.publish(msg, exchange, routingKey, mandatory, immediate, ticket)

class GeventRabbitMQClient(RabbitMQClient):
    """The gevent rabbitmq client
    """
    def __init__(self, host, port, user = None, password = None, vhost = '/', connectTimeout = None, heartbeat = None, onConnected = None, onDisconnected = None, onClosed = None):
        """Create a new GeventRabbitMQClient
        """
        # Super
        super(GeventRabbitMQClient, self).__init__(host, port, 'gevent', user, password, vhost, connectTimeout, heartbeat, onConnected, onDisconnected, onClosed)

    def dispatch(self, method, *args, **kwargs):
        """Dispatch a new method
        """
        import gevent
        # Spawn
        gevent.spawn(method, *args, **kwargs)

    @classmethod
    def loop(cls, connection):
        """Loop processing the request
        """
        import gevent
        # Continue processing
        while not connection.closed:
            try:
                connection.read_frames()
                gevent.sleep()
            except:
                cls.logger.exception('An error occurred when continue processing rabbitmq message frames')

    def getConnection(self):
        """Get a connection
        """
        conn = super(GeventRabbitMQClient, self).getConnection()
        import gevent
        gevent.spawn(self.loop, conn)
        # Done
        return conn

class NotConnectedError(Exception):
    """Not connected error
    """
