# encoding=utf8

""" The response object
    Author: lipixun
    Created Time : 一  1/18 22:32:14 2016

    File Name: response.py
    Description:

"""

from Cookie import SimpleCookie

from unifiedrpc.errors import NotAcceptableError, ERRCODE_NOTACCEPTABLE_NO_SUPPORTED_MIMETYPES
from unifiedrpc.definition import CONFIG_RESPONSE_MIMETYPE, CONFIG_RESPONSE_ENCODING, CONFIG_RESPONSE_CONTENT_CONTAINER, CONFIG_RESPONSE_CONTENT_BUILDER
from unifiedrpc.content.builder import TextContentBuilder
from unifiedrpc.content.container import PlainContentContainer

class Response(object):
    """The response class
    """
    DEFAULT_RESPONSE_MIMETYPE           = 'text/plain'
    DEFAULT_RESPONSE_ENCODING           = 'utf-8'
    DEFAULT_CONTENT_CONTAINER           = PlainContentContainer
    DEFAULT_CONTENT_BUILDER             = TextContentBuilder

    def __init__(self, headers = None, content = None, mimeType = None, encoding = None, cookies = None):
        """Create a new Response
        """
        self.headers = headers or {}
        self.content = content or ResponseContent()
        self.mimeType = mimeType
        self.encoding = encoding
        self.cookies = cookies or SimpleCookie()

    @classmethod
    def getEncoding(cls, request, response, execution):
        """Get the response encoding
        """
        # How to choose the encoding:
        #   - If header accept-encoding is set, will use this value
        #   - If header accept-charset is set, will use this value
        if request and request.accept and request.accept.encodings:
            encoding = request.accept.encodings[0].value.lower()
        elif request and request.accept and request.accept.charsets:
            encoding = request.accept.charsets[0].value.lower()
        else:
            encoding = execution.getConfig(CONFIG_RESPONSE_ENCODING)
            if not encoding:
                encoding = cls.DEFAULT_RESPONSE_ENCODING
        # Done
        return encoding

    @classmethod
    def getMimeType(cls, request, response, execution):
        """Get the response mimeType
        """
        # Get the allowed mime type(s)
        allowedMimeTypes = execution.getConfig(CONFIG_RESPONSE_MIMETYPE)
        if isinstance(allowedMimeTypes, basestring):
            allowedMimeTypes = [ allowedMimeTypes.lower() ]
        elif isinstance(allowedMimeTypes, (tuple, list)):
            allowedMimeTypes = [ x.lower() for x in allowedMimeTypes ]
        # NOTE:
        #   Pay attention to the value of allowedMimeTypes:
        #       - None means no limitation, in this case the server will prefer to choose the one which server supported
        #       - [] means don't allowed any mime types. If this value has been set, the server will return an error
        mimeType = None
        # Check the accepted mime types
        if not allowedMimeTypes is None and len(allowedMimeTypes) == 0:
            # Return error
            raise NotAcceptableError
        # Check the accpet mimetype
        if request.accept and request.accept.mimeTypes:
            # Select the first allowed accept mime types
            for acceptValue in request.accept.mimeTypes:
                acceptMimeType = acceptValue.value.lower().strip()
                if acceptMimeType == '*/*':
                    # Use the first accept content type the server supported
                    if not allowedMimeTypes or cls.DEFAULT_RESPONSE_MIMETYPE in allowedMimeTypes:
                        mimeType = cls.DEFAULT_RESPONSE_MIMETYPE
                    else:
                        mimeType = allowedMimeTypes[0]
                    break
                elif ((allowedMimeTypes and acceptMimeType in allowedMimeTypes) or (not allowedMimeTypes)) and response.content.builder.isSupportMimeType(acceptMimeType):
                    mimeType = acceptMimeType
                    break
            # Done
            if not mimeType:
                raise NotAcceptableError(ERRCODE_NOTACCEPTABLE_NO_SUPPORTED_MIMETYPES, 'No supported mimetype found')
        else:
            # Select the first allowed mime types
            if not allowedMimeTypes or cls.DEFAULT_RESPONSE_MIMETYPE in allowedMimeTypes:
                mimeType = cls.DEFAULT_RESPONSE_MIMETYPE
            else:
                mimeType = allowedMimeTypes[0]
        # Done
        return mimeType

    @classmethod
    def getContentContainer(cls, request, response, execution):
        """Get content container
        """
        return execution.getConfig(CONFIG_RESPONSE_CONTENT_CONTAINER) or cls.DEFAULT_CONTENT_CONTAINER

    @classmethod
    def getContentBuilder(cls, request, response, execution):
        """Get content builder
        """
        return execution.getConfig(CONFIG_RESPONSE_CONTENT_BUILDER) or cls.DEFAULT_CONTENT_BUILDER

class ResponseContent(object):
    """The response content
    """
    def __init__(self, executionResult = None, error = None, container = None, builder = None):
        """Create a new ResponseContent
        """
        self.executionResult = executionResult
        self.error = error
        self.container = container
        self.builder = builder
