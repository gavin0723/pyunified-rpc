# encoding=utf8
# The endpoint discover

"""The endpoint discover
"""

from protocol import Endpoint

class EndpointDiscover(object):
    """The EndpointDiscover class
    """
    def discover(self, obj):
        """Discover endpoints
        Parameters:
            obj                         Any kind of supported object
        Returns:
            A list of endpoint
        """
        raise NotImplementedError

class ServiceEndpointDiscover(object):
    """The service endpoint discover
    """
    def discover(self, service):
        """Discover endpoints from service
        Parameters:
            service                     The Service object
        Returns:
            A list of endpoint
        """
        endpoints = []
        for name in dir(service):
            value = getattr(service, name)
            if isinstance(value, Endpoint):
                endpoints.append(value)
        return endpoints
