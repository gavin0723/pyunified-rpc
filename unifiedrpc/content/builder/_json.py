# encoding=utf8
# The json content builder

"""The json content builder
"""

import mime

from unifiedrpc.util import json

from base import ContentBuilder

class JsonContentBuilder(ContentBuilder):
    """The ContentBuilder
    """
    SUPPORT_MIMETYPES = [
        mime.APPLICATION_JSON
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
            if not context.response.encoding:
                raise ValueError('Require response encoding')
            if isinstance(value, (dict, tuple, list)):
                context.response.content = json.dumps(value, ensure_ascii = False).encode(context.response.encoding)
            else:
                raise ValueError('Unsupported response value type [%s]' % type(value).__name__)


