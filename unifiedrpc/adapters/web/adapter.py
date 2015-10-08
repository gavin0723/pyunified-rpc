# encoding=utf8
# The web RPC adapter

"""The web RPC adapter
"""

from unifiedrpc.adapters import AdapterBase

class WebAdapter(AdapterBase):
    """The web adapter
    This is the basic web adapter class, also a WSGI compatible class
    NOTE:
        This adapter doesn't implement the 'startAsync' and 'close' method, so it couldn't be
        used instanced directly to insert into rpc server
    """
    def __init__(self, host, port):
        """Create a new WebAdapter
        Parameters:
            host                        The bound host
            port                        The bound port
        """
        # Check parameters
        if not isinstance(host, basestring):
            raise TypeError('Invalid parameter host, require string type actually got [%s]' % (type(host).__name__))
        if not isinstance(port, int):
            raise TypeError('Invalid parameter port, require int type actually got [%s]' % (type(port).__name__))
        # Set
        self.host = host
        self.port = port

    def __call__(self, environ, startResponse):
        """The WSGI entry
        Parameters:
            environ                     The environment
            startResponse               The callback method to start response
        Returns:
            Yield or list of string for http response content
        """

    def onRequest(self, request):
        """On request
        Parameters:
            request                     The request object
        Returns:
            response content or None
        """
        raise NotImplementedError

class GeventWebAdapter(WebAdapter):
    """The gevent web adapter
    This is a gevent-bound web adapter which should be used in gevent rpc server
    """
    def __init__(self, host, port):
        """Create a new GeventWebAdapter
        """
        # Super
        super(GeventWebAdapter, self).__init__(host, port)
        # Set
        self.server = None
        self.callback = None

    def onRequest(self, request):
        """On request
        """
        cb = self.callback
        if cb:
            return cb(request)

    def startAsync(self, onRequestCallback, endpoints):
        """Start asynchronously
        """
        if not onRequestCallback:
            raise ValueError('Require parameter onRequestCallback')
        if self.server:
            raise ValueError('Adapter has already started')
        self.callback = onRequestCallback
        from gevent import pywsgi
        self.server = pywsgi.WSGIServer((self.host, self.port), self)
        self.server.start()

    def close(self):
        """Close current adapter
        """
        if not self.server:
            raise ValueError('Adapter hasn\'t started')
        self.server.close()
        self.server = None
        self.callback = None

