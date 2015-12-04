# encoding=utf8
# The web adapter

"""The web adapter

This adapter implements a full http web service functionalities that could be used as a python web framework

"""

from adapter import GeventWebAdapter
from decorators import *
from session import SecureCookieSession, CookieSessionManager
from response import Redirect

