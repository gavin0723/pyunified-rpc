# encoding=utf8

""" The execution
    Author: lipixun
    Created Time : 四  4/ 7 17:36:11 2016

    File Name: execution.py
    Description:

"""

import types
import logging

from unifiedrpc.errors import *

from context import context
from handler import Handler

class ExecutionContext(object):
    """The execution context
    NOTE:
        This class simplify the configs, stages accross scopes (Server, Adapter, Service, Endpoint)
        All these objects have the following attributs:
            - _configs          A dict
            - _stage            A EndpointExecutionStage object
    """
    def __init__(self, server, adapter = None, service = None, endpoint = None):
        """Create a new ExecutionContext
        """
        self.server = server
        self.adapter = adapter
        self.service = service
        self.endpoint = endpoint

    def getConfig(self, key):
        """Get config
        """
        if self.endpoint and self.endpoint._configs and key in self.endpoint._configs:
            return self.endpoint._configs[key]
        elif self.service and self.service._configs and key in self.service._configs:
            return self.service._configs[key]
        elif self.adapter and self.adapter._configs and key in self.adapter._configs:
            return self.adapter._configs[key]
        elif self.server and self.server._configs and key in self.server._configs:
            return self.server._configs[key]

    def getEndpointExecutionContext(self):
        """Get endpoint execution context
        """
        stages = []
        # Collect stages
        if self.endpoint:
            stages.append((self.endpoint._stage, self.endpoint.bound))
        if self.server:
            stages.append((self.server._stage, self.server))
        if self.adapter:
            stages.append((self.adapter._stage, self.adapter))
        if self.service:
            stages.append((self.service._stage, self.service))
        # Done
        return EndpointExecutionContext(stages, self.endpoint)

class EndpointExecutionStage(object):
    """The endpoint execution stages
    The method signature of each stages:
        prerequest                  ()
        postrequest                 ()
        calling                     (params, next)
        onerror                     (error)
        finalizing                  ()
    """
    def __init__(self, prerequest = None, postrequest = None, calling = None, onerror = None, finalizing = None):
        """Create a new EndpointExecutionStage
        """
        self._prerequest = prerequest or []
        self._postrequest = postrequest or []
        self._calling = calling or []
        self._onerror = onerror or []
        self._finalizing = finalizing or []

    def clone(self):
        """Clone this stages
        """
        return EndpointExecutionStage(
            prerequest = list(self._prerequest),
            postrequest = list(self._postrequest),
            calling = list(self._calling),
            onerror = list(self._onerror),
            finalizing = list(self._finalizing)
            )

    def addPreRequest(self, method, weight = None):
        """Add a pre-request method
        """
        if not method:
            raise ValueError('Invalid method')
        self._prerequest.append(Handler(method, weight))

    def addPostRequest(self, method, weight = None):
        """Add a post-request method
        """
        if not method:
            raise ValueError('Invalid method')
        self._postrequest.append(Handler(method, weight))

    def addCaller(self, method, weight = None):
        """Add a caller method
        """
        if not method:
            raise ValueError('Invalid method')
        self._calling.append(Handler(method, weight))

    def addErrorHandler(self, method, weight = None):
        """Add a onerror method
        """
        if not method:
            raise ValueError('Invalid method')
        self._onerror.append(Handler(method, weight))

    def addFinalizer(self, method, weight = None):
        """Add a finalize method
        """
        if not method:
            raise ValueError('Invalid method')
        self._finalizing.append(Handler(method, weight))

    # -*- ---------- The decorators ---------- -*-

    def prerequest(self, weight = None):
        """Pre-request decorator
        """
        def decorator(method):
            """The decorator
            """
            self.addPreRequest(method, weight)
        # Done
        return decorator

    def postrequest(self, method):
        """Post-request decorator
        """
        def decorator(method):
            """The decorator
            """
            self.addPreRequest(method, weight)
        # Done
        return decorator

    def caller(self, method):
        """Caller decorator
        """
        def decorator(method):
            """The decorator
            """
            self.addPreRequest(method, weight)
        # Done
        return decorator

    def onerror(self, method):
        """Error handler decorator
        """
        def decorator(method):
            """The decorator
            """
            self.addPreRequest(method, weight)
        # Done
        return decorator

    def finalize(self, method):
        """Finalizer decorator
        """
        def decorator(method):
            """The decorator
            """
            self.addPreRequest(method, weight)
        # Done
        return decorator

