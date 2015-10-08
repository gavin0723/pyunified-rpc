# encoding=utf8
# The web adapter endpoint

"""The web endpoint adapter
"""

from uuid import uuid4

class WebEndpoint(object):
    """The web endpoint
    Attributes:
        path                            The path
        method                          The method
        contentType                     The content type
    """
    def __init__(self, path, method, contentType = None):
        """Create a new WebEndpoint
        """
        self.id = str(uuid4())  # Create a unique id, this id will be used for further endpoint tracking and seeking
                                # NOTE: DONOT modify this field
        self.path = path
        self.method = method
        self.contentType = contentType

