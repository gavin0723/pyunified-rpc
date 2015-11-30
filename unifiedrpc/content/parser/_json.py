# encoding=utf8
# The json content parser

"""The json content parser
"""

import logging

import mime

from unifiedrpc.util import json, JSONDecodeError
from unifiedrpc.errors import BadRequestBodyError

from base import ContentParser

class JsonContentParser(ContentParser):
    """The JsonContentParser
    """
    SUPPORT_MIMETYPES = [
        mime.APPLICATION_JSON,
    ]

    logger = logging.getLogger('unifiedrpc.content.parser.json')

    def parse(self, context):
        """Parse the request content
        """
        try:
            return json.load(context.request.content.stream, encoding = context.request.content.encoding)
        except JSONDecodeError:
            # Failed to decode the content
            self.logger.error('Failed to decode request content')
            raise BadRequestBodyError
