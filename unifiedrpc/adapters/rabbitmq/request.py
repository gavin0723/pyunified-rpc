# encoding=utf8

""" The rabbitmq adapter request
    Author: lipixun
    Created Time : Sat 14 Nov 2015 06:40:44 PM CST

    File Name: request.py
    Description:

"""

from cStringIO import StringIO

from unifiedrpc.protocol.request import RequestContent

class RabbitMQRequest(object):
    """The rabbitmq request
    """
    def __init__(self, consumer, message):
        """Create a new RabbitMQSubscriptionRequest
        """
        self.consumer = consumer
        self.message = message
        # Get headers
        self.properties = message.properties
        self.headers = self.properties.get('application_headers')
        # Get request
        self.content = RequestContent(
            self.properties.get('content_type'),
            self.properties.get('content_encoding'),
            stream = StringIO(message.body)
            )

class RabbitMQSubscriptionRequest(RabbitMQRequest):
    """The rabbitmq subscription request
    """
