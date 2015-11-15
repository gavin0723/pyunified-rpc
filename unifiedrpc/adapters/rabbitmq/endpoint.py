# encoding=utf8

""" The rabbitmq endpoint
    Author: lipixun
    Created Time : Sat 14 Nov 2015 07:37:08 PM CST

    File Name: endpoint.py
    Description:

"""

from uuid import uuid4

from definition import ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY
from execnode import SetDataAsParameterNode

class SubscribeEndpoint(object):
    """The subscribe endpoint
    Attributes:

    """
    def __init__(self, *queues, **kwargs):
        """Create a new SubscribeEndpoint
        """
        if not queues:
            raise ValueError('Require at least one queue')
        self.id = str(uuid4())
        self.queues = queues
        self.ack = kwargs.get('ack', False)

    def __call__(self, endpoint):
        """Attach to endpoint object
        Parameters:
            endpoint                    The protocol.Endpoint object
        Returns:
            The protocol.Endpoint object
        """
        # Add this web endpoint to the endpoint object
        if ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY in endpoint.children:
            endpoint.children[ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY][self.id] = self
        else:
            endpoint.children[ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY] = { self.id: self }
        # Add execution node
        shouldAddSetDataAsParamNode = True
        for node in endpoint.pipeline.nodes:
            if isinstance(node, SetDataAsParameterNode):
                shouldAddSetDataAsParamNode = False
        if shouldAddSetDataAsParamNode:
            endpoint.pipeline.add(SetDataAsParameterNode(), 10000)
        # Done
        return endpoint

class AnonymousSubscribeEndpoint(object):
    """The anonymous subscribe endpoint
    """
    def __init__(self, *bindings, **kwargs):
        """Create a new AnonymousSubscribeEndpoint
        Parameters:
            bindings                    A list of tuple (exchange, routingKey)
        """
        self.id = str(uuid4())
        self.bindings = bindings
        self.ack = kwargs.get('ack', False)

    def __call__(self, endpoint):
        """Attach to endpoint object
        Parameters:
            endpoint                    The protocol.Endpoint object
        Returns:
            The protocol.Endpoint object
        """
        # Add this web endpoint to the endpoint object
        if ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY in endpoint.children:
            endpoint.children[ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY][self.id] = self
        else:
            endpoint.children[ENDPOINT_CHILDREN_RABBITMQ_SUBCRIBE_ENDPOINT_KEY] = { self.id: self }
        # Add execution node
        shouldAddSetDataAsParamNode = True
        for node in endpoint.pipeline.nodes:
            if isinstance(node, SetDataAsParameterNode):
                shouldAddSetDataAsParamNode = False
        if shouldAddSetDataAsParamNode:
            endpoint.pipeline.add(SetDataAsParameterNode(), 10000)
        # Done
        return endpoint

class RPCEndpoint(object):
    """The RPC endpoint
    """
    def __init__(self):
        """Create a new RPCEndpoint
        """
        raise NotImplementedError
