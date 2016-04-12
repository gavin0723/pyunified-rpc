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
        return mimeType.lower() in self.SUPPORT_MIMETYPES

    def build(self, response, container):
        """Build the content
        Parameters:
            response                            The Response object
            container                           The Container object
        Returns:
            The build value
        """
        raise NotImplementedError
