# encoding=utf8
# The web adapter request

"""The web adapter request

Always be used as raw request in protocol.Request

"""
import urlparse

from werkzeug.wrappers import Request

from unifiedrpc.errors import BadRequestError
from unifiedrpc.protocol.request import Request as ProtocolRequest, RequestContent, AcceptContent, AcceptValue

class WebRequest(Request, ProtocolRequest):
    """The web request class
    Attributes:
        queryParams                         The query parameters
        requestContent                      The request content, RequestContent object
                                            NOTE:
                                                This class will only parse the necessary data structure in header but request body itself
        acceptContent                       The accept content, AcceptContent object
    """
    def __init__(self, environ):
        """Create a new WebRequest
        """
        # Super for werkzeug request
        Request.__init__(self, environ)
        # Parse the query string
        # NOTE:
        #   Here, the value of queryParams a list: key -> [ value ]
        #   We will not change this value in order to support multiple values of a query parameter
        self.queryParams = self.parseQueryParameter()
        # Super for protocol request
        ProtocolRequest.__init__(self,
            self.headers,
            self.queryParams,
            self.parseRequestContent(),
            self.parseAcceptContent()
            )

    def parseQueryParameter(self):
        """Parse the query parameters
        Returns:
            A dict which key is parameter name value is a list of parameter value
        """
        if self.query_string:
            return urlparse.parse_qs(self.query_string)

    def parseRequestContent(self):
        """Parse content type
        Returns:
            RequestContent object
        """
        mimeType, encoding, params = self.mimetype, self.content_encoding, self.mimetype_params
        # Check the encoding
        if not encoding:
            encoding = params.get('charset')
        length = self.content_length
        # Send it
        return RequestContent(mimeType, encoding, length, params, self.stream)

    def parseAcceptContent(self):
        """Parse accept
        Returns:
            A list of AcceptContent
        """
        mimeTypes, charsets, encodings, languages = None, None, None, None
        # The mime types
        if self.accept_mimetypes:
            mimeTypes = list(sorted(map(lambda (v, q): AcceptValue(v, q), self.accept_mimetypes), key = lambda v: v.quality, reverse = True))
        if self.accept_charsets:
            charsets = list(sorted(map(lambda (v, q): AcceptValue(v, q), self.accept_charsets), key = lambda v: v.quality, reverse = True))
        # Done
        return AcceptContent(mimeTypes, charsets, encodings, languages)


