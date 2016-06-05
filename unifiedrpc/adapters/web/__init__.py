# encoding=utf8
# The web adapter

"""The web adapter

This adapter implements a full http web service functionalities that could be used as a python web framework

"""

from helper import redirect
from adapter import WebAdapter, GeventWebAdapter, GeventUnixSocketWebAdapter
from session import SecureCookieSession, CookieSessionManager
from decorators import *
