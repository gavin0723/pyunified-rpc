# encoding=utf8
# The context object

"""The context object
"""

class Context(object):
    """The context class
    Attributes:
        server                              The RPC server object
        adapter                             The adapter of current request
        dispatcher                          The dispatcher object of current request
        response                            The response of current request
    """
    def __init__(self, server, adapter, dispatcher = None, request = None, session = None, response = None):
        """Create a new context
        """
        self.server = server
        self.adapter = adapter
        self.dispatcher = dispatcher
        self.request = request
        self.session = session
        self.response = response
        self.components = Components()
        self.shouldCleanSession = False

    def cleanSession(self):
        """Clean session
        After calling this method, the session will be removed in the response, but could still be accessed by context.session before responding
        """
        self.shouldCleanSession = True

class Components(object):
    """The components
    """
    pass
