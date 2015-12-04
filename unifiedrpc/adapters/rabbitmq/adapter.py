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

from uuid import uuid4
from functools import partial

from haigha.message import Message

from unifiedrpc.adapters import Adapter
from unifiedrpc.protocol import Dispatcher, context, contextspace
from unifiedrpc.protocol.request import RequestContent
from unifiedrpc.errors import *
from unifiedrpc.definition import CONFIG_REQUEST_ENCODING

from .client import GeventRabbitMQClient
from .endpoint import SubscribeEndpoint, AnonymousSubscribeEndpoint
from .request import RabbitMQRequest
from .response import RabbitMQResponse
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
        self.services = {}      # A dict which key is service name value is MQService object
        # Super
        super(RabbitMQAdapter, self).__init__(name, **configs)

    @property
    def started(self):
        """Tell if this adapter is started or not
        """
        return self.client and self.client.isConnected

    def getSubscribeEndpointFromService(self, service):
        """Get the subscribe endpoint from service
        """
        endpoints = service.getEndpoints()
        if endpoints:
            for endpoint in endpoints:
                subEndpoints = endpoint.children.get(ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY)
                if subEndpoints:
                    for subEndpoint in subEndpoints.itervalues():
                        yield subEndpoint, endpoint

    def addService(self, service):
        """Add a service
        """
        hasEndpoint = False
        # Get subscription endpoints
        subscriptionConsumers = {}
        for subEndpoint, endpoint in self.getSubscribeEndpointFromService(service):
            hasEndpoint = True
            # Create consumer
            if isinstance(subEndpoint, SubscribeEndpoint):
                consumer = RabbitMQSubscriptionConsumer(self, endpoint, subEndpoint)
            elif isinstance(subEndpoint, AnonymousSubscribeEndpoint):
                consumer = RabbitMQAnnonymousSubscriptionConsumer(self, endpoint, subEndpoint)
            else:
                raise ValueError('Unknown endpoint type [%s]' % type(subEndpoint).__name__)
            subscriptionConsumers[subEndpoint.id] = consumer
        # Add this service
        if hasEndpoint:
            mqService = MQService(service, subscriptionConsumers)
            self.services[service.name] = mqService
            # Check if connected
            if self.started:
                self.bootupService(mqService)

    def removeService(self, service):
        """Remove a service
        """
        if service.name in self.services:
            mqService = self.services.pop(service.name)
            # Shutdown this service
            self.shutdownService(mqService)

    def cleanServices(self, services):
        """Clean all service
        """
        for service in services:
            self.removeService(service)

    def onRabbitMQConnected(self):
        """On rabbitmq connected
        """
        # Bootup all service
        for mqService in self.services.itervalues():
            self.bootupService(mqService)

    def onRabbitMQDisconnected(self):
        """On rabbitmq disconnected
        """
        # Shutdown all service
        for mqService in self.services.itervalues():
            self.shutdownService(mqService)

    def bootupService(self, mqService):
        """Boot up the mq service
        """
        channel = mqService.service.bootup(self)
        if not channel:
            # Channel not found, create a new one
            self.logger.warn('Channel not created by service [%s] when booting up, will create a new one', mqService.service.name)
            channel = self.client.connection.channel()
        # Start subscription consumers
        if mqService.subscriptionConsumers:
            for consumer in mqService.subscriptionConsumers.itervalues():
                consumer.startAsyncConsuming(channel)

    def shutdownService(self, mqService):
        """Shutdown the mq service
        """
        # Close subscription consumers
        if mqService.subscriptionConsumers:
            for consumer in mqService.subscriptionConsumers.itervalues():
                consumer.stopConsuming()
        # Close rpc consumers

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

    def startAsync(self):
        """Start asynchronously
        """
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
        self.client = None

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
        params = { 'host': host, 'port': port, 'onConnected': self.onRabbitMQConnected, 'onDisconnected': self.onRabbitMQDisconnected }
        if user:
            params['user'] = user
        if password:
            params['password'] = password
        if vhost:
            params['vhost'] = vhost
        # Create the gevent rabbitmq client
        return GeventRabbitMQClient(**params)

