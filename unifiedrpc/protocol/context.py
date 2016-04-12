# encoding=utf8
# The context object

"""The context object
"""

from threading import local
from contextlib import contextmanager

from werkzeug.local import LocalProxy

from unifiedrpc.definition import CONFIG_REQUEST_CONTENT_PARSER, CONFIG_RESPONSE_CONTENT_CONTAINER, CONFIG_RESPONSE_CONTENT_BUILDER

class Context(object):
    """The context class
    Attributes:
        runtime                             The runtime object
        adapter                             The adapter of current request
        request                             The request
        session                             The session
        response                            The response
    """
    def __init__(self, server, adapter, request = None, dispatchResult = None, session = None, response = None, meta = None):
        """Create a new context
        """
        self.server = server
        self.adapter = adapter
        self.request = request
        self.dispatchResult = dispatchResult
        self.session = session
        self.response = response
        self.meta = meta or {}

    def __getattr__(self, key):
        """Get attribute which is not pre-defined, try the meta
        """
        if key in self.meta:
            return self.meta[key]
        # Raise error
        raise AttributeError

    def execution(self):
        """Get the execution context
        """
        from execution import ExecutionContext
        return ExecutionContext(
            self.server,
            self.adapter,
            self.dispatchResult.service if self.dispatchResult else None,
            self.dispatchResult.endpoint if self.dispatchResult else None
            )

_local = local()
context = LocalProxy(lambda: _local.context if hasattr(_local, 'context') else None)

def setContext(context):
    """Set the current context object
    """
    _local.context = context

def clearContext():
    """Clear the current context object
    """
    if hasattr(_local, 'context'):
        del _local.context
