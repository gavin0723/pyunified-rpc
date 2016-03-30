# encoding=utf8
# The web adapter decorators

"""the web adapter decorators
"""

from definition import HTTP_METHOD_GET, HTTP_METHOD_POST, HTTP_METHOD_PUT, HTTP_METHOD_PATCH, HTTP_METHOD_DELETE, HTTP_METHOD_HEAD, HTTP_METHOD_OPTIONS

from endpoint import WebEndpoint

webEndpoint = WebEndpoint

def get(path, **kwargs):
    """The web get endpoint
    """
    return webEndpoint(path, method = HTTP_METHOD_GET, **kwargs)

def post(path, **kwargs):
    """The web post endpoint
    """
    return webEndpoint(path, method = HTTP_METHOD_POST, **kwargs)

def put(path, **kwargs):
    """The web put endpoint
    """
    return webEndpoint(path, method = HTTP_METHOD_PUT, **kwargs)

def patch(path, **kwargs):
    """The web patch endpoint
    """
    return webEndpoint(path, method = HTTP_METHOD_PATCH, **kwargs)

def delete(path, **kwargs):
    """The web delete endpoint
    """
    return webEndpoint(path, method = HTTP_METHOD_DELETE, **kwargs)

def head(path, **kwargs):
    """The web head endpoint
    """
    return webEndpoint(path, method = HTTP_METHOD_HEAD, **kwargs)

def options(path, **kwargs):
    """The web options endpoint
    """
    return webEndpoint(path, method = HTTP_METHOD_OPTIONS, **kwargs)

