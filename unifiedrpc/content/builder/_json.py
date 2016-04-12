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
        mime.APPLICATION_JSON,
    ]

    def build(self, response, values):
        """Build the content
        """
        # Get all results
        values = list(values)
        # Check the values
        if len(values) == 0:
            # An empty response
            yield '{}'
        elif len(values) == 1:
            # Good, encode the value
            value = values[0]
            if isinstance(value, (dict, tuple, list)):
                yield json.dumps(value, ensure_ascii = False).encode(response.encoding)
            else:
                raise ValueError('Unsupported value type [%s] for json content builder' % type(value).__name__)
        else:
            # Too many values
            raise ValueError('Too many values [%s] returned for json content builder' % len(values))
