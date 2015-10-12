# encoding=utf8
# The response

"""The response
"""

class Response(object):
    """The response class
    """
    def __init__(self, status = None, headers = None, content = None, mimeType = None, encoding = None, container = None):
        """Create a new Response
        """
        self.status = status
        self.headers = headers or {}
        self.content = content
        self.mimeType = mimeType
        self.encoding = encoding
        self.container = container
