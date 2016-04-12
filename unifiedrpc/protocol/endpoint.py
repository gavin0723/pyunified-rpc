# encoding=utf8

""" The endpoint
    Author: lipixun
    Created Time : 四  4/ 7 13:43:59 2016

    File Name: endpoint.py
    Description:

"""

import logging
import inspect

from context import context

from handler import Handler
from execution import EndpointExecutionStage
from callabletypes import CallableObject

class Endpoint(object):
    """The Endpoint
    Attributes:
        _executor                       The executor of this endpoint
        _document                       The document of this endpoint
        _callers                        The callers to invoke this endpoints
        children                        The child endpoints, usually used in adapters
        configs                         The configs
        bindObject                      The bound object if the endpoint is defined in the class context
    """
    def __init__(self, executor = None, document = None, children = None, configs = None, stage = None, bindObject = None):
        """Create a new Endpoint
        """
        self._executor = CallableObject.create(executor) if executor else None
        self._document = document
        self._bindObject = bindObject
        # The execution stage
        self._stage = stage or self.__initstage__()
        # The children and configs
        self._children = children or {}
        self._configs = configs or {}

    def __getattr__(self, key):
        """Get the attribute, transparently access attribute of executor
        """
        return getattr(self._executor.obj, key)

    def __call__(self, *args, **kwargs):
        """Call the endpoint executor
        """
        return self._executor.getCallable(self._bindObject)(*args, **kwargs)

    def __initstage__(self):
        """Initialize a new stage
        """
        stage = EndpointExecutionStage()
        # Add the default stage
        from unifiedrpc.stages import ParameterConverter
        stage.addCaller(ParameterConverter())
        # Done
        return stage

    @property
    def children(self):
        """Get the children
        """
        return self._children

    @property
    def bound(self):
        """Tell if this endpoint is bounded
        """
        return not self._bindObject is None

    def getConfig(self, key):
        """Get the config
        """
        return self._configs.get(key)

    def setConfig(self, key, value):
        """Set the config
        """
        self._configs[key] = value

    def bind(self, obj):
        """Bind this endpoint to a specified object
        Parameters:
            obj                             The class to bound
        Returns:
            The endpoint object
        NOTE:
            This method will create a *NEW* endpoint class. The children / callers and handlers will be cloned.
        """
        return Endpoint(
            executor = self._executor.obj,
            document = self._document,
            children = dict(self._children),
            configs = dict(self._configs),
            stage = self._stage.clone(),
            bindObject = obj,
            )

    def executor(self, method):
        """Set the executor of this endpoint
        """
        if not method:
            raise ValueError('Invalid method')
        self._executor = CallableObject.create(method)

    def prerequest(self, *args, **kwargs):
        """Add a prerequest method
        """
        return self._stage.prerequest(*args, **kwargs)

    def postrequest(self, method):
        """Add a postrequest method
        """
        return self._stage.postrequest(*args, **kwargs)

    def caller(self, method):
        """Add a caller method
        """
        return self._stage.caller(*args, **kwargs)

    def onerror(self, method):
        """Add a onerror method
        """
        return self._stage.onerror(*args, **kwargs)

    def finalize(self, method):
        """Add a finalize method
        """
        return self._stage.finalize(*args, **kwargs)

    def getSignature(self):
        """Get the signature of this endpoint (The signature of executor)
        """
        return self._executor.bind(self._bindObject).getSignature()
