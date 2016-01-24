# encoding=utf8
# The RPC content builder

"""The RPC content builder
"""

from text import TextContentBuilder
from _json import JsonContentBuilder
from binary import BinaryContentBuilder
from automatic import AutomaticContentBuilder

def default():
    """Get the default builder
    """
    # Create the builders
    textBuilder = TextContentBuilder()
    jsonBuilder = JsonContentBuilder()
    binaryBuilder = BinaryContentBuilder()
    # Add them
    builders = {}
    for builder in (textBuilder, jsonBuilder, binaryBuilder):
        for mimeType in builder.SUPPORT_MIMETYPES:
            builders[mimeType] = builder
    # Done
    return AutomaticContentBuilder(builders)

__all__ = [ 'default' ]

