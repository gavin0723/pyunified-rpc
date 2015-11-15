# encoding=utf8

""" The rabbitmq adapter
    Author: lipixun
    Created Time : Sat 14 Nov 2015 06:39:31 PM CST

    File Name: adapter.py
    Description:

        We have two endpoints basicly:

            - Subscribe endpoint

                The subscribe endpoint is used to consuming messages from queues.
                The endpoint method always have four parameters:
                    - routingKey        The routingKey
                    - data              The decoded data
                    - message           The raw message object
                    - publish           The publish method (Used to publish message), actually the RabbitMQAdapter.publish method
                    - ack               The ack method (Used to acknowledge the message), actually the RabbitMQAdapter.ack method

            - RPC endpoint

                Not implemented

        NOTE:

            You have to declare everything you need in the bootup method of the service class, and be sure the declaration is synchronous (nowait = Fase),
            since the framework will consume the queues after bootup and the queues must be existed at that time.

            And also the bootup method of service class should return a channel object (Will be used when consuming queues), if None is returned, a channel
            will be created automaticaly (This is not recommended)

"""

import logging
import traceback

from haigha.message import Message

from unifiedrpc.adapters import Adapter
from unifiedrpc.protocol import Context, Request, Response, Dispatch
from unifiedrpc.protocol.request import RequestContent
from unifiedrpc.errors import *
from unifiedrpc.definition import CONFIG_REQUEST_ENCODING

from .client import GeventRabbitMQClient
from .endpoint import SubscribeEndpoint, AnonymousSubscribeEndpoint
from .request import RabbitMQSubscriptionRequest
from .definition import ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY, DEFAULT_PUBLISH_CONTENT_TYPE_KEY, DEFAULT_PUBLISH_CONTENT_ENCODING_KEY
from .errors import NotStartedError

class RabbitMQAdapter(Adapter):
    """The rabbitmq adapter
    """
    type = 'rabbitmq'
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq')

    def __init__(self, name, **configs):
        """Create a new RabbitMQAdapter
        """
        self.client = None
        self.onRequestCallback = None
        self.srvEndpoints = None
        self.consumers = None
        # Super
        super(RabbitMQAdapter, self).__init__(name, **configs)

    def onMessageReceived(self, consumer, message):
        """On message received
        """
        if not self.onRequestCallback:
            raise ValueError('Require request callback')
        # Invoke request callback
        return self.onRequestCallback((consumer, message), self)

    def parseRequest(self, incoming, context):
        """Parse the request, set the context
        """
        consumer, message = incoming
        # Get raw request
        rawRequest = consumer.parseRequest(message)
        # Generate the request
        # TODO: Resolve headers etc.. from raw request
        request = Request(headers = rawRequest.headers, content = rawRequest.content, raw = rawRequest)
        # Set context
        context.request = request

    def initResponse(self, incoming, context):
        """Initialize the response
        """
        consumer, message = incoming
        # Done
        return consumer.initResponse(message, context)

    def dispatch(self, context):
        """Dispatch the request
        """
        consumer, message = context.request.raw.consumer, context.request.raw.message
        # Create the dispatch object
        params = consumer.resolveParameters(message, context)
        context.dispatch = Dispatch(consumer.endpoint, params, consumer = consumer)

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
        self.logger.error('An error occurred\nError: %s\ntraceback: %s\n', error, traceback)

    def onRabbitMQConnected(self):
        """On rabbitmq connected
        """
        consumers = []
        # Initialize all rabbitmq service
        for service, endpoints in self.srvEndpoints:
            # Check out the endpoints
            channel = None
            for endpoint in endpoints:
                # Get the subscription endpoints
                subEndpoints = endpoint.children.get(ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY)
                if subEndpoints:
                    # Good, found subscription endpoint, check out the channel
                    if not channel:
                        channel = service.bootup(self)
                        if not channel:
                            # Channel not found
                            self.logger.warn('Channel not created by service [%s] when booting up, will create a new one', service)
                            channel = self.client.connection.channel()
                    # Create consumers
                    for endpointID, subEndpoint in subEndpoints.iteritems():
                        if isinstance(subEndpoint, SubscribeEndpoint):
                            consumer = RabbitMQSubscriptionConsumer(self, channel, endpoint, subEndpoint)
                        elif isinstance(subEndpoint, AnonymousSubscribeEndpoint):
                            consumer = RabbitMQAnnonymousSubscriptionConsumer(self, channel, endpoint, subEndpoint)
                        else:
                            raise ValueError('Unknown endpoint type [%s]' % type(subEndpoint).__name__)
                        consumers.append(consumer)
        # Done
        self.consumers = consumers

    def publish(self, routingKey, exchange, body, durable = False, contentType = None, encoding = None):
        """Publish messages
        """
        if not self.client:
            raise NotStartedError
        # Get properties
        properties = {}
        contentType = contentType or self.configs.get(DEFAULT_PUBLISH_CONTENT_TYPE_KEY)
        encoding = encoding or self.configs.get(DEFAULT_PUBLISH_CONTENT_ENCODING_KEY)
        if contentType:
            properties['content_type'] = contentType
        if encoding:
            properties['content_encoding'] = encoding
        # Create message
        message = Message(body, **properties)
        # Publish it
        return self.client.publish(message, exchange, routingKey)

    def ack(self, message):
        """Ack the message
        """
        channel = message.delivery_info['channel']
        tag = message.delivery_info.get('delivery_tag')
        if tag:
            channel.basic.ack(tag)

    def startAsync(self, onRequestCallback, onErrorCallback, srvEndpoints):
        """Start asynchronously
        """
        # Set
        self.onRequestCallback = onRequestCallback
        self.srvEndpoints = srvEndpoints
        # Create client
        self.client = self.getRabbitMQClient()

    def getRabbitMQClient(self):
        """Get a new rabbitmq client
        """
        raise NotImplementedError

    def close(self):
        """Close current adapter
        """
        self.client.close()
        self.srvEndpoints = None
        self.client = None
        self.consumers = None

