# encoding=utf8
# The form content parser

"""The form content parser
"""

import logging

import mime

from werkzeug.formparser import parse_form_data

from unifiedrpc.errors import BadRequestError

from base import ContentParser

class FormContentParser(ContentParser):
    """The form content parser
    """
    SUPPORT_MIMETYPES = [
        mime.APPLICATION_X_WWW_FORM_URLENCODED,
        mime.MULTIPART_FORM_DATA
    ]

    logger = logging.getLogger('unifiedrpc.content.parser.form')

    def parse(self, context):
        """Parse the request content
        """
        try:
            stream, form, files = parse_form_data(context.request.environ)
            return FormData(form, stream, files)
        except:
            # Failed to decode the content
            self.logger.error('Failed to decode request content')
            # Raise
            raise BadRequestError

class FormData(dict):
    """The form data object
    """
    def __init__(self, form, stream, files):
        """Create a new FormData
        """
        self.stream = stream
        self.files = files
        # Super
        super(FormData, self).__init__(form)
