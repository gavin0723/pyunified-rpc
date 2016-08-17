# encoding=utf8

""" The web connection
    Author: lipixun
    Created Time : 一  6/ 6 18:15:23 2016

    File Name: connection.py
    Description:

"""

from email.utils import parsedate

class Connection(object):
    """The web connection
    """
    def __init__(self, environ):
        """Create a new Connection
        """
        self.socket = environ.get('wsgi.socket')
        if self.socket:
            # Set the info
            endpoint = self.socket.getpeername()
            if endpoint and isinstance(endpoint, tuple):
                host, port = self.socket.getpeername()
                self.remote = RemoteInfo(host, port)
            else:
                self.remote = RemoteInfo()
            endpoint = self.socket.getsockname()
            if endpoint and isinstance(endpoint, tuple):
                host, port = endpoint
                self.local = LocalInfo(host, port)
            else:
                self.local = LocalInfo()
        else:
            # Socket object not found
            self.local = None
            self.remote = None
        # Check ssl
        if environ.get('wsgi.url_scheme') == 'https':
            self.ssl = True
            self.remote.cert = self.loadCertificate()
        else:
            self.ssl = False

    def loadCertificate(self):
        """Load certificate
        """
        cert = self.socket.getpeercert()
        if cert:
            # Get the time
            notBefore = parsedate(cert['notBefore']) if cert.get('notBefore') else None
            notAfter = parsedate(cert['notAfter']) if cert.get('notAfter') else None
            # Get the name
            subjectNames = dict(map(lambda x: x[0], cert['subject'])) if cert.get('subject') else {}
            issuerNames = dict(map(lambda x: x[0], cert['issuer'])) if cert.get('issuer') else {}
            # Get the subject alternative name
            subjectAltName = cert.get('subjectAltName')
            if subjectAltName:
                subjectNames['altNames'] = subjectAltName
            # Create the Certificate object
            return Certificate(Name(**subjectNames), Name(**issuerNames), notBefore, notAfter, cert.get('serialNumber'), cert.get('version'))

class LocalInfo(object):
    """The local info
    """
    def __init__(self, host = None, port = None):
        """Create an new LocalInfo
        """
        self.host = host
        self.port = port

class RemoteInfo(object):
    """The remote info
    """
    def __init__(self, host = None, port = None, cert = None):
        """Create a new PeerInfo
        """
        self.host = host
        self.port = port
        self.cert = cert

class Certificate(object):
    """The certificate
    """
    def __init__(self, subject, issuer, notBefore, notAfter, serialNumber, version):
        """Create a new Certificate
        """
        self.subject = subject
        self.issuer = issuer
        self.notBefore = notBefore
        self.notAfter = notAfter
        self.serialNumber = serialNumber
        self.version = version

    def __str__(self):
        """To string
        """
        return 'Subject [%s] Issuer [%s] NotBefore [%s] NotAfter[%s] SN [%s] VERSION [%s]' % (
            self.subject,
            self.issuer,
            self.notBefore,
            self.notAfter,
            self.serialNumber,
            self.version
            )

class Name(object):
    """The name
    """
    def __init__(
        self,
        countryName = None,
        stateOrProvinceName = None,
        localityName = None,
        organizationName = None,
        organizationalUnitName = None,
        commonName = None,
        emailAddress = None,
        altNames = None
        ):
        """Create a new Name
        """
        self.countryName = countryName
        self.stateOrProvinceName = stateOrProvinceName
        self.localityName = localityName
        self.organizationName = organizationName
        self.organizationalUnitName = organizationalUnitName
        self.commonName = commonName
        self.emailAddress = emailAddress
        self.altNames = altNames

    def __str__(self):
        """To string (The DN String)
        """
        pieces = []
        if self.commonName:
            pieces.append('/CN=%s' % self.commonName)
        if self.countryName:
            pieces.append('/C=%s' % self.countryName)
        if self.stateOrProvinceName:
            pieces.append('/ST=%s' % self.stateOrProvinceName)
        if self.localityName:
            pieces.append('/L=%s' % self.localityName)
        if self.organizationName:
            pieces.append('/O=%s' % self.organizationName)
        if self.organizationalUnitName:
            pieces.append('/OU=%s' % self.organizationalUnitName)
        if self.emailAddress:
            pieces.append('/emailAddress=%s' % self.emailAddress)
        # Done
        return ''.join(pieces)
