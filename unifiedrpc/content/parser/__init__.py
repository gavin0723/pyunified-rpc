# encoding=utf8
# The RPC content parser

"""The RPC content parser
"""

from text import TextContentParser
from form import FormContentParser
from _json import JsonContentParser
from aggregate import AggregateContentParser

def default():
    """Get default content parser
    """
    # Create the parsers
    parsers = {}
    for parser in (
        TextContentParser(),
        FormContentParser(),
        JsonContentParser(),
        ):
        for mimeType in parser.SUPPORT_MIMETYPES:
            parsers[mimeType] = parser
    # Done
    return AggregateContentParser(parsers)

__all__ = [ 'default' ]
