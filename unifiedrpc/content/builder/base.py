# encoding=utf8
# The base content buidler

"""The base content builder
"""

class ContentBuilder(object):
    """The ContentBuilder
    """
    def isSupportMimeType(self, mimeType):
        """Check if the current content builder could support the specified mimeType
        """
        raise NotImplementedError

    def build(self, context):
        """Build the content
        NOTE:
            This method should set the context properly
        Parameters:
            context                         The Context object
        Returns:
            Nothing
        """
        raise NotImplementedError

    def applyHeaderResponse(self, headers, context):
        """Apply header response
        """
        for header, value in headers.iteritems():
            context.headers[header] = value

    def encodeHeaderValue(self, value):
        """Encode the header value
        """
        raise NotImplementedError
