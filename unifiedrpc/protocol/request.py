# encoding=utf8
# The request definition

"""The request definition
"""

from collections import namedtuple

from unifiedrpc import CONFIG_RESPONSE_ENCODING

class Request(object):
    """The request class
    This is a general request object
    Attributes:
        headers                         A dict which key is a string value is any kind of object represents the request headers
        params                          A dict which key is a string value is any kind of object. The request parameters which used as RPC method parameters
        content                         The request content, RequestContent object
        accept                          The accept content, AcceptContent object
    """
    DEFAULT_RESPONSE_ENCODING   = 'utf-8'

    def __init__(self, headers = None, params = None, content = None, accept = None):
        """Create a new Request object
        """
        self.headers = headers
        self.params = params
        self.content = content
        self.accept = accept

    def getDefinedEncoding(self, context):
        """Get the defined request encoding
        """
        encoding = context.adapter.configs.get(CONFIG_RESPONSE_ENCODING)
        if not encoding:
            encoding = context.runtime.configs.get(CONFIG_RESPONSE_ENCODING)
        if not encoding:
            encoding = self.DEFAULT_RESPONSE_ENCODING
        # Done
        return encoding

class RequestContent(object):
    """The body of the request
    Attributes:
        mimeType                        The request content mimeType
        encoding                        The request content encoding
        length                          The request content length
        stream                          The request stream
        data                            The parsed data
    """
    def __init__(self, mimeType = None, encoding = None, length = None, params = None, stream = None, data = None):
        """Create a new RequestContent
        """
        self.mimeType = mimeType
        self.encoding = encoding
        self.length = length
        self.params = params
        self.stream = stream
        self.data = data

class AcceptContent(object):
    """The accept content of the request
    Attributes:
        mimeTypes                       The mime types, a list of AcceptValue object
        charsets                        The charsets, a list of AcceptValue object
        encodings                       The encodings, a list of AcceptValue object
        languages                       The languages, a list of AcceptValue object
    """
    def __init__(self, mimeTypes = None, charsets = None, encodings = None, languages = None):
        """Create a new AcceptContent
        """
        self.mimeTypes = mimeTypes
        self.charsets = charsets
        self.encodings = encodings
        self.languages = languages

    def __str__(self):
        """Convert to string
        """
        return 'MimeTypes [%s] Charsets [%s] Encodings [%s] Languages [%s]' % (
            ','.join([ '%s:%s' % x for x in self.mimeTypes ]) if self.mimeTypes else '',
            ','.join([ '%s:%s' % x for x in self.charsets ]) if self.charsets else '',
            ','.join([ '%s:%s' % x for x in self.encodings ]) if self.encodings else '',
            ','.join([ '%s:%s' % x for x in self.languages ]) if self.languages else '',
            )

    def __repr__(self):
        """Repr
        """
        return '%s: %s' % (type(self).__name__, self)

AcceptValue = namedtuple('AcceptValue', 'value,quality')
