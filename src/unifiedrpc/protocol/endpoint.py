# encoding=utf8
# The endpoint

"""The endpoint

Endpoint is the one which actually handle the request finally

"""

import types
import inspect

from collections import OrderedDict

class Endpoint(object):
    """The Endpoint
    Attributes:
        callableObject                  A callable object
        signature                       The Signature object
        document                        The document
    """
    def __init__(self, callableObject, document = None, children = None):
        """Create a new Endpoint
        """
        if callableObject is None:
            raise ValueError('callableObject cannot be None')
        self.callableObject = callableObject
        # Inspect the callable object
        if inspect.ismethod(self.callableObject):
            # An instance method
            self.signature = self.getSignature(self.callableObject, ignoreFirstArgument = True)
            self.document = self.callableObject.__doc__ if not document else document
        elif isinstance(self.callableObject, classmethod):
            # A class method
            self.signature = self.getSignature(self.callableObject.__func__, ignoreFirstArgument = True)
            self.document = self.callableObject.__doc__ if not document else document
        elif inspect.isfunction(self.callableObject):
            # A function
            self.signature = self.getSignature(self.callableObject)
            self.document = self.callableObject.__doc__ if not document else document
        elif inspect.isclass(self.callableObject):
            # A class
            self.signature = self.getSignature(
                self.callableObject.__init__,
                name = self.callableObject.__name__,
                ignoreFirstArgument = True
                )
            self.document = self.callableObject.__doc__ if not document else document
        elif hasattr(self.callableObject, '__call__'):
            # An object with '__call__' method
            self.signature = self.getSignature(
                self.callableObject.__call__,
                name = self.callableObject.__class__.__name__,
                ignoreFirstArgument = True
                )
            self.document = self.callableObject.__doc__ if not document else document
        else:
            raise ValueError('Unsupported callable object [%s] of type [%s]' % (self.callableObject, type(self.callableObject).__name__))
        # Set the children
        self.children = children or {}

    def __getattr__(self, key):
        """Get the attribute, transparently access attribute of _endpoint
        """
        return getattr(self.callableObject, key)

    def __get__(self, instance, owner):
        """Get the caller of this endpoint
        NOTE:
            This method is called on instance method and class method
        Returns:
            The Endpoint object
        """
        endpoint = Endpoint(self.callableObject.__get__(instance, owner), self.document, self.children)
        if instance:
            # Set the endpoint instance to the instance
            setattr(instance, endpoint.signature.name, endpoint)
        # Done
        return endpoint

    def __call__(self, *args, **kwargs):
        """Call the endpoint
        """
        return self.callableObject(*args, **kwargs)

    def getSignature(self, method, name = None, ignoreFirstArgument = False):
        """Get the signature of a method
        Parameters:
            method                      The method
            name                        The method name
            ignoreFirstArgument         Ignore the first argument or not
        Returns:
            Signature object
        """
        args, varArgs, kwArgs, defaults = inspect.getargspec(method)
        args = args or tuple()
        # Do not support args with tuple
        for arg in args:
            if not isinstance(arg, basestring):
                raise ValueError('Do not support argument with type [%s]' % type(arg).__name__)
        # Get the default values to the dict
        if defaults:
            if len(defaults) > len(args):
                raise ValueError('Invalid method default values')
            defaults = dict(zip(args[-len(defaults): ], defaults))
        # Get all of the known arguments
        if ignoreFirstArgument:
            # Ignore the first argument, must be self or cls
            args = args[1: ]
        # Get the var args
        if varArgs:
            raise ValueError('Donot support var arguments in endpoint')
        # Done
        return Signature(name if name else method.__name__, ParameterConstraint(args, kwArgs, defaults))

class Signature(object):
    """The Endpoint Signature
    Attributes:
        name                            The method name
        parameter                       The ParameterConstraint object
        document                        The document string
    NOTE:
        For the MethodType (Which is the method of a class), the first argument (self usually) will be ignored by design
    """
    def __init__(self, name, parameter):
        """Create a new Signature
        """
        self.name = name
        self.parameter = parameter

    def __str__(self):
        """Convert to string
        """
        return 'Name [%s] Parameters [%s]' % (self.name, self.parameter)

    def __repr__(self):
        """Repr
        """
        return 'Endpoint Signature: %s' % self

class ParameterConstraint(object):
    """The parameter constraint of the endpoint
    Attributes:
        args                            The arguments, a list of argument name
        varArg                          The var args argument name, None if not exist
        keywordArg                      The key-word args argument name, None if not exist
        defaults                        The default values of argument
        types                           The type of argument
    """
    def __init__(self, args, keywordArg = None, defaults = None, types = None):
        """Create a new ParameterConstraint
        """
        self.args = args
        self.keywordArg = keywordArg
        self.defaults = defaults or {}
        self.types = types or {}

    def __str__(self):
        """Convert to string
        """
        return 'Args {%s} KW {%s} Defaults {%s} Types {%s}' % (
            ','.join(self.args) if self.args else '',
            self.keywordArg if self.keywordArg else '',
            ','.join([ '%s:%s' % (x, y) for x, y in self.defaults.iteritems() ]) if self.defaults else '',
            ','.join([ '%s:%s' % (x, y) for x, y in self.types.iteritems() ]) if self.types else '',
            )
