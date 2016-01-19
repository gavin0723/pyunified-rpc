# encoding=utf8
# The base adapter definitions

"""The base adapter definitions
"""

class Adapter(object):
    """The adapter base class
    Attributes:
        name                            The adapter name. Each adapter should have a unique name
    """
    def __init__(self, name, **configs):
        """Create a new AdapterBase
        """
        self.name = name
        self.configs = configs
        self._started = False
        self._closed = True

    @property
    def started(self):
        """Get if the adapter is started
        """
        return self._started

    @property
    def closed(self):
        """Get if the adapter is closed
        """
        return self._closed

    def getStatus(self):
        """Get the adapter status
        Returns:
            A json serializable dict
        """
        raise NotImplementedError

    def startAsync(self, runtime):
        """Start asynchronously
        """
        raise NotImplementedError

    def shutdown(self):
        """Shutdown the adapter
        Returns:
            Nothing
        """
        raise NotImplementedError

    def attach(self, serviceRuntime):
        """Attach a service
        Returns:
            ServiceAdapterRuntime
        """
        raise NotImplementedError
