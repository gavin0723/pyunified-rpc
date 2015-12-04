# encoding=utf8
# The endpoint pipeline execution nodes

"""The endpoint pipeline execution nodes
"""

from unifiedrpc.errors import BadRequestError
from unifiedrpc.protocol.endpoint import ExecutionNode

class SetDataAsParameterNode(ExecutionNode):
    """The parameter value selection node
    NOTE:
        This execution node is used to set the parsed data from content to parameters
    """
    allowedAdapterTypes = [ 'rabbitmq' ]

    def __call__(self, context, next):
        """Run this node logic
        """
        if not context.request.content.data is None:
            context.dispatcher.params['data'] = context.request.content.data
        # Run next node
        return next()
