# encoding=utf8
# The base adapter definitions

"""The base adapter definitions
"""

class Adapter(object):
    """The adapter base class
    Attributes:
        name                            The adapter name. Each adapter should have a unique name
    """
    def __init__(self, name, **configs):
        """Create a new AdapterBase
        """
        self.name = name
        self.configs = configs

    def startAsync(self, onRequestCallback, onErrorCallback, endpoints):
        """Start asynchronously
        Parameters:
            onRequestCallback           The callback which should be called when received a new request, the method has two parameters:
                                        - incoming          The incoming request, any kind of object
                                        - adapter           The adapter
                                        Returns the Context object
                                        NOTE:
                                            This callback will NEVER raise any exception
            onErrorCallback             The callback which should be called when an unhandled error occurred, the method has three parameters:
                                        - error             The error object
                                        - adapter           The adapter
                                        - traceback         The traceback string, optional
                                        - message           The message of this error, optional
                                        NOTE:
                                            This callback will NEVER raise any exception
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

    def parseRequest(self, incoming, context):
        """Parse the request, set the context
        """
        raise NotImplementedError

    def initResponse(self, incoming, context):
        """Initialize the response
        """
        raise NotImplementedError

    def dispatch(self, context):
        """Dispatch the request
        """
        raise NotImplementedError

    def handleError(self, error, traceback, incoming, context):
        """Handle the request error
        Parameters:
            error                       The error object
            traceback                   The traceback string
            incoming                    The incoming parameters
            context                     The context
        Returns:
            Nothing
        """
        raise NotImplementedError

