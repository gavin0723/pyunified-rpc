# encoding=utf8

""" The helpers
    Author: lipixun
    Created Time : 五  4/ 8 17:30:10 2016

    File Name: helper.py
    Description:

"""

from unifiedrpc import context

def redirect(location, status = 302):
    """Redirect
    """
    context.response.status = status
    context.response.headers['Location'] = location
