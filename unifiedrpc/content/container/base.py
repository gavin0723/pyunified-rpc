# encoding=utf8
# The base content container

"""The base content container
"""

class ContentContainer(object):
    """The ContentContainer
    """
    def getValue(self):
        """Get the value
        """
        raise NotImplementedError

    def setValue(self, value):
        """Set the value
        Parameters:
            value                   The EndpointExecutionResult object
        """
        raise NotImplementedError

    def cleanValue(self):
        """Clean the value
        """
        raise NotImplementedError

    def getError(self):
        """Get the error
        """
        raise NotImplementedError

    def setRPCError(self, error):
        """Set the rpc error
        """
        self.setError(error.code, error.reason, error.detail)

    def setError(self, code, reason, detail = None):
        """Set the error
        """
        raise NotImplementedError

    def cleanError(self):
        """Clean the error
        """
        raise NotImplementedError

    def getMeta(self, key):
        """Get the meta
        """
        raise NotImplementedError

    def setMeta(self, key, value):
        """Set the meta
        """
        raise NotImplementedError

    def deleteMeta(self, key):
        """Delete the meta
        """
        raise NotImplementedError

    def cleanMeta(self):
        """Clean all meta
        """
        raise NotImplementedError

    def dump(self):
        """Dump the content of this container
        Returns:
            A tuple (an iterable object, header dict which key is string value is an object)
        """
        raise NotImplementedError
