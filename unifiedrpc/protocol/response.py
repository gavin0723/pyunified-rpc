# encoding=utf8

""" The response object
    Author: lipixun
    Created Time : 一  1/18 22:32:14 2016

    File Name: response.py
    Description:

"""

from unifiedrpc import CONFIG_RESPONSE_MIMETYPE, CONFIG_RESPONSE_ENCODING, CONFIG_RESPONSE_CONTENT_CONTAINER
from unifiedrpc.errors import NotAcceptableError, ERRCODE_NOTACCEPTABLE_NO_SUPPORTED_MIMETYPES
from unifiedrpc.content.container.plain import PlainContentContainer

class Response(object):
    """The response class
    """
    DEFAULT_RESPONSE_MIMETYPE       = 'text/plain'
    DEFAULT_RESPONSE_ENCODING       = 'utf-8'
    DEFAULT_CONTENT_CONTAINER_CLASS = PlainContentContainer

    def __init__(self, headers = None, content = None, mimeType = None, encoding = None, container = None):
        """Create a new Response
        """
        self.headers = headers or {}
        self.content = content
        self.mimeType = mimeType
        self.encoding = encoding
        self.container = container
        # Set default
        from unifiedrpc import context
        if not self.mimeType:
            self.mimeType = self.getMimeType(context)
        if not self.encoding:
            self.encoding = self.getEncoding(context)
        if not self.container:
            self.container = self.getContainer(context)
        # Done

    def getMimeType(self, context):
        """Get the response mimeType
        """
        # Get the raw mime type(s)
        rawMimeType = None
        if context.endpoint:
            rawMimeType = context.endpoint.configs.get(CONFIG_RESPONSE_MIMETYPE)
        if not rawMimeType:
            rawMimeType = context.adapter.configs.get(CONFIG_RESPONSE_MIMETYPE)
            if not rawMimeType:
                rawMimeType = context.runtime.configs.get(CONFIG_RESPONSE_MIMETYPE)
        # Get the allowed mime types array from raw mime type(s)
        if isinstance(rawMimeType, basestring):
            allowedMimeTypes = [ rawMimeType.lower() ]
        elif isinstance(rawMimeType, (tuple, list)):
            allowedMimeTypes = [ x.lower() for x in rawMimeType ]
        else:
            allowedMimeTypes = None
        # NOTE:
        #   Pay attention to the value of allowedMimeTypes:
        #       - None means no limitation, in this case the server will prefer to choose the one which server supported
        #       - [] means donot allowed any mime types. If this value has been set, the server will return as DEFAULT_RESPONSE_MIMETYPE regardless of
        #         accept of request
        mimeType = None
        # Check the accepted mime types
        if isinstance(allowedMimeTypes, (tuple, list)) and len(allowedMimeTypes) == 0:
            # Use the default one
            mimeType = self.DEFAULT_RESPONSE_MIMETYPE
        else:
            if context.request and context.request.accept and context.request.accept.mimeTypes:
                # Select the first allowed accept mime types
                for acceptValue in context.request.accept.mimeTypes:
                    acceptMimeType = acceptValue.value.lower().strip()
                    if acceptMimeType == '*/*':
                        # Use the first accept content type the server supported
                        if not allowedMimeTypes or self.DEFAULT_RESPONSE_MIMETYPE in allowedMimeTypes:
                            mimeType = self.DEFAULT_RESPONSE_MIMETYPE
                        else:
                            mimeType = allowedMimeTypes[0]
                        break
                    elif acceptMimeType in allowedMimeTypes and context.components.contentBuilder.isSupportMimeType(acceptMimeType):
                        mimeType = acceptMimeType
                        break
                if not mimeType:
                    raise NotAcceptableError(ERRCODE_NOTACCEPTABLE_NO_SUPPORTED_MIMETYPES, 'No supported mimetype found')
            else:
                # Select the first allowed mime types
                if not allowedMimeTypes or self.DEFAULT_RESPONSE_MIMETYPE in allowedMimeTypes:
                    mimeType = self.DEFAULT_RESPONSE_MIMETYPE
                else:
                    mimeType = allowedMimeTypes[0]
        # Done
        return mimeType

    def getEncoding(self, context):
        """Get the response encoding
        """
        # How to choose the encoding:
        #   - If header accept-encoding is set, will use this value
        #   - If header accept-charset is set, will use this value
        #   - Otherwise will use the encoding defined in endpoint / adapter / server / server default
        if context.request and context.request.accept and context.request.accept.encodings:
            encoding = context.request.accept.encodings[0].value.lower()
        elif context.request and context.request.accept and context.request.accept.charsets:
            encoding = context.request.accept.charsets[0].value.lower()
        else:
            encoding = None
            if context.endpoint:
                encoding = context.endpoint.configs.get(CONFIG_RESPONSE_ENCODING)
            if not encoding:
                encoding = context.adapter.configs.get(CONFIG_RESPONSE_ENCODING)
            if not encoding:
                encoding = context.runtime.configs.get(CONFIG_RESPONSE_ENCODING)
            if not encoding:
                encoding = self.DEFAULT_RESPONSE_ENCODING
        # Done
        return encoding

    def getContainer(self, context):
        """Get the response container
        """
        containerClass = None
        if context.endpoint:
            containerClass = context.endpoint.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
        if not containerClass:
            containerClass = context.adapter.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
        if not containerClass:
            containerClass = context.components.contentContainer
        if not containerClass:
            containerClass = context.runtime.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)
        if not containerClass:
            containerClass = self.DEFAULT_CONTENT_CONTAINER_CLASS
        # Done
        return containerClass()

