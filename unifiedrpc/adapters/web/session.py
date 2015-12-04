# encoding=utf8

""" The web session adapter
    Author: lipixun
    Created Time : Fri 04 Dec 2015 07:11:08 PM CST

    File Name: session.py
    Description:

"""

from datetime import datetime

from unifiedrpc.protocol import Session, SessionManager

from werkzeug.contrib.securecookie import SecureCookie

class SecureCookieSession(Session):
    """The session which is powered by secure cookie
    """
    def __init__(self, secret, data):
        """Create a new SecureCookieSession
        """
        self.cookie = SecureCookie.unserialize(data, secret) if data else SecureCookie(secret_key = secret)

    def __len__(self):
        """Get the key count of session
        """
        return len(self.cookie)

    def __contains__(self, key):
        """Check if the session contains a key
        """
        return key in self.cookie

    def __getitem__(self, key):
        """Get value from session
        """
        return self.cookie[key]

    def __setitem__(self, key, value):
        """Set value to session
        """
        self.cookie[key] = value

    @property
    def changed(self):
        """Tell if the session is changed
        """
        return self.cookie.should_save

    def get(self, key, default = None):
        """Get value from session
        """
        return self.cookie.get(key, default)

    def set(self, key, value):
        """Set value to session
        """
        self.cookie[key] = value

    def dumps(self):
        """Dump to string
        """
        return self.cookie.serialize()

class CookieSessionManager(SessionManager):
    """The cookie session manager
    Attributes:
        sessionType         The session type, currently supports:
                            - DictSession
                            - SecureCookieSession
        key                 The key of the session cookie
        path                The cookie path
        maxAge              A number of seconds, None if the cookie should last only as long as the client's brower session
        expires             Datetime or unix timestamp
        domain              The domain
        secure              Whether the cookie should only be used in secure http transport
        httpOnly            Whether the cookie is http only or not (http only means cannot be read by java script or other brownser - side scripts)

    More specific document: http://werkzeug.pocoo.org/docs/0.11/wrappers/#werkzeug.wrappers.BaseResponse.set_cookie
    """
    def __init__(self, sessionType, key, path = '/', maxAge = None, expires = None, domain = None, secure = None, httpOnly = True):
        """Create new CookieSessionManager
        """
        self.sessionType = sessionType
        self.key = key
        self.path = path
        self.maxAge = maxAge
        self.expires = expires
        self.domain = domain
        self.secure = secure
        self.httpOnly = httpOnly

    def get(self, request):
        """Get session from cookie
        """
        return self.sessionType(request.cookies.get(self.key))

    def set(self, session, response):
        """Set session to cookie
        """
        if session.changed:
            response.set_cookie(
                    self.key,
                    value = session.dumps(),
                    path = self.path,
                    max_age = self.maxAge,
                    expires = self.expires,
                    domain = self.domain,
                    secure = self.secure,
                    httponly = self.httpOnly
                    )
    def clean(self, response):
        """Clean session
        """
        response.set_cookie(self.key, value = '', max_age = 0, expires = datetime.now())

