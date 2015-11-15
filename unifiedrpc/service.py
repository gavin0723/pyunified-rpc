# encoding=utf8
# The abstract service

"""The abstract service
"""

from protocol import Endpoint

class Service(object):
    """The service
    """
    def __init__(self, name):
        """Create a new Service
        """
        self.name = name

    def bootup(self, adapter):
        """Bootup this service
        """
        pass

    def shutdown(self, adapter):
        """Shutdown this service
        """
        pass

    def getEndpoints(self):
        """Get the endpoints of current service
        Returns:
            A list of endpoints
        """
        endpoints = []
        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, Endpoint):
                endpoints.append(value)
        return endpoints
