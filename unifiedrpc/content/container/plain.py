# encoding=utf8
# The plain content container

"""The plain content container
"""

from base import ContentContainer

class PlainContentContainer(ContentContainer):
    """The plain content container
    This container will return value directly as response content and use headers to return meta data (include error)
    """
    KEY_META_ERROR      = 'X-SERVER-ERROR'

    def __init__(self):
        """Create a new PlainContentContainer
        """
        self._value = None
        self._headers = {}

    def getValue(self):
        """Get the value
        """
        return self._value

    def setValue(self, value):
        """Set the value
        """
        self._value = value

    def cleanValue(self):
        """Clean the value
        """
        self._value = None

    def getError(self):
        """Get the error
        """
        return self._headers.get(self.KEY_META_ERROR)

    def setError(self, code, reason, detail = None):
        """Set the error
        """
        self._headers[self.KEY_META_ERROR] = { 'code': code, 'reason': reason, 'detail': detail }

    def cleanError(self):
        """Clean the error
        """
        if self.KEY_META_ERROR in self._headers:
            del self._headers[self.KEY_META_ERROR]

    def getMeta(self, key):
        """Get the meta
        """
        return self._headers.get('X-SERVER-' + key.upper())

    def setMeta(self, key, value):
        """Set the meta
        """
        self._headers['X-SERVER-' + key.upper()] = value

    def deleteMeta(self, key):
        """Delete the meta
        """
        key = 'X-SERVER-' + key.upper()
        if key in self._headers:
            del self._headers[key]

    def cleanMeta(self):
        """Clean all meta
        """
        self._headers = {}

    def dump(self):
        """Dump the content of this container
        Returns:
            A tuple (value object, header dict which key is string value is an object)
        """
        return (self._value or tuple(), self._headers)
