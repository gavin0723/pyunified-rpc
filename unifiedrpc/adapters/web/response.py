# encoding=utf8

""" The response object
    Author: lipixun
    Created Time : 三 12/ 2 16:32:06 2015

    File Name: response.py
    Description:

"""

from werkzeug.wrappers import Response as WKResponse

from unifiedrpc.protocol import Response

class WebResponse(Response):
    """The web response
    """
    def __init__(self, status = None, **kwargs):
        """Create a new WebResponse
        """
        self.status = status
        # Super
        super(WebResponse, self).__init__(**kwargs)

class Redirect(WKResponse):
    """The redirect
    """
    def __init__(self, location, status = 302, content = None):
        """Create a new Redirect
        """
        super(Redirect, self).__init__(response = content, status = status, headers = { 'Location': location })
