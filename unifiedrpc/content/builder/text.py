# encoding=utf8
# The text content builder

"""The text content builder
"""

import types

import mime

from base import ContentBuilder

class TextContentBuilder(ContentBuilder):
    """The TextContentBuilder
    """
    SUPPORT_MIMETYPES = [
        'text/plain',
        mime.APPLICATION_XHTML_XML,
        mime.TEXT_HTML,
        mime.TEXT_MARKDOWN,
    ]

    def isSupportMimeType(self, mimeType):
        """Check if the current content builder could support the specified mimeType
        """
        return mimeType.lower() in self.SUPPORT_MIMETYPES

    def build(self, context):
        """Build the content
        Parameters:
            context                         The Context object
        Returns:
            The build value
        """
        if context.response.container:
            # Good, get the value and headers
            value, headers = context.response.container.dump()
            if headers:
                self.applyHeaderResponse(headers, context)
            if isinstance(value, str):
                return value
            elif isinstance(value, unicode):
                if not context.response.encoding:
                    raise ValueError('Require response encoding')
                return value.encode(context.response.encoding)
            elif value is None:
                return ''
            elif isinstance(value, types.GeneratorType):
                return StreamTextContentWrapper(value, context.response.encoding)
            else:
                return str(value)

class StreamTextContentWrapper(object):
    """The stream text content wrapper
    """
    def __init__(self, iterator, encoding):
        """Create a new StreamTextContentWrapper
        """
        self.iterator = iterator
        self.encoding = encoding
        # We have to call next once in order to let the endpoint handler execute
        self._firstValue = self.iterator.next()

    def __iter__(self):
        """Iterate content
        """
        yield self._firstValue
        # Continue yield
        for content in self.iterator:
            # Check the content type
            if isinstance(content, str):
                yield content
            elif isinstance(value, unicode):
                if not self.encoding:
                    raise ValueError('Require response encoding')
                yield content.encode(self.encoding)
            elif content is None:
                yield ''
            else:
                yield str(content)

