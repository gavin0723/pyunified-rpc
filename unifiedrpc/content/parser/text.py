# encoding=utf8
# The text content parser

"""The text content parser
"""

from base import ContentParser

class TextContentParser(ContentParser):
    """The text content parser
    """
    SUPPORT_MIMETYPES = [
        'text/plain',
    ]

    def parse(self, context):
        """Parse the body from stream
        """
        return context.request.content.stream.read().decode(context.request.content.encoding)
