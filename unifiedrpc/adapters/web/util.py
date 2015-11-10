# encoding=utf8

""" The web utility
    Author: lipixun
    Created Time : Tue 10 Nov 2015 04:36:30 PM CST

    File Name: util.py
    Description:

"""

import mime

TEXT_MIMETYPES = [
        mime.APPLICATION_JSON,
        mime.APPLICATION_XML
        ]

def getContentType(mimetype, charset):
    """Returns the full content type string with charset for a mimetype.
    """
    if mimetype.startswith('text/') or \
       mimetype in TEXT_MIMETYPES or \
       (mimetype.startswith('application/') and (mimetype.endswith('+xml') or mimetype.endswith('+json'))):
        mimetype += '; charset=' + charset
    return mimetype


