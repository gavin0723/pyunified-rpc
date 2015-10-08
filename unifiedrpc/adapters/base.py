# encoding=utf8
# The base adapter definitions

"""The base adapter definitions
"""

class AdapterBase(object):
    """The adapter base class
    """
    def startAsync(self, onRequestCallback, endpoints):
        """Start asynchronously
        Parameters:
            onRequestCallback           The callback which should be called when received a new request, the method has 
            endpoints                   A list of all endpoints
        Returns:
            Nothing
        """
        raise NotImplementedError

    def close(self):
        """Close current adapter
        Returns:
            Nothing
        """
        raise NotImplementedError

    def respond(self, context):
        """Respond the request by context
        """

