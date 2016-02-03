# encoding=utf8

""" The binary content builder
    Author: lipixun
    Created Time : 日  1/24 17:51:57 2016

    File Name: binary.py
    Description:

"""

import logging
import cStringIO, StringIO

import mime

from base import ContentBuilder

class BinaryContentBuilder(ContentBuilder):
    """The binary content builder
    """
    SUPPORT_MIMETYPES = [
        mime.APPLICATION_OCTET_STREAM,
        mime.IMAGE_PNG,
        ]

    def isSupportMimeType(self, mimeType):
        """Check if the current content builder could support the specified mimeType
        """
        return mimeType.lower() in self.SUPPORT_MIMETYPES

    def build(self, context):
        """Build the content
        Parameters:
            context                         The Context object
        Returns:
            The build value
        """
        if context.response.container:
            # Good, get the value and headers
            value, headers = context.response.container.dump()
            if headers:
                self.applyHeaderResponse(headers, context)
            if isinstance(value, (file, StringIO.StringIO, cStringIO.InputType)):
                # A file like stream object
                return StreamContentWrapper(value)
            elif isinstance(value, basestring):
                # A string
                return (value, )
            else:
                raise ValueError('No supported value [%s] of type [%s]' % (value, type(value).__name__))

class StreamContentWrapper(object):
    """The file like stream object content wrapper
    """
    BLOCK_SIZE  = 4096

    logger = logging.getLogger('unifiedrpc.content.builder.binary.file')

    def __init__(self, fd):
        """Create a new FileContentWrapper
        """
        self.fd = fd

    def __iter__(self):
        """Iterate file content
        """
        try:
            while True:
                buffer = self.fd.read(self.BLOCK_SIZE)
                if buffer:
                    yield buffer
                else:
                    break
        except EOFError:
            pass
        except:
            self.logger.exception('Iterate read stream error')
        finally:
            try:
                self.fd.close()
            except:
                self.logger.exception('Failed to close stream')

