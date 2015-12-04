# enocding=utf8
# The Unified RPC Framework Protocol

"""The Unified RPC Framework Protocol
"""

from threading import local
from contextlib import contextmanager

from werkzeug.local import LocalProxy

from endpoint import Endpoint
from request import Request
from response import Response
from dispatcher import Dispatcher
from context import Context
from session import Session, DictSession, SessionManager

_context = local()
context = LocalProxy(lambda: _context.context if hasattr(_context, 'context') else None)

@contextmanager
def contextspace(server, adapter):
    """The context space
    """
    _context.context = Context(server, adapter)
    yield
    _context.context = None

__all__ = [ 'Endpoint', 'Request', 'Response', 'Dispatcher', 'Context', 'context', 'contextspace', 'Session', 'DictSession', 'SessionManager' ]
