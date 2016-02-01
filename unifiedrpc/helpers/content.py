# encoding=utf8

""" The content helper
    Author: lipixun
    Created Time : Sat 21 Nov 2015 09:05:08 PM CST

    File Name: content.py
    Description:

"""

from unifiedrpc.caller import DataTypeValidationCaller
from unifiedrpc.definition import CONFIG_RESPONSE_CONTENT_CONTAINER, CONFIG_RESPONSE_MIMETYPE, CONFIG_RESPONSE_ENCODING

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

def container(containerClass):
    """Set the container class of the endpoint
    """
    def decorate(endpoint):
        """The method to decorate the endpoint
        """
        endpoint.configs[CONFIG_RESPONSE_CONTENT_CONTAINER] = containerClass
        # Done
        return endpoint
    # Done
    return decorate

def mimetype(mimetype):
    """Set the response mimetype
    Parameters:
        mimetype                    The mimetype, could a single mimetype or a list / tuple of mimetypes
    """
    def decorate(endpoint):
        """The method to decorate the endpoint
        """
        endpoint.configs[CONFIG_RESPONSE_MIMETYPE] = mimetype
        # Done
        return endpoint
    # Done
    return decorate

def encoding(encoding):
    """Set the response encoding
    """
    def decorate(endpoint):
        """The method to decorate endpoint
        """
        endpoint.configs[CONFIG_RESPONSE_ENCODING] = encoding
        # Done
        return endpoint
    # Done
    return decorate


