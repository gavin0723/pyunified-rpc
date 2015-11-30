# encoding=utf8

""" The content helper
    Author: lipixun
    Created Time : Sat 21 Nov 2015 09:05:08 PM CST

    File Name: content.py
    Description:

"""

from ..executionnode.content import DataTypeValidationNode

def requiredata(dataType = dict, notEmpty = True):
    """Require the request data should be a specified type
    """
    def decorate(endpoint):
        """The method to decorate the endpoint
        """
        node = DataTypeValidationNode(dataType, notEmpty)
        endpoint.pipeline.add(node, 500)
        # Done
        return endpoint
    # Done
    return decorate

