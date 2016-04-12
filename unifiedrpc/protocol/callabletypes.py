# encoding=utf8

""" The callable types
    Author: lipixun
    Created Time : 四  4/ 7 14:52:32 2016

    File Name: callabletypes.py
    Description:

"""
import inspect

from types import FunctionType, MethodType, ClassType

class CallableObject(object):
    """The callable object
    """
    def __init__(self, obj, bindObject = None):
        """Create a new CallableObject
        """
        self.obj = obj
        self.bindObject = bindObject

    def __get__(self, instance, cls):
        """The get descriptor
        """
        return self.getCallable(instance)

    def __getattr__(self, key):
        """Get the attribute, transparently access attribute of object
        """
        return getattr(self.obj, key)

    def bind(self, bindObject):
        """Bind this callable object
        """
        return type(self)(self.obj, bindObject)

    def getCallable(self, bindObject = None):
        """Get the callable object
        """
        return self.obj

    def getSignature(self):
        """Get the signature
        Returns:
            Signature object
        """
        raise NotImplementedError

    @classmethod
    def create(self, obj):
        """Create the callable object
        """
        if isinstance(obj, (FunctionType, MethodType)):
            return MethodCallable(obj)
        elif hasattr(obj, '__call__'):
            return ClassCallable(obj)
        else:
            raise ValueError('Unsupported callable object [%s]' % type(obj).__name__)

class Signature(object):
    """The Endpoint Signature
    Attributes:
        parameter                       The ParameterConstraint object
    NOTE:
        For the MethodType (Which is the method of a class), the first argument (self usually) will be ignored by design
    """
    def __init__(self, parameter):
        """Create a new Signature
        """
        self.parameter = parameter

    def __str__(self):
        """Convert to string
        """
        return 'Parameters [%s]' % self.parameter

    def __repr__(self):
        """Repr
        """
        return 'Endpoint Signature: %s' % self

class ParameterConstraint(object):
    """The parameter constraint of the endpoint
    Attributes:
        args                            The arguments, a list of argument name
        keywordArgName                  The key word argument name, None if not exist
        defaults                        The default values of argument
    """
    def __init__(self, args, keywordArgName = None, defaults = None):
        """Create a new ParameterConstraint
        """
        self.args = args
        self.keywordArgName = keywordArgName
        self.defaults = defaults or {}

    @property
    def isDynamic(self):
        """Check if this parameter constraint support dynamic argument
        """
        return not self.keywordArgName is None

class MethodCallable(CallableObject):
    """The method callable
    """
    def inspect(self):
        """Inspect the method
        """
        args, varArgs, kwArgs, defaults = inspect.getargspec(self.obj)
        args = args or tuple()
        # Done
        return args, varArgs, kwArgs, defaults

    def getSignature(self):
        """Get the signature of a method
        Returns:
            Signature object
        """
        args, varArgs, kwArgs, defaults = self.inspect()
        if self.bindObject:
            # Remove the first args in bind mode
            args = tuple(args[1: ])
        # Do not support args with tuple
        for arg in args:
            if not isinstance(arg, basestring):
                raise ValueError('Do not support argument with type [%s]' % type(arg).__name__)
        # Get the default values to the dict
        if defaults:
            if len(defaults) > len(args):
                raise ValueError('Invalid method default values')
            defaults = dict(zip(args[-len(defaults): ], defaults))
        # Get the var args
        if varArgs:
            raise ValueError('Donot support var arguments in endpoint')
        # Done
        return Signature(ParameterConstraint(args, kwArgs, defaults))

    def getCallable(self, bindObject = None):
        """Get the callable object
        """
        bindObject = bindObject if bindObject else self.bindObject
        # Return the callable
        if not bindObject or (hasattr(self.obj, '__self__') and self.obj.__self__):
            return self.obj
        else:
            return MethodType(self.obj, bindObject)

class ClassCallable(CallableObject):
    """The method callable
    """
    def inspect(self):
        """Inspect the method
        """
        args, varArgs, kwArgs, defaults = inspect.getargspec(self.obj.__call__)
        args = args or tuple()
        # Done
        return args, varArgs, kwArgs, defaults

    def getSignature(self):
        """Get the signature of a method
        Returns:
            Signature object
        """
        args, varArgs, kwArgs, defaults = self.inspect()
        # Remove the first args in bind mode
        args = tuple(args[1: ])
        # Do not support args with tuple
        for arg in args:
            if not isinstance(arg, basestring):
                raise ValueError('Do not support argument with type [%s]' % type(arg).__name__)
        # Get the default values to the dict
        if defaults:
            if len(defaults) > len(args):
                raise ValueError('Invalid method default values')
            defaults = dict(zip(args[-len(defaults): ], defaults))
        # Get the var args
        if varArgs:
            raise ValueError('Donot support var arguments in endpoint')
        # Done
        return Signature(ParameterConstraint(args, kwArgs, defaults))

    def getCallable(self, bindObject = None):
        """Get the callable object
        """
        return self.obj
