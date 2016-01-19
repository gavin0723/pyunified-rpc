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

from collections import namedtuple
from threading import Lock

from haigha.message import Message

from unifiedrpc.adapters import Adapter
from unifiedrpc.protocol import context, contextspace
from unifiedrpc.protocol.runtime import ServiceAdapterRuntime
from unifiedrpc.errors import *

from client import GeventRabbitMQClient
from endpoint import SubscribeEndpoint, AnonymousSubscribeEndpoint
from request import RabbitMQRequest
from response import RabbitMQResponse
from definition import ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY, CONFIG_PUBLISH_CONTENT_TYPE, CONFIG_PUBLISH_CONTENT_ENCODING
from errors import NotStartedError

GLOCK = Lock()

class RabbitMQSubscriptionAdapter(Adapter):
    """The rabbitmq subscription adapter
    """
    type = 'rabbitmqsub'
    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.subscription')

    def __init__(self, name, **configs):
        """Create a new RabbitMQAdapter
        """
        self.client = None
        self.runtimes = {}          # A dict which key is service name, value is RabbitMQServiceAdapterRuntime
        # Super
        super(RabbitMQSubscriptionAdapter, self).__init__(name, **configs)

    def getStatus(self):
        """Get the adapter status
        Returns:
            A json serializable dict
        """
        raise NotImplementedError

    def onRabbitMQConnected(self):
        """On rabbitmq connected
        """
        for name, runtime in self.runtimes.iteritems():
            try:
                runtime.onConnected()
            except:
                self.logger.exception('Call service [%s] runtime connect callback failed', name)

    def onRabbitMQDisconnected(self):
        """On rabbitmq disconnected
        """
        for name, runtime in self.runtimes.iteritems():
            try:
                runtime.onClose()
            except:
                self.logger.exception('Call service [%s] runtime close callback failed', name)

    def startAsync(self, runtime):
        """Start asynchronously
        """
        # Create client
        self.client = self.getRabbitMQClient()

    def shutdown(self):
        """Shutdown the adapter
        Returns:
            Nothing
        """
        self.client.close()
        self.client = None
        self.runtimes = {}

    def attach(self, serviceRuntime):
        """Attach a service
        Returns:
            ServiceAdapterRuntime
        """
        if serviceRuntime.service.name in self.runtimes:
            raise ValueError('Conflict service name [%s]' % serviceRuntime.service.name)
        # Get subscription endpoints
        endpoints = list(self.getEndpointFromService(serviceRuntime.service))
        # Create runtime & add
        runtime = RabbitMQSubscriptionServiceAdapterRuntime(self, serviceRuntime, endpoints)
        self.runtimes[serviceRuntime.service.name] = runtime
        # Done
        return runtime

    def publish(self, routingKey, exchange, body, durable = False, contentType = None, encoding = None):
        """Publish messages
        """
        if not self.client:
            raise NotStartedError
        # Get properties
        properties = {}
        contentType = contentType or self.configs.get(CONFIG_PUBLISH_CONTENT_TYPE)
        encoding = encoding or self.configs.get(CONFIG_PUBLISH_CONTENT_ENCODING)
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

    def getRabbitMQClient(self):
        """Get a new rabbitmq client
        """
        raise NotImplementedError

    @classmethod
    def getEndpointFromService(cls, service):
        """Get the subscribe endpoint from service
        """
        if service.activeEndpoints:
            for endpoint in service.activeEndpoints.itervalues():
                subEndpoints = endpoint.children.get(ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY)
                if subEndpoints:
                    for subEndpoint in subEndpoints:
                        yield subEndpoint, endpoint

class GeventRabbitMQSubscriptionAdapter(RabbitMQSubscriptionAdapter):
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

class MessageReceiver(object):
    """The message receiver
    """
    def __init__(self, rabbitMQEndpoint, endpoint, queue, runtime):
        """Create a new MessageReceiver
        """
        self.rabbitMQEndpoint = rabbitMQEndpoint
        self.endpoint = endpoint
        self.queue = queue
        self.runtime = runtime

    def __call__(self, message):
        """On message received
        """
        return self.runtime(self.rabbitMQEndpoint, self.endpoint, self.queue, message)

