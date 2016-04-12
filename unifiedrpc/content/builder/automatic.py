# encoding=utf8
# The automatic content builder

"""The automatic content builder
"""

from base import ContentBuilder

class AutomaticContentBuilder(ContentBuilder):
    """The automatic content builder
    """
    DEFAULT_MIME_TYPE   = 'text/plain'

    def __init__(self, builders = None):
        """Create a new AutomaticContentBuilder
        """
        self.builders = builders or {}

    @property
    def SUPPORT_MIMETYPES(self):
        """Get the supported mime types
        """
        return self.builders.keys()

    def build(self, response, values):
        """Build the content
        """
        mimeType = response.mimeType.lower() or self.DEFAULT_MIME_TYPE
        if not mimeType in self.builders:
            raise ValueError('Unsupported mime type [%s] for automatic content builder' % response.mimeType)
        # Build
        return self.builders[mimeType].build(response, values)

    def add(self, builder, mimeType):
        """Add a builder
        """
        self.builders[mimeType] = builder
