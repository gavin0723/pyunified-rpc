# encoding=utf8

""" The service
    Author: lipixun
    Created Time : 日  4/ 3 00:05:45 2016

    File Name: service.py
    Description:

"""

from uuid import uuid4

from handler import StartupHandler, ShutdownHandler
from endpoint import Endpoint
from execution import EndpointExecutionStage

ENDPOINTS_NAME  = '__pyunified_rpc_service_endpoints__'
STARTUPS_NAME   = '__pyunified_rpc_service_startups__'
SHUTDOWNS_NAME  = '__pyunified_rpc_service_shutdowns__'

class ServiceMetaClass(type):
    """The service meta class
    """
    def __new__(cls, name, bases, attrs):
        """Create a new Service class
        """
        endpoints = {}      # Name 2 Endpoint
        startups = {}       # Type 2 StartupHandler
        shutdowns = {}      # Type 2 ShutdownHandler
        # Check the base classes
        for base in bases:
            if hasattr(base, ENDPOINTS_NAME):
                endpoints.update(getattr(base, ENDPOINTS_NAME))
            if hasattr(base, STARTUPS_NAME):
                startups.update(getattr(base, STARTUPS_NAME))
            if hasattr(base, SHUTDOWNS_NAME):
                shutdowns.update(getattr(base, SHUTDOWNS_NAME))
        # Check the attributes
        for key, value in attrs.iteritems():
            if isinstance(value, Endpoint):
                endpoints[key] = value
            elif isinstance(value, StartupHandler):
                for _type in value.types:
                    startups[_type] = value
            elif isinstance(value, ShutdownHandler):
                for _type in value.types:
                    shutdowns[_type] = value
        # Add endpoints to attrs
        attrs[ENDPOINTS_NAME] = endpoints
        attrs[STARTUPS_NAME] = startups
        attrs[SHUTDOWNS_NAME] = shutdowns
        # Super
        return type.__new__(cls, name, bases, attrs)

class Service(object):
    """The service
    Attributes:
        name                    The service name
        endpoints               The endpoints of this service
    """
    __metaclass__ = ServiceMetaClass

    def __init__(self, name = None, endpoints = None, configs = None, stage = None):
        """Create a new Service
        """
        self._name = name or type(self).__name__
        # Set configs and stage
        self._configs = configs or {}
        self._stage = stage or EndpointExecutionStage()
        # Create the endpoints of this instance
        self._endpoints = {}
        # Get from class
        clsEndpoints = getattr(self, ENDPOINTS_NAME)
        if clsEndpoints:
            self._endpoints.update(map(lambda (k, v): (k, v.bind(self)), clsEndpoints.iteritems()))
        # Update endpoints
        if endpoints:
            self._endpoints.update(map(lambda (k, v): (k, v.bind(self)), endpoints.iteritems()))

    @property
    def name(self):
        """The name of this service
        """
        return self._name

    @property
    def endpoints(self):
        """Get the active endpoints
        """
        return self._endpoints

    @property
    def startups(self):
        """Get the startup handlers
        """
        return getattr(self, STARTUPS_NAME)

    @property
    def shutdowns(self):
        """Get the shutdown handlers
        """
        return getattr(self, SHUTDOWNS_NAME)
