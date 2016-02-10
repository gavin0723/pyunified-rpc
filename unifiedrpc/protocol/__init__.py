# enocding=utf8
# The Unified RPC Framework Protocol

"""The Unified RPC Framework Protocol
"""

from threading import local
from contextlib import contextmanager

from werkzeug.local import LocalProxy

from request import Request
from response import Response
from context import Context
from session import Session, DictSession, SessionManager
from probe import PROBE_LOCATION_BEFORE_REQUEST, PROBE_LOCATION_AFTER_REQUEST, PROBE_LOCATION_AFTER_RESPONSE

from definition import *
from runtime import Runtime, Caller

_context = local()
context = LocalProxy(lambda: _context.context if hasattr(_context, 'context') else None)

@contextmanager
def contextspace(runtime, adapter):
    """The context space
    """
    _context.context = Context(runtime, adapter)
    yield
    _context.context = None

__all__ = [
    'context', 'contextspace',
    'Runtime', 'Caller',
    'Endpoint', 'Request', 'Response', 'Context',
    'Session', 'DictSession', 'SessionManager'
    ]
