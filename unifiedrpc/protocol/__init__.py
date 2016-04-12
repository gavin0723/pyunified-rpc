# encoding=utf8
# The Unified RPC Framework Protocol

""" The Unified RPC Framework Protocol
    Author: lipixun
    Created Time : 四  4/ 7 14:52:32 2016

    File Name: __init__.py
    Description:

"""

from context import context, Context
from request import Request
from handler import Handler, StartupHandler, ShutdownHandler
from service import Service
from session import Session, DictSession, SessionManager
from endpoint import Endpoint
from response import Response
from execution import createResponseResult
from definition import *

def startup(*types):
    """The startup handler decorator
    """
    def decorator(method):
        """The decorator
        """
        return StartupHandler(types, method)
    # Done
    return decorator

def shutdown(*types):
    """The shutdown handler decorator
    """
    def decorator(method):
        """The decorator
        """
        return ShutdownHandler(types, method)
    # Done
    return decorator

__all__ = [
    'context',
    'Endpoint', 'Request', 'Response', 'Context',
    'Session', 'DictSession', 'SessionManager'
    ]
