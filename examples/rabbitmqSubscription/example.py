#!/usr/bin/env python
# encoding=utf8
# The simple webservice example

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import gevent
from gevent import monkey
monkey.patch_all()

from os.path import abspath, dirname

import logging

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s', level = logging.DEBUG)

import json

from datetime import datetime

import mime

try:
    import unifiedrpc
except ImportError:
    sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
    import unifiedrpc

from unifiedrpc import Context, Server, Service, endpoint, CONFIG_RESPONSE_MIMETYPE, CONFIG_RESPONSE_CONTENT_CONTAINER
from unifiedrpc.adapters.rabbitmq import GeventRabbitMQAdapter, subscribe, annonymousSubscribe, DEFAULT_PUBLISH_CONTENT_ENCODING_KEY, DEFAULT_PUBLISH_CONTENT_TYPE_KEY

class SimpleService(Service):
    """A simple service
    """
    def __init__(self):
        """Create a new SimpleServer
        """
        super(SimpleService, self).__init__('simple')

    def bootup(self, adapter):
        """Boot up this service
        """
        if adapter.type == 'rabbitmq':
            # Bootup for rabbitmq
            channel = adapter.client.connection.channel()
            # Declare exchange, queue and binding
            channel.basic.qos(prefetch_count = 5)
            channel.exchange.declare('test_exchange', 'direct', nowait = False)
            channel.queue.declare('test_queue', auto_delete = True, nowait = False)
            channel.queue.bind('test_queue', 'test_exchange', 'testkey', nowait = False)
            # Done
            return channel

    @subscribe('test_queue', ack = True)
    @endpoint()
    def testSubscription1(self, routingKey, data, message, publish, ack):
        """Get all persons
        """
        print '#1: Receive message with routing key [%s] data [%s]' % (routingKey, data)
        print '#1: Will send ack in 5s'
        gevent.sleep(5)
        ack(message)
        print '#1: Ack sent'

    @annonymousSubscribe(('test_exchange', 'testkey2'))
    @endpoint()
    def testSubscription2(self, routingKey, data, message, publish, ack):
        """Add a persion
        """
        print '#2: Receive message with routing key [%s] data [%s]' % (routingKey, data)
        print '#2: Send message to testSubscription1 with routingKey = testkey'
        publish('testkey', 'test_exchange', json.dumps({ 'to': '#1', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S') }, ensure_ascii = False))
        print '#2: Message published'

if __name__ == '__main__':

    from argparse import ArgumentParser

    def getArguments():
        """Get arguments
        """
        parser = ArgumentParser(description = 'Rabbitmq subscription example')
        parser.add_argument('--host', dest = 'host', required = True, help = 'The rabbitmq host')
        parser.add_argument('--port', dest = 'port', type = int, default = 5672, help = 'The rabbitmq port')
        parser.add_argument('--user', dest = 'user', default = 'test', help = 'The user')
        parser.add_argument('--password', dest = 'password', default = 'test', help = 'The password')
        parser.add_argument('--vhost', dest = 'vhost', default = '/', help = 'The virtual host')
        # Done
        return parser.parse_args()

    def main():
        """The main entry
        """
        args = getArguments()
        # Create the server
        server = Server()
        server.addAdapter(GeventRabbitMQAdapter('rabbitmq', **{
            'host': args.host,
            'port': args.port,
            'user': args.user,
            'password': args.password,
            'vhost': args.vhost,
            DEFAULT_PUBLISH_CONTENT_TYPE_KEY: mime.APPLICATION_JSON,
            DEFAULT_PUBLISH_CONTENT_ENCODING_KEY: 'utf8'
            }))
        server.addService(SimpleService())
        # Start async
        server.startAsync()
        # Wait for 2s
        print 'Server: Will sent messages to #2 every 1s, press ctrl + c to quit'
        try:
            while True:
                gevent.sleep(1)
                print 'Server: Send test message to #2'
                server.adapters['rabbitmq'].publish('testkey2', 'test_exchange', json.dumps({ 'to': '#2', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S') }, ensure_ascii = False))
        except KeyboardInterrupt:
            pass

    main()

