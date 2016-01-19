# encoding=utf8

""" The content helper
    Author: lipixun
    Created Time : Sat 21 Nov 2015 09:05:08 PM CST

    File Name: content.py
    Description:

"""

from unifiedrpc.caller import DataTypeValidationCaller

def requiredata(dataType = dict, notEmpty = True):
    """Require the request data should be a specified type
    """
    def decorate(endpoint):
        """The method to decorate the endpoint
        """
        endpoint.callers.append((DataTypeValidationCaller(dataType, notEmpty), 500))
        # Done
        return endpoint
    # Done
    return decorate
