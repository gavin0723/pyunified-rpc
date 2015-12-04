# encoding=utf8

""" The response object
    Author: lipixun
    Created Time : 三 12/ 2 16:32:06 2015

    File Name: response.py
    Description:

"""

import mime

from werkzeug.wrappers import Response

from util import getContentType

class WebResponse(Response):
    """The web response
    """
    def __init__(self, *args, **kwargs):
        """Create a new WebResponse
        """
        self._mimeType = 'text/plain'
        self._encoding = 'utf-8'
        self._content = None
        self.container = None
        # Super
        Response.__init__(self, *args, **kwargs)

    @property
    def content(self):
        """Get the content
        """
        return self._content

    @content.setter
    def content(self, value):
        """Set the content
        """
        self._content = value
        # Set the response
        if isinstance(value, basestring):
            self.response = (value, )
        else:
            self.response = value

    @property
    def mimeType(self):
        """Get the mime type
        """
        return self._mimeType

    @mimeType.setter
    def mimeType(self, value):
        """Set the mime type
        """
        self._mimeType = value
        self.setContentType(mimeType = value)

    @property
    def encoding(self):
        """Get the encoding
        """
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        """Set the encoding
        """
        self._encoding = value
        self.setContentType(encoding = value)

    def setContentType(self, mimeType = None, encoding = None):
        """Set the content type
        """
        self.content_type = getContentType(mimeType or self._mimeType, encoding or self._encoding)

