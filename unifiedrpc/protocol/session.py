# encoding=utf8

""" The session protocol
    Author: lipixun
    Created Time : Fri 04 Dec 2015 07:01:26 PM CST

    File Name: session.py
    Description:

"""

from base64 import b64encode, b64decode

from unifiedrpc.util import json

class Session(object):
    """The session
    """
    def __init__(self):
        """Create a new Session
        """
        self.clean = True           # Should clean the session or not

    def __len__(self):
        """Get the key count of session
        """
        raise NotImplementedError

    def __contains__(self, key):
        """Check if the session contains a key
        """
        raise NotImplementedError

    def __getitem__(self, key):
        """Get value from session
        """
        raise NotImplementedError

    def __setitem__(self, key, value):
        """Set value to session
        """
        raise NotImplementedError

    @property
    def changed(self):
        """Tell if the session is changed
        """
        raise NotImplementedError

    def get(self, key, default = None):
        """Get value from session
        """
        raise NotImplementedError

    def set(self, key, value):
        """Set value to session
        """
        raise NotImplementedError

class DictSession(Session):
    """The dict session
    """
    def __init__(self, dictObject = None):
        """Create a new DictSession
        """
        self._changed = False
        if dictObject is None:
            self.dictObject = {}
        elif isinstance(dictObject, basestring):
            self.dictObject = json.loads(b64decode(dictObject).decode('utf8'))
        else:
            self.dictObject = dictObject

    def __len__(self):
        """Get the key count of session
        """
        return len(self.dictObject)

    def __contains__(self, key):
        """Check if the session contains a key
        """
        return key in self.dictObject

    def __getitem__(self, key):
        """Get value from session
        """
        return self.dictObject[key]

    def __setitem__(self, key, value):
        """Set value to session
        """
        if self.dictObject.get(key) != value:
            self._changed = True
            self.dictObject[key] = value

    @property
    def changed(self):
        """Tell if the session is changed
        """
        return self._changed

    def get(self, key, default = None):
        """Get value from session
        """
        return self.dictObject.get(key, default)

    def set(self, key, value):
        """Set value to session
        """
        self[key] = value

    def dumps(self):
        """Convert to string
        """
        return b64encode(json.dumps(self.dictObject, ensure_ascii = False).encode('utf8'))

class SessionManager(object):
    """The session manager, used to extract session from request and set session to response
    """
    def get(self, request):
        """Get session object from request object
        """
        raise NotImplementedError

    def set(self, session, response):
        """Set session object to response object
        """
        raise NotImplementedError
