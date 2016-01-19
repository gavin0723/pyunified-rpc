# encoding=utf8
# The decorators

"""The decorators
"""

from protocol import Endpoint

def endpoint(**configs):
    """The endpoint decorator, used to decorate a endpoint
    The decorated object could be a method, class or any other callable object
    """
    def decorate(callableObject):
        """Decorate the callableObject
        """
        return Endpoint(callableObject, configs)
    # Done
    return decorate
