# encoding=utf8

""" The response object
    Author: lipixun
    Created Time : 三 12/ 2 16:32:06 2015

    File Name: response.py
    Description:

"""

from Cookie import SimpleCookie

from unifiedrpc.protocol import Response

class WebResponse(Response):
    """The web response
    """
    def __init__(self, status = 200, cookies = None, **kwargs):
        """Create a new WebResponse
        """
        self.status = status
        self.cookies = cookies or SimpleCookie()
        # Super
        super(WebResponse, self).__init__(**kwargs)

    def redirect(self, location, code = 302):
        """Redirect this response
        """
        self.headers["Location"] = location
        self.status = code
