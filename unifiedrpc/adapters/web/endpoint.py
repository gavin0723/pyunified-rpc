# encoding=utf8
# The web adapter endpoint

"""The web endpoint adapter
"""

from uuid import uuid4

from werkzeug.routing import Rule

from definition import ENDPOINT_CHILDREN_WEBENDPOINT_KEY

class WebEndpoint(object):
    """The web endpoint
    Attributes:
        path                            The path
        name                            The name of this endpoint, just used for friendly naming
        method                          The method(s), could be a single method or a list/tuple of methods
        host                            The host to match
        subdomain                       The sub domain to match
        cookieSecret                    The cookie secret to use, will use adapter cookie secret config if not specified
        allowedMultiParams              The allowed parameters to have multiple values, the value of this parameter could be:
                                        - A list of parameter name
                                        - string '*' indicates ALL parameters
                                        NOTE:
                                            if a parameter is allowed, the value of that parameter will always be array if any value exists
    """
    def __init__(self,
            path,
            name = None,
            method = None,
            host = None,
            subdomain = None,
            cookieSecret = None,
            allowedMultiParams = None,
            configs = None
            ):
        """Create a new WebEndpoint
        """
        self.path = path
        self.name = name
        self.method = method
        self.host = host
        self.subdomain = subdomain
        self.cookieSecret = cookieSecret
        self.allowedMultiParams = allowedMultiParams
        self._configs = configs or {}

    def __call__(self, endpoint):
        """Attach to endpoint object
        Parameters:
            endpoint                    The protocol.Endpoint object
        Returns:
            The protocol.Endpoint object
        """
        # Add this web endpoint to the endpoint object
        if not ENDPOINT_CHILDREN_WEBENDPOINT_KEY in endpoint.children:
            endpoint.children[ENDPOINT_CHILDREN_WEBENDPOINT_KEY] = [ self ]
        else:
            endpoint.children[ENDPOINT_CHILDREN_WEBENDPOINT_KEY].append(self)
        # Done
        return endpoint

    def getUrlRule(self, endpoint):
        """Get the url rule
        """
        # Get the methods
        if not self.method:
            methods = None
        elif isinstance(self.method, basestring):
            methods = (self.method, )
        else:
            methods = self.method
        # Create the Rule
        return Rule(self.path, endpoint = (self, endpoint), methods = methods, host = self.host, subdomain = self.subdomain)
