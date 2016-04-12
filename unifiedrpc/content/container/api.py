# encoding=utf8
# The API content container

""" The API content container
    Author: lipixun
    Created Time : 四  4/ 7 14:52:32 2016

    File Name: api.py
    Description:

        The result format:
        {
            value:
            error:
        }

        If the return value is empty, then value = None
        If the return value is a single value, then value = value
        If the return value is not a single value, then value = list of value
"""

from base import ContentContainer

class APIContentContainer(ContentContainer):
    """The api content container
    This container will return all data by response content
    """
    KEY_VALUE           = 'value'
    KEY_META_ERROR      = 'error'

    def __init__(self):
        """Create a new APIContentContainer
        """
        self._object = {}

    def getValue(self):
        """Get the value
        """
        return self._object.get(self.KEY_VALUE)

    def setValue(self, value):
        """Set the value
        """
        if value.isSingle:
            value = list(value)
            if len(value) == 0:
                value = None
            else:
                value = value[0]
        else:
            value = list(value)
        # Set to json dict
        self._object[self.KEY_VALUE] = value

    def cleanValue(self):
        """Clean the value
        """
        if self.KEY_VALUE in self._object:
            del self._object[self.KEY_VALUE]

    def getError(self):
        """Get the error
        """
        return self._object.get(self.KEY_META_ERROR)

    def setError(self, code = None, reason = None, detail = None):
        """Set the error
        """
        self._object[self.KEY_META_ERROR] = { 'code': code, 'reason': reason, 'detail': detail }

    def cleanError(self):
        """Clean the error
        """
        if self.KEY_META_ERROR in self._object:
            del self._object[self.KEY_META_ERROR]

    def getMeta(self, key):
        """Get the meta
        """
        return self._object.get(key)

    def setMeta(self, key, value):
        """Set the meta
        """
        self._object[key] = value

    def deleteMeta(self, key):
        """Delete the meta
        """
        if key in self._object:
            del self._object[key]

    def cleanMeta(self):
        """Clean all meta
        """
        if self.KEY_VALUE in self._object:
            self._object = { self.KEY_VALUE: self._object[self.KEY_VALUE] }
        else:
            self._object = {}

    def dump(self):
        """Dump the content of this container
        Returns:
            A tuple (value object, header dict which key is string value is an object)
        """
        return ((self._object, ), None)
