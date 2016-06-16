# encoding=utf8

""" The secure helpers
    Author: lipixun
    Created Time : 三  6/ 8 16:40:19 2016

    File Name: secure.py
    Description:

"""

from unifiedrpc.stages import SSLValidator

def requiressl(clientAuth = False):
    """Require the request should be transported via ssl
    """
    def decorate(endpoint):
        """The method to decorate the endpoint
        """
        endpoint._stage.addPreRequest(SSLValidator(clientAuth), 5000)
        # Done
        return endpoint
    # Done
    return decorate
