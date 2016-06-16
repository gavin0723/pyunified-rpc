# encoding=utf8

""" The requests adapter
    Author: lipixun
    Created Time : 三  6/ 8 16:53:41 2016

    File Name: __init__.py
    Description:

        This adapter will help to handle http error when requesting to unified-rpc server via requests

"""

from errorhandlers import Http2UnifiedRPCErrorHandler

__all__ = [ 'Http2UnifiedRPCErrorHandler' ]

