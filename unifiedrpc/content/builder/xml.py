# encoding=utf8
# The xml content builder

"""The xml content builder
"""

import mime

from unifiedrpc.util import ET

from base import ContentBuilder

class XmlContentBuilder(ContentBuilder):
    """The TextContentBuilder
    """
    SUPPORT_MIMETYPES = [
        mime.APPLICATION_XML,
    ]

    def isSupportMimeType(self, mimeType):
        """Check if the current content builder could support the specified mimeType
        """
        return mimeType.lower() in self.SUPPORT_MIMETYPES

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

