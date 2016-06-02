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

    def build(self, response, values):
        """Build the content
        """
        for value in values:
            if isinstance(value, str):
                yield value
            elif isinstance(value, unicode):
                yield value.encode(response.encoding)
            elif isinstance(value, file):
                # Read the file
                while True:
                    try:
                        buffer = value.read(4096)
                        if not buffer:
                            break
                        yield buffer
                    except EOFError:
                        break
            else:
                raise ValueError('Unsupported value type [%s] for text content builder' % type(value).__name__)
