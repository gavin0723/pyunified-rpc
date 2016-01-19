# encoding=utf8

""" The unified RPC framework
    Author: lipixun
    Created Time : 四 12/17 17:43:19 2015

    File Name: __init__.py
    Description:

        About the context:

            The 'Context' is the class of Context
            The 'context' is a thread-local proxy which is the context object of current request

"""

from __version__ import __version__

from definition import *
from errors import *
from protocol import Service, context, contextspace
from decorators import *
from server import Server
