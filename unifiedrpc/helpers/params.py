# encoding=utf8

""" The parameter helpers
    Author: lipixun
    Created Time : Fri 06 Nov 2015 05:42:01 PM CST

    File Name: params.py
    Description:

"""

def paramtype(**params):
    """Define the parameter types
    """
    def decorate(endpoint):
        """The method to decorate the endpoint
        """
        # Add the parameters to endpoint
        for name, type in params.iteritems():
            endpoint.signature.parameter.types[name] = type
        # Done
        return endpoint

    return decorate


