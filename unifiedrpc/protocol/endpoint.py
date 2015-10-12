# encoding=utf8
# The endpoint

"""The endpoint

Endpoint is the one which actually handle the request finally

"""

import types
import inspect

from uuid import uuid4

from collections import OrderedDict

from unifiedrpc.errors import BadRequestParameterError

class Endpoint(object):
    """The Endpoint
    Attributes:
        id                              The unique id of this endpoint, will be automatically set and shouldn't be changed
        callableObject                  A callable object
        signature                       The Signature object
        document                        The document
        children                        The child endpoints, usually used in adapters
    NOTE:
        children
            If endpoint is defined in class, then when using the endpoint as a descriptor, the children will not be copied, that means the:
            - Children list itself
            - The child in the list
            will not be copied, they will be shared among endpoints if the class is instanced many times.
    """
    def __init__(self, callableObject, document = None, children = None, pipeline = None, **configs):
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
        # Set the id
        self.id = str(uuid4())  # Create a unique id, this id will be used for further endpoint tracking and seeking
                                # NOTE: DONOT modify this field
        # Set the children
        self.children = children or {}
        self.pipeline = pipeline or ExecutionPipeline()
        self.configs = configs
        # Add default execution node
        from unifiedrpc.executionnode.parameter import ParameterTypeConversionNode
        self.pipeline.add(ParameterTypeConversionNode(), 1000)

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
        # NOTE:
        #   Here, we donot copy the children, pipeline, configs and other attributes for performance concern
        endpoint = Endpoint(self.callableObject.__get__(instance, owner), self.document, self.children, self.pipeline, **self.configs)
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

    def invoke(self, context):
        """Invoke this endpoint by context
        Parameters:
            context                     The Context object
        Returns:
            The returned value
        """
        params = {}
        # Build the final invoking parameters
        #   - Check the parameters
        #   - Set the default value
        for param, value in context.dispatch.params.iteritems():
            if not param in self.signature.parameter.args and not self.signature.parameter.isDynamic:
                # Unknown parameter error
                raise BadRequestParameterError(param)
            params[param] = value
        for param in self.signature.parameter.args:
            if not param in params:
                # Set the default value
                if param in self.signature.parameter.defaults:
                    params[param] = self.signature.parameter.defaults[param]
                else:
                    # Lack of necessary parameter
                    raise BadRequestParameterError(param)
        # Call the endpoint
        return self(**params)

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
        keywordArg                      The key-word args argument name, None if not exist
        defaults                        The default values of argument
        types                           The type of argument, a dict which key is argument name value is argument type
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

    @property
    def isDynamic(self):
        """Check if this parameter constraint support dynamic argument
        """
        return not self.keywordArg is None

class ExecutionPipeline(object):
    """The ExecutionPipeline
    """
    def __init__(self, nodes = None):
        """Create a new ExecutionPipeline
        """
        self._nodes = nodes or []        # A list of tuple (ExecutionNode, weight), the highest weight, the high priority (Which means will execute first)
        self._sorted = False

    def __call__(self, context):
        """Run the pipeline
        Parameters:
            context                     The Context object
        Returns:
            The returned value
        """
        execContext = ExecutionContext(
            [ node for node in map(lambda x: x[0], self.nodes) if not node.allowedAdapterTypes or context.adapter.type in node.allowedAdapterTypes ],
            context.dispatch.endpoint.invoke,
            context
            )
        return execContext()

    def add(self, node, weight):
        """Add a node
        Parameters:
            node                        The ExecutionNode object
            weight                      The weight
        Returns:
            Nothing
        """
        self._nodes.append((node, weight))
        self._sorted = False

    @property
    def nodes(self):
        """Get all nodes
        NOTE:
            This method will cause all nodes be sorted
        Returns:
            The sorted nodes list which each item is a tuple (node, weight)
        """
        if not self._sorted:
            self._nodes.sort(key = lambda (n, w): w, reverse = True)
            self._sorted = True
        return self._nodes

class ExecutionContext(object):
    """The excution context
    """
    def __init__(self, nodes, final, context):
        """Create a new ExecutionContext
        """
        self.index = -1
        self.nodes = nodes
        self.final = final
        self.context = context

    def __call__(self):
        """Run next node
        """
        self.index += 1
        if self.index >= len(self.nodes):
            # All nodes has been executed
            return self.final(self.context)
        else:
            node = self.nodes[self.index]
            return node(self.context, self)

class ExecutionNode(object):
    """The execution node
    Attributes:
        allowedAdapterTypes             The alloed adapter types, a list of adapter type names, None means all kind of adapters
    """
    allowedAdapterTypes = None

    def __call__(self, context, next):
        """Run the node logic
        Parameters:
            context                     The Context object
            next                        The next method to continue processing, this method has no parameter
        Returns:
            The returned value
        """
        raise NotImplementedError
