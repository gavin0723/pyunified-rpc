# encoding=utf8
# The base content parser

"""The base content parser
"""

class ContentParser(object):
    """The content parser
    """
    def isSupportMimeType(self, mimeType):
        """Check if the current content parser could support the specified mimeType
        """
        return mimeType.lower() in self.SUPPORT_MIMETYPES

    def parse(self, request):
        """Parse the body from stream
        Parameters:
            body                        The protocol.request.Body object
            stream                      The stream - like object
        Returns:
            The parsed content
        """
        raise NotImplementedError
