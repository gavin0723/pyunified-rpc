# encoding=utf8

""" The ping service
    Author: lipixun
    Created Time : 三  3/30 00:16:08 2016

    File Name: ping.py
    Description:

"""

from unifiedrpc import endpoint, Service
from unifiedrpc.adapters.web import get

class PingService(Service):
    """The ping service
    """
    def __init__(self, name = 'ping', pingResponse = 'OK'):
        """Create a new PingService
        """
        self.pingResponse = pingResponse
        # Super
        super(PingService, self).__init__(name)

    @get('/_ping')
    @endpoint()
    def ping(self):
        """Ping this service
        """
        return self.pingResponse