class MQService(object):
    """The mq service
    Attributes:
        service                                 The service object
        subscriptionConsumers                   A dict which key is subscription endpoint id, value is consumer object
    """
    def __init__(self, service, subscriptionConsumers):
        """Create a new MQService
        """
        self.service = service
        self.subscriptionConsumers = subscriptionConsumers

class RabbitMQConsumer(object):
    """The rabbit consumer
    """
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.consumer')

    def __init__(self, adapter, endpoint):
        """Create a new RabbitMQConsumer
        """
        self.adapter = adapter
        self.endpoint = endpoint
        self.channel = None

    def getDefaultRequestContentEncoding(self):
        """Get the default request content encoding
        """
        encoding = self.adapter.configs.get(CONFIG_REQUEST_ENCODING)
        if not encoding:
            encoding = context.server.configs.get(CONFIG_REQUEST_ENCODING, context.server.DEFAULT_REQUEST_ENCODING)
        return encoding

    def startAsyncConsuming(self, channel):
        """Start async consuming
        """
        if self.channel:
            raise ValueError('Consumer is already consuming')
        self.channel = channel

    def stopConsuming(self):
        """Stop consuming
        """
        self.channel = None

class RabbitMQSubscriptionConsumer(RabbitMQConsumer):
    """A rabbitmq consumer
    """
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.consumer.subscription')

    def __init__(self, adapter, endpoint, subscribeEndpoint):
        """Create a new RabbitMQConsumer
        """
        self.subscribeEndpoint = subscribeEndpoint
        self.consumerTag = str(uuid4())
        # Super
        super(RabbitMQSubscriptionConsumer, self).__init__(adapter, endpoint)

    def __call__(self, message):
        """The consuming method
        """
        # Start context
        with contextspace(self.adapter.server, self.adapter):
            # Initialize the context
            try:
                # Init context
                self.adapter.server.initContext(context)
                # Parse request
                context.request = RabbitMQRequest(self, message)
                if context.request.content and context.request.content.mimeType:
                    if not context.request.content.encoding:
                        context.request.content.encoding = self.getDefaultRequestContentEncoding()
                    context.request.content.data = context.components.contentParser.parse(context)
                # Get the parameters
                params = {
                    'routingKey': message.delivery_info['routing_key'],
                    'data': context.request.content.data,
                    'message': message,
                    'publish': self.adapter.publish,
                    'ack': self.adapter.ack
                    }
                context.dispatcher = Dispatcher(self.endpoint, params, consumer = self)
                # Call the handler
                context.dispatcher.endpoint.pipeline(context)
            except Exception as error:
                # Error happened
                self.logger.exception('Error occurred when processing subscription message')

    def startAsyncConsuming(self, channel):
        """Start async consuming
        """
        # Super
        super(RabbitMQSubscriptionConsumer, self).startAsyncConsuming(channel)
        # Conume queues
        for queue in self.subscribeEndpoint.queues:
            channel.basic.consume(queue, self, self.consumerTag, no_ack = not self.subscribeEndpoint.ack)
            self.logger.info('Consume queue [%s]', queue)

    def stopConsuming(self):
        """Stop consuming
        """
        try:
            self.channel.cancel(self.consumerTag)
        except:
            self.logger.exception('Failed to stop consuming by tag [%s]', self.consumerTag)
        # Super
        super(RabbitMQSubscriptionConsumer, self).stopConsuming()

class RabbitMQAnnonymousSubscriptionConsumer(RabbitMQSubscriptionConsumer):
    """The rabbitmq annonymous subscription consumer
    """
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.consumer.subscription.annonymous')

    def startAsyncConsuming(self, channel):
        """Start async consuming
        """
        # Super
        RabbitMQConsumer.startAsyncConsuming(self, channel)
        # Declare anonymous queue
        channel.queue.declare(auto_delete = True, cb = partial(self.onQueueDeclared, channel))

    def onQueueDeclared(self, channel, queue, msgCount, consumerCount):
        """On annoymous queue declared
        """
        self.logger.info('Annonymous queue [%s] declared', queue)
        # Bind
        for exchange, routingKey in self.subscribeEndpoint.bindings:
            channel.queue.bind(queue, exchange, routingKey)
        # Consume
        channel.basic.consume(queue, self, no_ack = not self.subscribeEndpoint.ack)
        self.logger.info('Consume queue [%s]', queue)

