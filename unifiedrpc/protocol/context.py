# encoding=utf8
# The context object

"""The context object
"""

import threading

class Context(object):
    """The context class
    Attributes:
        server                              The RPC server object
        adapter                             The adapter of current request
        dispatch                            The dispatch object of current request
        response                            The response of current request
    """
    LOCAL = threading.local()

    def __init__(self, server, adapter = None, dispatch = None, request = None, response = None):
        """Create a new context
        """
        self.server = server
        self.adapter = adapter
        self.dispatch = dispatch
        self.request = request
        self.response = response

    def respond(self):
        """Respond current request
        """
        if not self.adapter:
            raise ValueError('Cannot respond the request without a adapter')
        return self.adapter.respond(self)

    @classmethod
    def current(cls):
        """Get the current context
        """
        if hasattr(Context.LOCAL, 'context'):
            return Context.LOCAL.context

    @classmethod
    def setCurrent(cls, context):
        """Set the current context
        """
        Context.LOCAL.context = context

    @classmethod
    def cleanCurrent(cls):
        """Clean current context
        """
        if hasattr(Context.LOCAL, 'context'):
            del Context.LOCAL.context

