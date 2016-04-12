# encoding=utf8

""" The runtime of protocol
    Author: lipixun
    Created Time : 一  1/18 16:01:27 2016

    File Name: runtime.py
    Description:

"""

import logging

from threading import Event, Lock

from unifiedrpc.errors import BadRequestParameterError, ERRCODE_BADREQUEST_UNKNOWN_PARAMETER, ERRCODE_BADREQUEST_LACK_OF_PARAMETER

from probe import ProbeFrame, PROBE_LOCATION_BEFORE_REQUEST, PROBE_LOCATION_AFTER_REQUEST, PROBE_LOCATION_AFTER_RESPONSE

class Runtime(object):
    """Represents a server runtime
    """
    GLOCK   = Lock()

    logger = logging.getLogger('unifiedrpc.protocol.runtime')

    def __init__(self, server, services, adapters, **configs):
        """Create a new Runtime
        """
        self.server = server
        self.services = services
        self.adapters = adapters
        self.configs = configs
        self.probe = ProbeFrame()
        # Runtimes
        self._serviceRuntimes = None
        # Create stateful parameters
        self._started = False
        self._closed = True
        self._closedEvent = Event()

    @property
    def started(self):
        """Get if the runtime is started
        """
        return self._started

    @property
    def closed(self):
        """Get if the runtime is closed
        """
        return self._closed

    def start(self):
        """Start this runtime
        """
        self.startAsync()
        # Wait forever
        self.wait()

    def startAsync(self):
        """Start this runtime asynchronously
        """
        with self.GLOCK:
            # Check flag
            if self._started:
                raise ValueError('The runtime is already started')
            if not self.services:
                raise ValueError('Require services')
            if not self.adapters:
                raise ValueError('Require adapters')
            # Initialize the parameters
            self._started = True
            self._closed = False
            self._serviceRuntimes = {}
            self._closedEvent.clear()
            # Boot up services
            self.logger.info('Boot up services')
            for service in self.services.itervalues():
                self.logger.info('Start service [%s]', service.name)
                serviceRuntime = service.bootup(self)
                if not serviceRuntime:
                    raise ValueError('Require service runtime after boot up service [%s]' % service.name)
                self._serviceRuntimes[service.id] = serviceRuntime
            # Start all adapters
            self.logger.info('Boot up adapters')
            for adapter in self.adapters.itervalues():
                self.logger.info('Start adapter [%s]', adapter.name)
                adapter.startAsync(self)
            # Done
            self.logger.info('Runtime completely started')

    def wait(self):
        """Wait for this runtime to complete
        """
        self._closedEvent.wait()

    def shutdown(self):
        """Shutdown this runtime
        """
        # Shutdown all services
        if self._serviceRuntimes:
            for serviceRuntime in self._serviceRuntimes.itervalues():
                try:
                    self.logger.info('Shutdown service [%s]', serviceRuntime.service.name)
                    serviceRuntime.shutdown()
                except:
                    self.logger.exception('Failed to shutdown service [%s], skip', serviceRuntime.service.name)
            # Shutdown all adapters
            for adapter in self.adapters.itervalues():
                try:
                    self.logger.info('Shutdown adapter [%s]', adapter.name)
                    adapter.shutdown()
                except:
                    self.logger.exception('Failed to shutdown adapter [%s], skip', adapter.name)
        # Done
        self._started = False
        self._closed = True
        self._serviceRuntimes = None
        self._closedEvent.set()

    # The helper methods
    def invokeBeforeRequest(self, method):
        """Add a probe before request
        """
        self.probe.add(PROBE_LOCATION_BEFORE_REQUEST, method)

    def invokeAfterRequest(self, method):
        """Add a probe after request
        """
        self.probe.add(PROBE_LOCATION_AFTER_REQUEST, method)

    def invokeAfterResponse(self, method):
        """Add a probe after response
        """
        self.probe.add(PROBE_LOCATION_AFTER_RESPONSE, method)

class ServiceRuntime(object):
    """Represents a service runtime
    """
    def __init__(self, service, runtime, adapters = None):
        """Create a new ServiceRuntime
        """
        self.service = service
        self.runtime = runtime
        self.adapters = adapters or {}

    def shutdown(self):
        """Shutdown the whole service
        """
        # Shutdown all service adapter runtime
        for rt in self.adapters.itervalues():
            rt.shutdown()
        # Call the service shutdown
        self.service.shutdown(self)

class ServiceAdapterRuntime(object):
    """Represents a server runtime for a specified adapter
    """
    def __init__(self, adapter, serviceRuntime, serviceShutdown = None):
        """Create a new ServiceAdapterRuntime
        """
        self.adapter = adapter
        self.serviceRuntime = serviceRuntime
        self.serviceShutdown = serviceShutdown  # The shutdown method of the service to shutdown for the adapter

    def shutdown(self):
        """Shutdown this service adapter
        """
        if self.serviceShutdown:
            self.serviceShutdown(self)

class ActiveEndpoint(object):
    """Represents a active endpoint
    """
    def __init__(self, endpoint, signature, document = None, isClass = False):
        """Create a new ActiveEndpoint
        """
        self.endpoint = endpoint
        self.signature = signature
        self.document = document
        self.isClass = isClass

    @property
    def configs(self):
        """Get the configs
        """
        return self.endpoint.configs

    @property
    def children(self):
        """Get the children
        """
        return self.endpoint.children

    def __call__(self, context, additionalCallers = None):
        """Invoke this endpoint by context
        Parameters:
            context                     The Context object
        Returns:
            The returned value
        """
        from unifiedrpc.caller import ParameterTypeConversionCaller
        # Build the caller stack
        callers = list(self.endpoint.callers) if self.endpoint.callers else []
        if additionalCallers:
            callers.extend(additionalCallers)
        callers.append((ParameterTypeConversionCaller(), 1000))
        callStack = CallStack(callers, self.invoke, context)
        # Run it
        return callStack()

    def invoke(self, context):
        """Invoke the endpoint
        """
        params = {}
        # Build the final invoking parameters
        #   - Check the parameters
        #   - Set the default value
        for param, value in context.params.iteritems():
            if not param in self.signature.parameter.args and not self.signature.parameter.isDynamic:
                # Unknown parameter error
                raise BadRequestParameterError(param, ERRCODE_BADREQUEST_UNKNOWN_PARAMETER, 'Parameter [%s] is unknown via current endpoint' % param)
            params[param] = value
        for param in self.signature.parameter.args:
            if not param in params:
                # Set the default value
                if param in self.signature.parameter.defaults:
                    params[param] = self.signature.parameter.defaults[param]
                else:
                    # Lack of necessary parameter
                    raise BadRequestParameterError(param, ERRCODE_BADREQUEST_LACK_OF_PARAMETER, 'Missing necessary parameter [%s] via current endpoint' % param)
        # Call the endpoint
        return self.endpoint(**params)
