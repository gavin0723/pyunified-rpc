# encoding=utf8
# The web adapter decorators

"""the web adapter decorators
"""

from definition import HTTP_METHOD_GET, HTTP_METHOD_POST, HTTP_METHOD_PUT, HTTP_METHOD_DELETE, HTTP_METHOD_HEAD, HTTP_METHOD_OPTIONS, \
        ENDPOINT_CHILDREN_WEBENDPOINT_KEY

from endpoint import WebEndpoint

def endpoint(**kwargs):
    """The web endpoint
    """
    webEndpoint = WebEndpoint(**kwargs)
    def decorate(endpoint):
        """Decorate the endpoint
        """
        if ENDPOINT_CHILDREN_WEBENDPOINT_KEY in endpoint.children:
            endpoint.children[ENDPOINT_CHILDREN_WEBENDPOINT_KEY][webEndpoint.id] = webEndpoint
        else:
            endpoint.children[ENDPOINT_CHILDREN_WEBENDPOINT_KEY] = { webEndpoint.id: webEndpoint }
        # Done
        return endpoint
    return decorate

def get(**kwargs):
    """The web get endpoint
    """
    return endpoint(method = HTTP_METHOD_GET, **kwargs)

def post(**kwargs):
    """The web post endpoint
    """
    return endpoint(method = HTTP_METHOD_POST, **kwargs)

def put(**kwargs):
    """The web put endpoint
    """
    return endpoint(method = HTTP_METHOD_PUT, **kwargs)

def delete(**kwargs):
    """The web delete endpoint
    """
    return endpoint(method = HTTP_METHOD_DELETE, **kwargs)

def head(**kwargs):
    """The web head endpoint
    """
    return endpoint(method = HTTP_METHOD_HEAD, **kwargs)

def options(**kwargs):
    """The web options endpoint
    """
    return endpoint(method = HTTP_METHOD_OPTIONS, **kwargs)

