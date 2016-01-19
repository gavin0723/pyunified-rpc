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
logger = logging.getLogger('example')

import json

from datetime import datetime

import mime

try:
    import unifiedrpc
except ImportError:
    sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
    import unifiedrpc

from unifiedrpc import Server, Service, endpoint
from unifiedrpc.adapters.rabbitmq import GeventRabbitMQSubscriptionAdapter, subscribe, annonymousSubscribe, \
        CONFIG_PUBLISH_CONTENT_TYPE, CONFIG_PUBLISH_CONTENT_ENCODING

class SimpleService(Service):
    """A simple service
    """
    def __init__(self):
        """Create a new SimpleServer
        """
        super(SimpleService, self).__init__('simple')

    def bootup4rabbitmqsub(self, runtime):
        """Boot up this service
        """
        # Declare exchange, queue and binding
        runtime.basic(prefetch = 5)
        runtime.exchange('test_exchange', 'direct')
        runtime.queue('test_queue', autoDelete = True)
        runtime.bind('test_queue', 'test_exchange', 'testkey')

    @subscribe('test_queue', ack = True)
    @endpoint()
    def testSubscription1(self, routingKey, data, message, publish, ack):
        """Get all persons
        """
        print '#1: Receive message with routing key [%s] data [%s]' % (routingKey, data)
        print '#1: Will send ack now'
        ack(message)
        print '#1: Ack sent'

    @annonymousSubscribe(('test_exchange', 'testkey2'), ack = False)
    @endpoint()
    def testSubscription2(self, routingKey, data, message, publish, ack):
        """Add a persion
        """
        print '#2: Receive message with routing key [%s] data [%s]' % (routingKey, data)
        print '#2: Send message to testSubscription1 with routingKey = testkey'
        gevent.sleep(1)
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
        server = Server([ SimpleService() ])
        runtime = server.startAsync([ GeventRabbitMQSubscriptionAdapter('rabbitmq', **{
            'host': args.host,
            'port': args.port,
            'user': args.user,
            'password': args.password,
            'vhost': args.vhost,
            CONFIG_PUBLISH_CONTENT_TYPE: mime.APPLICATION_JSON,
            CONFIG_PUBLISH_CONTENT_ENCODING: 'utf-8'
            }) ])
        # Wait for 2s
        print 'Server: Will sent messages to #2 every 1s, press ctrl + c to quit'
        try:
            while True:
                gevent.sleep(1)
                print 'Server: Send test message to #2'
                try:
                    runtime.adapters['rabbitmq'].publish('testkey2', 'test_exchange', json.dumps({ 'to': '#2', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S') }, ensure_ascii = False))
                except Exception as error:
                    logger.exception('Failed to publish test message')
                except KeyboardInterrupt:
                    break
        except KeyboardInterrupt:
            pass

    main()
