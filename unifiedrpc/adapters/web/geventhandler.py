# encoding=utf8

""" The gevent wsgi handler
    Author: lipixun
    Created Time : 一  6/ 6 19:20:50 2016

    File Name: geventhandler.py
    Description:

"""

from gevent.pywsgi import WSGIHandler as _WSGIHandler

class WSGIHandler(_WSGIHandler):
    """The wsgi handler
    This handle will extend the standard gevent wsgi handler:
        - Add socket object to the environ as key 'wsgi.socket'
    """
    def get_environ(self):
        """Get environ
        """
        environ = super(WSGIHandler, self).get_environ()
        environ['wsgi.socket'] = self.socket
        # Done
        return environ

