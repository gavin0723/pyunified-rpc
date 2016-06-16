# encoding=utf8

""" The secure stage
    Author: lipixun
    Created Time : 三  6/ 8 16:41:17 2016

    File Name: secure.py
    Description:

"""

from unifiedrpc import context
from unifiedrpc.errors import ForbiddenError

class SSLValidator(object):
    """The ssl validator
    This class will ensure the request should be transported via secure connection
    """
    def __init__(self, clientAuth = False):
        """Create a new SSLValidator
        Parameters:
            clientAuth                          Whether the client should be authenticated by ssl certificate
        """
        self.clientAuth = clientAuth

    def __call__(self):
        """Validate the request data
        """
        if not context.connection.ssl:
            raise ForbiddenError
        if self.clientAuth and not context.connection.remote.cert:
            raise ForbiddenError
