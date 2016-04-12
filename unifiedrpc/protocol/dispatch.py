# encoding=utf8

""" The dispatch
    Author: lipixun
    Created Time : 五  4/ 8 15:11:56 2016

    File Name: dispatch.py
    Description:

"""

class DispatchResult(object):
    """The dispatch result
    """
    def __init__(self, endpoint, parameters, service):
        """Create a new DispatchResult
        """
        self.endpoint = endpoint
        self.parameters = parameters
        self.service = service
