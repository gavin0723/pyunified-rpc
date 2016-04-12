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

    def build(self, response, values):
        """Build the content
        """
        raise NotImplementedError
