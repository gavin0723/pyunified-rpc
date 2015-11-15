# encoding=utf8

""" The rabbitmq adapters
    Author: lipixun
    Created Time : Sat 14 Nov 2015 06:39:44 PM CST

    File Name: decorators.py
    Description:

"""

from endpoint import SubscribeEndpoint, AnonymousSubscribeEndpoint

def subscribe(*queues, **kwargs):
    """Subscribe
    """
    def decorate(endpoint):
        """Decorate the endpoint
        """
        subEndpoint = SubscribeEndpoint(*queues, **kwargs)
        return subEndpoint(endpoint)
    return decorate

def annonymousSubscribe(*bindings, **kwargs):
    """Subscribe
    """
    def decorate(endpoint):
        """Decorate the endpoint
        """
        subEndpoint = AnonymousSubscribeEndpoint(*bindings, **kwargs)
        return subEndpoint(endpoint)
    return decorate
