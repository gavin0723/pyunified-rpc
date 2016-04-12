# encoding=utf8

""" The parameter helpers
    Author: lipixun
    Created Time : Fri 06 Nov 2015 05:42:01 PM CST

    File Name: params.py
    Description:

"""

from unifiedrpc.protocol import CONFIG_ENDPOINT_PARAMETER_TYPE

def paramtype(**params):
    """Define the parameter types
    """
    def decorate(endpoint):
        """The method to decorate the endpoint
        """
        if not CONFIG_ENDPOINT_PARAMETER_TYPE in endpoint._configs:
            endpoint._configs[CONFIG_ENDPOINT_PARAMETER_TYPE] = {}
        typeConfigs = endpoint._configs[CONFIG_ENDPOINT_PARAMETER_TYPE]
        # Add the parameters to endpoint
        for name, type in params.iteritems():
            typeConfigs[name] = type
        # Done
        return endpoint
    # Done
    return decorate
