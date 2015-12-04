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

    def isSupportMimeType(self, mimeType):
        """Check if the current content builder could support the specified mimeType
        """
        return mimeType in self.builders

    def build(self, context):
        """Build the content
        NOTE:
            This method should set the context properly
        Parameters:
            context                         The Context object
        Returns:
            Nothing
        """
        mimeType = context.response.mimeType.lower()
        if not mimeType:
            mimeType = self.DEFAULT_MIME_TYPE
        if not mimeType in self.builders:
            raise ValueError('Unsupported mime type [%s]' % context.response.mimeType)
        # Build
        return self.builders[mimeType].build(context)

    def add(self, builder, mimeType):
        """Add a builder
        """
        self.builders[mimeType] = builder

    @classmethod
    def default(cls):
        """Create a default AutomaticContentBuilder
        Returns:
            AutomaticContentBuilder object
        """
        from text import TextContentBuilder
        from _json import JsonContentBuilder
        # Create the builder
        textBuilder = TextContentBuilder()
        jsonBuilder = JsonContentBuilder()
        # Add them
        builders = {}
        for builder in (textBuilder, jsonBuilder):
            for mimeType in builder.SUPPORT_MIMETYPES:
                builders[mimeType] = builder
        # Done
        return AutomaticContentBuilder(builders)
