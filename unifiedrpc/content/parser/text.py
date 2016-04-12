# encoding=utf8
# The text content parser

"""The text content parser
"""

import logging

from unifiedrpc.errors import BadRequestError

from base import ContentParser

class TextContentParser(ContentParser):
    """The text content parser
    """
    SUPPORT_MIMETYPES = [
        'text/plain',
    ]

    logger = logging.getLogger('unifiedrpc.content.parser.form')

    def parse(self, context):
        """Parse the body from stream
        """
        try:
            return context.request.content.stream.read().decode(context.request.content.encoding)
        except:
            # Failed to decode the content
            self.logger.error('Failed to decode request content')
            # Raise
            raise BadRequestError
