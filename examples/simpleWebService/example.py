#!/usr/bin/env python
# encoding=utf8
# The simple webservice example

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from gevent import monkey
monkey.patch_all()

from os.path import abspath, dirname

import logging

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s', level = logging.DEBUG)

import mime

try:
    import unifiedrpc
except ImportError:
    sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
    import unifiedrpc

from unifiedrpc import Server, Service, endpoint, CONFIG_RESPONSE_MIMETYPE, CONFIG_RESPONSE_CONTENT_CONTAINER
from unifiedrpc.content.container import APIContentContainer
from unifiedrpc.adapters.web import GeventWebAdapter, get, post, put, delete

class SimpleService(Service):
    """A simple service
    """
    def __init__(self):
        """Create a new SimpleServer
        """
        super(SimpleService, self).__init__('simple')
        # Set
        self.persons = []

    @get('/')
    @endpoint()
    def getAllPersons(self):
        """Get all persons
        """
        return self.persons

if __name__ == '__main__':

    from argparse import ArgumentParser

    def getArguments():
        """Get arguments
        """
        parser = ArgumentParser(description = 'Simple web server example')
        parser.add_argument('--host', dest = 'host', default = 'localhost', help = 'The binding host')
        parser.add_argument('--port', dest = 'port', type = int, default = 8080, help = 'The binding port')
        # Done
        return parser.parse_args()

    def main():
        """The main entry
        """
        args = getArguments()
        # Create the server
        server = Server(**{ CONFIG_RESPONSE_MIMETYPE: mime.APPLICATION_JSON, CONFIG_RESPONSE_CONTENT_CONTAINER: APIContentContainer })
        server.addAdapter(GeventWebAdapter('web', args.host, args.port))
        server.addService(SimpleService())
        # Done
        server.start()

    main()