class EndpointExecutionContext(object):
    """The endpoint execution context
    """
    logger = logging.getLogger('unifiedrpc.protocol.endpoint.executionContext')

    def __init__(self, stages, endpoint):
        """Create a new EndpointExecutionContext
        Parameters:
            stages                          A list of tuple (EndpointExecutionStage, Bound Object)
            endpoint                        The endpoint object
        """
        self.stages = stages
        self.endpoint = endpoint

    def __call__(self):
        """Call this execution context
        """
        # Pre-request
        #   This stages will be executed firstly, if any error happend, on error will be called
        # Calling
        #   This stage will be executed after pre-request, the endpoint will be called at the end of this pipeline
        # Post-request
        #   This stage will be executed after the calling stage
        # On-error
        #   This stage will be called when any error occurred when executing the above three stages
        # Finialize
        #   This stage will be called after the underlying uwsgi server has already completed the request
        #   (After the whole content is responed and before the connection is closed)
        #   NOTE:
        #       - This stage will not be executed by this context (But the responsible of the adapter)
        #       - This stage will be executed even if error happend

        # The pre-request stage
        try:
            handlers = self.mergeHandlers(lambda x: x._prerequest, self.stages)
            for handler, bound in handlers:
                res = handler(bound)
                if not res is None:
                    # Stop handle
                    context.response.content.executionResult = createResponseResult(res)
                    break
        except Exception as error:
            # Only log error when debugging
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.exception('Error occurred when executing pre-request stage')
            # Call the on error
            if not self.handleError(error):
                raise
            # Done
            return

        # The calling stage
        if context.response.content.executionResult is None:
            try:
                if not self.endpoint:
                    raise NotFoundError
                handlers = self.mergeHandlers(lambda x: x._calling, self.stages)
                callStack = CallStack([ x.getCallable(y) for (x, y) in handlers ] + [ self.__callendpoint__ ])
                # Call the endpoint and create the execution result
                context.response.content.executionResult = createResponseResult(callStack())
            except Exception as error:
                # Only log error when debugging
                if not isinstance(error, RPCError):
                    self.logger.exception('Error occurred when executing calling stage')
                # Call the on error
                if not self.handleError(error):
                    raise
                # Done
                return

        # The post-request stage
        try:
            handlers = self.mergeHandlers(lambda x: x._postrequest, self.stages)
            for handler, bound in handlers:
                handler(bound)
        except Exception as error:
            # Only log error when debugging
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.exception('Error occurred when executing post-request stage')
            # Call the on error
            if not self.handleError(error):
                raise
            # Done
            return

    def __callendpoint__(self, next):
        """Call endpoint
        """
        params = context.dispatchResult.parameters
        signature = self.endpoint.getSignature()
        # Check parameters
        for param, value in params.iteritems():
            if not param in signature.parameter.args and not signature.parameter.isDynamic:
                # Unknown parameter error
                raise BadRequestParameterError(param, ERRCODE_BADREQUEST_UNKNOWN_PARAMETER, 'Parameter [%s] is unknown via current endpoint' % param)
            params[param] = value
        for param in signature.parameter.args:
            if not param in params:
                # Set the default value
                if param in signature.parameter.defaults:
                    params[param] = signature.parameter.defaults[param]
                else:
                    # Lack of necessary parameter
                    raise BadRequestParameterError(param, ERRCODE_BADREQUEST_LACK_OF_PARAMETER, 'Missing necessary parameter [%s] via current endpoint' % param)
        # Call endpoint
        return self.endpoint(**params)

    def finalize(self):
        """Run the finalize stage
        """
        handlers = self.mergeHandlers(lambda x: x._finalizing, self.stages)
        for handler, bound in handlers:
            handler(bound)

    def handleError(self, error):
        """Handle error
        """
        handled = False
        handlers = self.mergeHandlers(lambda x: x._onerror, self.stages)
        for handler, bound in handlers:
            handled = handler.callableObject.getCallable(bound)(error, handled)
        # Done
        return handled

    def mergeHandlers(self, func, stages):
        """Merge and sort the handlers
        Returns:
            A list of (handler, bound)
        """
        handlers = []
        for stage, bound in stages:
            _handlers = func(stage)
            for handler in _handlers:
                handlers.append((handler, bound))
        handlers.sort(key = lambda x: x[0].weight or 0, reverse = True)
        # Done
        return handlers

