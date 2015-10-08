# encoding=utf8
# The request definition

"""The request definition
"""

class Request(object):
    """The request class
    This is a general request object
    Attributes:
        headers                         A dict which key is a string value is any kind of object represents the request headers
        params                          A dict which key is a string value is any kind of object. The request parameters which used as RPC method parameters
        body                            The request body, any kind of object
        raw                             The raw request object (which is different among adapters)
    """
    def __init__(self, headers = None, params = None, body = None, raw = None):
        """Create a new Request object
        """
        self.headers = headers
        self.params = params
        self.body = body
        self.raw = raw

