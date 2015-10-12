# encoding=utf8
# The json content parser

"""The json content parser
"""

import mime

from unifiedrpc.util import json

from base import ContentParser

class JsonContentParser(ContentParser):
    """The JsonContentParser
    """
    SUPPORT_MIMETYPES = [
        mime.APPLICATION_JSON,
    ]

    def parse(self, request):
        """Parse the request content
        """
        return json.load(request.content.stream, encoding = request.content.encoding)
