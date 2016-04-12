# encoding=utf8

""" The general handler
    Author: lipixun
    Created Time : 四  4/ 7 16:18:23 2016

    File Name: handler.py
    Description:

"""
from callabletypes import CallableObject

class Handler(object):
    """Represents a handler
    """
    def __init__(self, method, weight = None):
        """Create a new Handler
        """
        self.callableObject = CallableObject.create(method)
        self.weight = weight

    def __get__(self, instance, cls):
        """Get descriptor
        """
        return self.callableObject.getCallable(instance)

    def __call__(self, bind, *args, **kwargs):
        """Call this handler
        """
        return self.callableObject.getCallable(bind)(*args, **kwargs)

    def getCallable(self, bind):
        """Get callable
        """
        return self.callableObject.getCallable(bind)

class StartupHandler(Handler):
    """The startup handler
    """
    def __init__(self, types, method):
        """Create a new StartupHandler
        """
        self.types = types
        # Super
        super(StartupHandler, self).__init__(method)

class ShutdownHandler(Handler):
    """The shutdown handler
    """
    def __init__(self, types, method):
        """Create a new ShutdownHandler
        """
        self.types = types
        # Super
        super(ShutdownHandler, self).__init__(method)
