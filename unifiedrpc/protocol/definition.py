# encoding=utf8

""" The definition of protocol
    Author: lipixun
    Created Time : 一  1/18 17:12:29 2016

    File Name: definition.py
    Description:

"""

import inspect

CONFIG_ENDPOINT_PARAMETER_TYPE                      = 'endpoint.parameter.type'
CONFIG_ENDPOINT_SESSION_MANAGER                     = 'endpoint.session.manager'

from runtime import ServiceRuntime, ServiceAdapterRuntime, ActiveEndpoint

class Service(object):
    """The service
    Attributes:
        name                    The unique service name
    """
    def __init__(self, name):
        """Create a new Service
        """
        self.name = name
        # Create the active endpoints
        self._activeEndpoints = {}      # Key is name, value is ActiveEndpoint object
        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, Endpoint):
                self._activeEndpoints[name] = value.active()

    @property
    def activeEndpoints(self):
        """Get the active endpoints
        """
        return self._activeEndpoints

    def bootup(self, runtime):
        """Bootup this service
        """
        # Create the runtime
        serviceRuntime = ServiceRuntime(self, runtime)
        # Create adapter runtimes
        for adapter in runtime.adapters.itervalues():
            # Find the bootup and shutdown method for this adapter in this service
            bootupMethodName = 'bootup4%s' % adapter.type
            shutdownMethodName = 'shutdown4%s' % adapter.type
            bootupMethod = getattr(self, bootupMethodName) if hasattr(self, bootupMethodName) else None
            shutdownMethod = getattr(self, shutdownMethodName) if hasattr(self, shutdownMethodName) else None
            # Attach the service
            rt = adapter.attach(serviceRuntime)
            rt.serviceShutdown = shutdownMethod
            serviceRuntime.adapters[adapter.name] = rt
            # Boot up the service for the adapter
            if bootupMethod:
                bootupMethod(rt)
        # Done
        return serviceRuntime

    def shutdown(self, serviceRuntime):
        """The shutdown method
        """
        pass

class Endpoint(object):
    """The Endpoint
    Attributes:
        callableObject                  A callable object
        document                        The document of this endpoint
        children                        The child endpoints, usually used in adapters
        callers                         The callers to invoke this endpoints
        configs                         The configs
    """
    def __init__(self, callableObject, document = None, children = None, callers = None, configs = None):
        """Create a new Endpoint
        """
        if callableObject is None:
            raise ValueError('callableObject cannot be None')
        self.callableObject = callableObject
        self.document = document
        self.children = children or {}
        self.callers = callers or []
        self.configs = configs or {}

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
        return Endpoint(self.callableObject.__get__(instance, owner), self.document, self.children, self.callers, self.configs)

    def __call__(self, *args, **kwargs):
        """Call the endpoint
        """
        return self.callableObject(*args, **kwargs)

    def active(self):
        """Get the active endpoint of this endpoint
        Returns:
            ActiveEndpoint object
        """
        if inspect.ismethod(self.callableObject) or inspect.isfunction(self.callableObject):
            signature = self.getSignature(self.callableObject.__name__, self.callableObject)
            document = self.callableObject.__doc__ if not self.document else self.document
            isClass = False
        elif inspect.isclass(self.callableObject):
            signature = self.getSignature(self.callableObject.__name__, self.callableObject.__init__)
            document = self.callableObject.__doc__ if not self.document else self.document
            isClass = True
        elif hasattr(self.callableObject, '__call__'):
            signature = self.getSignature(self.callableObject.__class__.__name__, self.callableObject.__call__)
            document = self.callableObject.__doc__ if not self.document else self.document
            isClass = False
        else:
            raise ValueError('Unsupported callable object [%s] of type [%s]' % (self.callableObject, type(self.callableObject).__name__))
        # Done
        return ActiveEndpoint(self, signature, document, isClass)

    def getSignature(self, name, method):
        """Get the signature of a method
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
        # Get the var args
        if varArgs:
            raise ValueError('Donot support var arguments in endpoint')
        # Check if it is a bound instance method
        if inspect.ismethod(method) and method.im_self:
            # Bound, ignore the first argument, must be self or cls
            args = args[1: ]
        # Done
        return Signature(name if name else method.__name__, ParameterConstraint(args, kwArgs, defaults))

class Signature(object):
    """The Endpoint Signature
    Attributes:
        name                            The method name
        parameter                       The ParameterConstraint object
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
        keywordArgName                  The key word argument name, None if not exist
        defaults                        The default values of argument
    """
    def __init__(self, args, keywordArgName = None, defaults = None):
        """Create a new ParameterConstraint
        """
        self.args = args
        self.keywordArgName = keywordArgName
        self.defaults = defaults or {}

    def __str__(self):
        """Convert to string
        """
        return 'Args {%s} KW NAME {%s} Defaults {%s} Types {%s}' % (
            ','.join(self.args) if self.args else '',
            self.keywordArgName or '',
            ','.join([ '%s:%s' % (x, y) for x, y in self.defaults.iteritems() ]) if self.defaults else '',
            )

    @property
    def isDynamic(self):
        """Check if this parameter constraint support dynamic argument
        """
        return not self.keywordArgName is None
