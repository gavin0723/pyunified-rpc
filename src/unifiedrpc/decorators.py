# encoding=utf8
# The decorators

"""The decorators
"""

from protocol.endpoint import Endpoint

def endpoint(**kwargs):
    """The endpoint decorator, used to decorate a endpoint
    The decorated object could be a method, class or any other callable object
    """
    def decorate(callableObject):
        """Decorate the callableObject
        """
        return Endpoint(callableObject, **kwargs)
    return decorate

