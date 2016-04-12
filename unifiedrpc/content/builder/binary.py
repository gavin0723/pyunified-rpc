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

    BLOCK_SIZE = 4096

    def build(self, response, values):
        """Build the content
        """
        for value in values:
            if isinstance(value, (file, StringIO.StringIO, cStringIO.InputType)):
                # A file like stream object
                try:
                    while True:
                        buffer = value.read(self.BLOCK_SIZE)
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
                        value.close()
                    except:
                        self.logger.exception('Failed to close stream')
            elif isinstance(value, basestring):
                # A string
                yield value
            else:
                raise ValueError('Unsupported value type [%s] for binary content builder' % type(value).__name__)