class RabbitMQSubscriptionServiceAdapterRuntime(ServiceAdapterRuntime):
    """The rabbitmq subscription service adapter runtime
    """
    DEFAULT_PREFETCH = 10

    logger = logging.getLogger('unifiedrpc.adapter.rabbitmq.subscription.serviceAdapterRuntime')

    def __init__(self, adapter, serviceRuntime, endpoints, serviceShutdown = None):
        """Create a new RabbitMQServiceAdapterRuntime
        """
        # Super
        super(RabbitMQSubscriptionServiceAdapterRuntime, self).__init__(adapter, serviceRuntime, serviceShutdown)
        # Configs
        self.prefetch = None
        self.exchanges = {}         # A dict of exchanges, key is exchange name, value is ExchangeDeclaration
        self.namedQueues = {}       # A dict of named queues, key is queue name, value is QueueDeclaration
        self.anonymousQueues = {}   # A dict of anonymous queues, key is queue name, value is (subscription endpoint, active endpoint)
        self.bindings = []          # A list of bindings, Binding
        self.endpoints = endpoints  # A list of (subscription endpoint, active endpoint)
        # The connected status
        self.channel = None

    def basic(self, prefetch = None):
        """Config the channel basic configuration
        """
        self.prefetch = prefetch

    def exchange(self, name, type):
        """Declare an exchange
        """
        if name in self.exchanges:
            raise ValueError('Conflict exchange [%s]', name)
        self.exchanges[name] = ExchangeDeclaration(name, type)

    def queue(self, name, autoDelete = True, durable = False):
        """Declare a queue
        """
        if name in self.namedQueues:
            raise ValueError('Conflict queue [%s]' % name)
        self.namedQueues[name] = QueueDeclaration(name, autoDelete, durable)

    def bind(self, queue, exchange, key):
        """Bind a queue to a exchange with a specified key
        """
        self.bindings.append(Binding(queue, exchange, key))

    def onConnected(self):
        """On rabbitmq connected
        """
        self.logger.info('Service [%s]: Initialize service adapter runtime', self.serviceRuntime.service.name)
        # Create new channel
        self.channel = self.adapter.client.connection.channel(synchronous = True)
        # Set channel basic
        self.channel.basic.qos(prefetch_count = self.prefetch or self.DEFAULT_PREFETCH)
        self.logger.info('Service [%s]: Channel created', self.serviceRuntime.service.name)
        # Declare exchanges
        for exchange in self.exchanges.itervalues():
            self.channel.exchange.declare(exchange.name, exchange.type)
            self.logger.info('Service [%s]: Exchange [%s] declared', self.serviceRuntime.service.name, exchange.name)
        # Declare named queues
        for queue in self.namedQueues.itervalues():
            queueName, msgCount, consumerCount = self.channel.queue.declare(queue.name, durable = queue.durable, auto_delete = queue.autoDelete, nowait = False)
            self.logger.info('Service [%s]: Named queue [%s] declared with [%d] messges and [%d] consumers',
                self.serviceRuntime.service.name,
                queue.name,
                msgCount,
                consumerCount
                )
        # Bind named queues
        for binding in self.bindings:
            self.channel.queue.bind(binding.queue, binding.exchange, binding.key)
            self.logger.info('Service [%s]: Bind named queue [%s] to exchange [%s] with key [%s]',
                self.serviceRuntime.service.name,
                binding.queue,
                binding.exchange,
                binding.key or ''
                )
        # Declare anonymous queues and bind them
        for subep, ep in self.endpoints:
            if isinstance(subep, AnonymousSubscribeEndpoint):
                # Declare a anonymous queue
                queueName, msgCount, consumerCount = self.channel.queue.declare(durable = False, auto_delete = True, exclusive = True, nowait = False)
                self.logger.info('Service [%s]: Anonymous queue [%s] declared', self.serviceRuntime.service.name, queueName)
                # Bind the queue
                for exchange, key in subep.bindings:
                    self.channel.queue.bind(queueName, exchange, key)
                    self.logger.info('Service [%s]: Bind anonymous queue [%s] to exchange [%s] with key [%s]',
                        self.serviceRuntime.service.name,
                        queueName,
                        exchange,
                        key or ''
                        )
                # Add this queue
                self.anonymousQueues[queueName] = (subep, ep)
        # Consuming
        for subep, ep in self.endpoints:
            if isinstance(subep, SubscribeEndpoint):
                for queue in subep.queues:
                    self.channel.basic.consume(queue, MessageReceiver(subep, ep, queue, self), no_ack = not subep.ack)
                    self.logger.info('Service [%s]: Consume named queue [%s]', self.serviceRuntime.service.name, queue)
        for queueName, (subep, ep) in self.anonymousQueues.iteritems():
            self.channel.basic.consume(queueName, MessageReceiver(subep, ep, queueName, self), no_ack = not subep.ack)
            self.logger.info('Service [%s]: Consume anonymous queue [%s]', self.serviceRuntime.service.name, queueName)
        # Done

    def onClosed(self):
        """On rabbitmq closed
        """
        # Clean
        self.channel = None
        self.anonymousQueues = []

    def shutdown(self):
        """Shutdown this runtime
        """
        # Super
        super(RabbitMQServiceAdapterRuntime, self).shutdown()
        # Shutdown
        self.channel.close()
        self.channel = None
        self.anonymousQueues = []
        # Remove
        with GLOCK:
            if self.serviceRuntime.service.name in self.adapter.runtimes:
                del self.adapter.runtimes[self.serviceRuntime.service.name]

    def __call__(self, subep, ep, queue, message):
        """On message received
        """
        # Start context
        with contextspace(self.serviceRuntime.runtime, self.adapter):
            try:
                # Parse request
                context.request = RabbitMQRequest(message)
                if context.request.content and context.request.content.mimeType:
                    if not context.request.content.encoding:
                        context.request.content.encoding = context.request.getDefinedEncoding(context)
                    context.request.content.data = context.components.contentParser.parse(context)
                # Get the parameters
                params = {
                    'routingKey': message.delivery_info['routing_key'],
                    'data': context.request.content.data,
                    'message': message,
                    'publish': self.adapter.publish,
                    'ack': self.adapter.ack
                    }
                context.endpoint = ep
                context.params = params
                # Call the endpoint
                return context.endpoint(context)
            except Exception as error:
                # Error happened
                self.logger.exception('Error occurred when processing subscription message')

ExchangeDeclaration = namedtuple('ExchangeDeclaration', 'name,type')
QueueDeclaration = namedtuple('QueueDeclaration', 'name,autoDelete,durable')
Binding = namedtuple('Binding', 'queue,exchange,key')
