# encoding=utf8
# The text content builder

"""The text content builder
"""

import mime

from base import ContentBuilder

class TextContentBuilder(ContentBuilder):
    """The TextContentBuilder
    """
    SUPPORT_MIMETYPES = [
        'text/plain',
        mime.APPLICATION_XHTML_XML,
        mime.TEXT_HTML,
        mime.TEXT_JAVASCRIPT,
        mime.TEXT_MARKDOWN,
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
        if context.response.container:
            # Good, get the value and headers
            value, headers = context.response.container.dump()
            if headers:
                self.applyHeaderResponse(headers)
            if isinstance(value, str):
                context.response.content = value
            elif isinstance(value, unicode):
                if not context.response.encoding:
                    raise ValueError('Require response encoding')
                context.response.content = value.encode(context.response.encoding)
            else:
                context.response.content = str(value)
