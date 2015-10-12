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
        stream, form, files = parse_form_data(context.request.raw.environ)
        return FormData(form, stream, files)

class FormData(object):
    """The form data object
    """
    def __init__(self, form, stream, files):
        """Create a new FormData
        """
        self.form = form
        self.stream = stream
        self.files = files

    def __len__(self):
        """Get the length
        """
        return len(self.form)

    def __contains__(self, key):
        """Check if the form contains an item
        """
        return key in self.form

    def __getitem__(self, key):
        """Get an item from form
        """
        return self.form[key]

    def get(self, key, default = None):
        """Try to get an item from form
        """
        return self.form.get(key, default)
