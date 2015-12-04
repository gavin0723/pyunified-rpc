# encoding=utf8

""" The rabbitmq adapter request
    Author: lipixun
    Created Time : Sat 14 Nov 2015 06:40:44 PM CST

    File Name: request.py
    Description:

"""

from cStringIO import StringIO

from unifiedrpc.protocol.request import Request, RequestContent

class RabbitMQRequest(Request):
    """The rabbitmq request
    """
    def __init__(self, consumer, message):
        """Create a new RabbitMQSubscriptionRequest
        """
        self.consumer = consumer
        self.message = message
        self.properties = message.properties
        # Get headers
        headers = self.properties.get('application_headers')
        # Get Content
        content = self.parseContent(headers)
        # Get parameters
        params = self.parseParameters(headers, content)
        # Get accept
        accept = self.parseAccept(headers, content)
        # Super
        super(RabbitMQRequest, self).__init__(headers, params, content, accept)

    def parseContent(self, headers):
        """Parse content
        """
        return RequestContent(
            self.properties.get('content_type'),
            self.properties.get('content_encoding'),
            stream = StringIO(self.message.body)
            )

    def parseParameters(self, headers, content):
        """Parse parameters
        """
        pass

    def parseAccept(self, headers, content):
        """Parse accept
        """
        pass
