# encoding=utf8
# The dispatch definition

"""The dispatch definition
"""

class Dispatcher(object):
    """The dispatch class
    Attributes:
        endpoint                        The dispatched endpoint
        params                          The parameters to call endpoint
        attrs                           The dispatch attributes
    """
    def __init__(self, endpoint, params = None, **attrs):
        """Create a new Dispatch object
        """
        self.endpoint = endpoint
        self.params = params
        self.attrs = attrs

    def __getattr__(self, key):
        """Get the attribute
        """
        return self.attrs[key]
