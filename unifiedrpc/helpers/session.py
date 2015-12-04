# encoding=utf8

""" The session helpers
    Author: lipixun
    Created Time : Fri 04 Dec 2015 10:04:03 PM CST

    File Name: session.py
    Description:

"""

from ..executionnode.session import SessionValidationNode

def requiresession(key, validator = None, error = None):
    """Require session to satisfy a condition
    Parameters:
        key                     The key in session
        validator               The value validator, have 1 parameter: the session value
        error                   The error method, has 1 parameter: the error which is raised by validator if has one
    """
    def decorate(endpoint):
        """The method to decorate the endpoint
        """
        node = SessionValidationNode(key, validator, error)
        endpoint.pipeline.add(node, 900)
        # Done
        return endpoint
    # Done
    return decorate

