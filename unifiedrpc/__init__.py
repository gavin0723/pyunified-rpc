# encoding=utf8
# The Unified RPC Framework

"""The Unified RPC Framework
"""

try:
    from __version__ import version
except ImportError:
    version = 'dev'

from decorators import *

from protocol.context import Context

