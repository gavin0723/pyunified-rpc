# encoding=utf8

""" The session helpers
    Author: lipixun
    Created Time : Fri 04 Dec 2015 10:04:03 PM CST

    File Name: session.py
    Description:

"""

from unifiedrpc.stages import SessionValidator

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
        endpoint.stage.addCaller(SessionValidator(key, validator, error), 900)
        # Done
        return endpoint
    # Done
    return decorate
