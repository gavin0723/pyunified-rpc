# encoding=utf8
# The Unified RPC Framework

"""The Unified RPC Framework

About the context:

    The 'Context' is the class of Context
    The 'context' is a thread-local proxy which is the context object of current request

"""

try:
    from __version__ import version
except ImportError:
    version = 'dev'

from definition import *
from errors import *
from protocol import Context, context, contextspace
from decorators import *
from service import Service
from server import Server, GeventServer
