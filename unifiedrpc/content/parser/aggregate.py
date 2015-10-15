# encoding=utf8
# The aggregate content parser

"""The aggregate content parser
"""

import mime

from base import ContentParser

from unifiedrpc.errors import UnsupportedMediaTypeError

class AggregateContentParser(ContentParser):
    """The aggregate content parser
    """
    def __init__(self, parsers = None):
        """Create a new AggregateContentParser
        Parameters:
            parsers                 A tuple (mimeType, parser)
        """
        self.parsers = parsers or {}

    def __contains__(self, mimeType):
        """Check mimeType
        """
        return mimeType.lower() in self.parsers

    def __getitem__(self, mimeType):
        """Get a parser
        Parameters:
            mimeType                The mimeType
        Returns:
            Parser object
        """
        return self.parsers[mimeType.lower()]

    def __setitem__(self, mimeType, parser):
        """Set a parser
        Parameters:
            mimeType                The mimeType
            parser                  The parser
        Returns:
            Nothing
        """
        self.parsers[mimeType.lower()] = parser

    def get(self, mimeType, default = None):
        """Try to get a parser
        Parameters:
            mimeType                The mimeType
            default                 The default parser
        Returns:
            Parser object
        """
        return self.parsers.get(mimeType.lower(), default)

    def parse(self, context):
        """Parse the request content
        """
        parser = self.get(context.request.content.mimeType)
        if not parser:
            raise UnsupportedMediaTypeError(context.request.content.mimeType)
        # Parse
        return parser.parse(context)

    @classmethod
    def default(cls):
        """Create a default AggregateContentParser
        Returns:
            AggregateContentParser object
        """
        from text import TextContentParser
        from form import FormContentParser
        from _json import JsonContentParser
        # Create the parser
        textParser = TextContentParser()
        formParser = FormContentParser()
        jsonParser = JsonContentParser()
        # Set the parsers
        parsers = {}
        for parser in (textParser, formParser, jsonParser):
            for mimeType in parser.SUPPORT_MIMETYPES:
                parsers[mimeType] = parser
        # Done
        return AggregateContentParser(parsers)