class GeventRabbitMQAdapter(RabbitMQAdapter):
    """The gevent rabbitmq adapter
    """
    def getRabbitMQClient(self):
        """Get a new rabbitmq client
        """
        # Get arguments
        host, port, user, password, vhost = \
            self.configs.get('host'), \
            self.configs.get('port'), \
            self.configs.get('user'), \
            self.configs.get('password'), \
            self.configs.get('vhost')
        if not host:
            raise ValueError('Require rabbitmq host')
        if not port:
            raise ValueError('Require rabbitmq port')
        params = { 'host': host, 'port': port, 'onConnected': self.onRabbitMQConnected }
        if user:
            params['user'] = user
        if password:
            params['password'] = password
        if vhost:
            params['vhost'] = vhost
        # Create the gevent rabbitmq client
        return GeventRabbitMQClient(**params)

class RabbitMQConsumer(object):
    """The rabbit consumer
    """
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.consumer')

    def __init__(self, adapter, channel, endpoint):
        """Create a new RabbitMQConsumer
        """
        self.adapter = adapter
        self.channel = channel
        self.endpoint = endpoint

    def parseRequest(self, message):
        """Get the request object
        """
        raise NotImplementedError

    def initResponse(self, message, context):
        """Initialize the response
        """
        raise NotImplementedError

    def resolveParameters(self, message, context):
        """Resolve parameters from message and context
        """
        raise NotImplementedError

class RabbitMQSubscriptionConsumer(RabbitMQConsumer):
    """A rabbitmq consumer
    """
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.consumer.subscription')

    def __init__(self, adapter, channel, endpoint, subscribeEndpoint):
        """Create a new RabbitMQConsumer
        """
        # Super
        super(RabbitMQSubscriptionConsumer, self).__init__(adapter, channel, endpoint)
        self.subscribeEndpoint = subscribeEndpoint
        # Start
        self.startAsync()

    def __call__(self, message):
        """The consuming method
        """
        self.adapter.onMessageReceived(self, message)

    def startAsync(self):
        """Start asynchronously
        """
        for queue in self.subscribeEndpoint.queues:
            self.channel.basic.consume(queue, self, no_ack = not self.subscribeEndpoint.ack)
            self.logger.info('Consume queue [%s]', queue)

    def parseRequest(self, message):
        """Get the request object
        """
        return RabbitMQSubscriptionRequest(self, message)

    def initResponse(self, message, context):
        """Initialize the response
        """
        context.response = Response()

    def resolveParameters(self, message, context):
        """Resolve parameters from message and context
        """
        return {
            'routingKey': message.delivery_info['routing_key'],
            'data': None,
            'message': message,
            'publish': self.adapter.publish,
            'ack': self.adapter.ack
            }

class RabbitMQAnnonymousSubscriptionConsumer(RabbitMQSubscriptionConsumer):
    """The rabbitmq annonymous subscription consumer
    """
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.consumer.subscription.annonymous')

    def startAsync(self):
        """Start asynchronously
        """
        self.channel.queue.declare(auto_delete = True, cb = self.onQueueDeclared)

    def onQueueDeclared(self, queue, msgCount, consumerCount):
        """On annoymous queue declared
        """
        self.logger.info('Annonymous queue [%s] declared', queue)
        # Bind
        for exchange, routingKey in self.subscribeEndpoint.bindings:
            self.channel.queue.bind(queue, exchange, routingKey)
        # Consume
        self.channel.basic.consume(queue, self, no_ack = not self.subscribeEndpoint.ack)
        self.logger.info('Consume queue [%s]', queue)

