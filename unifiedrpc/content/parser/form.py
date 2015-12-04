# encoding=utf8
# The form content parser

"""The form content parser
"""

import mime

from werkzeug.formparser import parse_form_data

from base import ContentParser

class FormContentParser(ContentParser):
    """The form content parser
    """
    SUPPORT_MIMETYPES = [
        mime.APPLICATION_X_WWW_FORM_URLENCODED,
        mime.MULTIPART_FORM_DATA
    ]

    def parse(self, context):
        """Parse the request content
        """
        stream, form, files = parse_form_data(context.request.environ)
        return FormData(form, stream, files)

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
