# encoding=utf8
# The dispatch definition

"""The dispatch definition
"""

class Dispatch(object):
    """The dispatch class
    Attributes:
        endpoint                        The dispatched endpoint
        params                          The final parameters to call endpoint
        attrs                           The dispatch attributes
    """
    def __init__(self, endpoint, params = None, **kwargs):
        """Create a new Dispatch object
        """
        self.endpoint = endpoint
        self.params = params
        self.attrs = kwargs

