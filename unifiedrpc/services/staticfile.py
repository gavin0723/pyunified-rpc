# encoding=utf8

""" The static files service
    Author: lipixun
    Created Time : 四  6/ 9 23:40:04 2016

    File Name: staticfiles.py
    Description:

"""

import mime

from os.path import join, isfile, splitext

from unifiedrpc import context, Endpoint, Service
from unifiedrpc.errors import NotFoundError
from unifiedrpc.helpers import container
from unifiedrpc.adapters.web import head, get
from unifiedrpc.content.container import PlainContentContainer

FILETYPES = {
    'js'        : 'application/x-javascript',
    'css'       : mime.TEXT_CSS,
    'html'      : mime.TEXT_HTML,
    'htm'       : mime.TEXT_HTML,
}

class StaticFileService(Service):
    """The static file service
    """
    def __init__(self, path, prefix = None, filetypes = None):
        """Create a new StaticFileService
        Parameters:
            path                        The local path
            prefix                      The url prefix
        """
        self.path = path
        # Create endpoint
        endpoints = {}
        if prefix:
            if prefix.endswith('/'):
                prefix = prefix[: -1]
            # Create the get entry
            endpoint = Endpoint(self.getEntry)
            get('%s/<path:path>' % prefix)(endpoint)
            container(PlainContentContainer)(endpoint)
            endpoints['getEntry'] = endpoint
            # Create the head entry
            endpoint = Endpoint(self.headEntry)
            head('%s/<path:path>' % prefix)(endpoint)
            endpoints['headEntry'] = endpoint
        # The file types
        self.filetypes = filetypes or FILETYPES
        # Super
        super(StaticFileService, self).__init__(endpoints = endpoints)

    def serveFile(self, path):
        """Serve file
        """
        # TODO: Secure the path
        filepath = join(self.path, path)
        # Checkout the file
        if not isfile(filepath):
            raise NotFoundError
        # Detect the file type
        ext = splitext(filepath)[1].lower()[1: ]
        context.response.mimeType = self.filetypes.get(ext, 'text/plain')
        # Return the file object
        return open(filepath, 'rb')

    def headEntry(self, path, **kwargs):
        """The head entry
        """

    def getEntry(self, path, **kwargs):
        """Get the file in path
        """
        return self.serveFile(path)