class EndpointExecutionResult(object):
    """The endpoint execution result wrapper
    This class is used to wrap the result of the endpoint execution handler in order to handle:
        - Generator
        - None iterable result
    """
    def __init__(self, result, isSingle = True):
        """Create a new EndpointExecutionResult
        """
        self._result = result
        self._isSingle = isSingle

    def __iter__(self):
        """Iterate the result
        """
        raise NotImplementedError

    @property
    def isSingle(self):
        """Get if the result is a single result
        """
        return self._isSingle

    @property
    def type(self):
        """Get the result type
        """
        return type(self._result)

    @classmethod
    def create(cls, result):
        """Create a result
        """
        if isinstance(result, types.GeneratorType):
            # Call this generator until the first value is returned
            try:
                first = result.next()
                return GeneratorEndpointExecutionResult(first, result)
            except StopIteration:
                # No value is returned
                return EmptyEndpointExecutionResult(result)
        elif isinstance(result, (list, tuple)):
            # A normal return result
            return IterableEndpointExecutionResult(result)
        else:
            # A single value result
            if result is None:
                return EmptyEndpointExecutionResult(result)
            else:
                return SingleValueEndpointExecutionResult(result)

class EmptyEndpointExecutionResult(EndpointExecutionResult):
    """The empty endpoint execution result
    """
    def __iter__(self):
        """Iterate an empty result
        """
        return
        yield

class GeneratorEndpointExecutionResult(EndpointExecutionResult):
    """The generator endpoint execution result
    """
    def __init__(self, first, result):
        """Create a new GeneratorEndpointExecutionResult
        """
        self._first = first
        # Super
        super(GeneratorEndpointExecutionResult, self).__init__(result, False)

    def __iter__(self):
        """Iterate an empty result
        """
        yield self._first
        try:
            for value in self._result:
                yield value
        except StopIteration:
            pass

class IterableEndpointExecutionResult(EndpointExecutionResult):
    """The iterable endpoint execution result
    """
    def __init__(self, result):
        """Create a new IterableEndpointExecutionResult
        """
        super(IterableEndpointExecutionResult, self).__init__(result, False)

    def __iter__(self):
        """Iterate the result
        """
        try:
            for value in self._result:
                yield value
        except StopIteration:
            pass

class SingleValueEndpointExecutionResult(EndpointExecutionResult):
    """The single value endpoint execution result
    """
    def __iter__(self):
        """Return the single result
        """
        yield self._result

class CallStack(object):
    """The CallStack
    """
    def __init__(self, handlers):
        """Create a new CallStack
        """
        self.handlers = handlers
        self.index = -1

    def __call__(self):
        """Run the pipeline
        Parameters:
            context                     The Context object
        Returns:
            The returned value
        """
        self.index += 1
        if self.index < len(self.handlers):
            return self.handlers[self.index](self)

def createResponseResult(result):
    """Create the response result
    """
    return EndpointExecutionResult.create(result)
