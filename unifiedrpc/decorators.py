# encoding=utf8
# The decorators

"""The decorators
"""

from protocol import Endpoint

def endpoint(**configs):
    """The endpoint decorator, used to decorate a endpoint
    The decorated object could be a method, class or any other callable object
    """
    def decorate(executor):
        """Decorate the endpoint
        """
        return Endpoint(executor, configs)
    # Done
    return decorate
