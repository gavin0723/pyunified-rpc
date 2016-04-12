# encoding=utf8

""" The response object
    Author: lipixun
    Created Time : 三 12/ 2 16:32:06 2015

    File Name: response.py
    Description:

"""

from unifiedrpc.protocol import Response

class WebResponse(Response):
    """The web response
    """
    def __init__(self, status = 200, **kwargs):
        """Create a new WebResponse
        """
        self.status = status
        # Super
        super(WebResponse, self).__init__(**kwargs)
