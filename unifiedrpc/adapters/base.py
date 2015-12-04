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
        self.server = None
        self.configs = configs

    @property
    def started(self):
        """Tell if this adapter is started or not
        """
        raise NotImplementedError

    def addService(self, service):
        """Add a service
        """
        raise NotImplementedError

    def removeService(self, service):
        """Remove a service
        """
        raise NotImplementedError

    def cleanServices(self, services):
        """Clean all service
        """
        raise NotImplementedError

    def startAsync(self):
        """Start asynchronously
        """
        raise NotImplementedError

    def close(self):
        """Close current adapter
        Returns:
            Nothing
        """
        raise NotImplementedError
