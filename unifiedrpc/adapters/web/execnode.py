# encoding=utf8
# The endpoint pipeline execution nodes

"""The endpoint pipeline execution nodes
"""

from unifiedrpc.errors import BadRequestError
from unifiedrpc.protocol.endpoint import ExecutionNode

class ParameterValueSelectionNode(ExecutionNode):
    """The parameter value selection node
    NOTE:
        This execution node is used to select the parameters from url / query array parameter values by endpoint config
    """
    allowedAdapterTypes = [ 'web' ]

    def __call__(self, context, next):
        """Run this node logic
        """
        webEndpoint, params = context.dispatcher.webEndpoint, context.dispatcher.params
        # Check it
        if webEndpoint.allowedMultiParams:
            if webEndpoint.allowedMultiParams == '*':
                # All parameters should be array
                for key in params.iterkeys():
                    value = params[key]
                    if not isinstance(value, (list, tuple)):
                        params[key] = (value, )
            elif isinstance(webEndpoint.allowedMultiParams, (list, tuple)):
                # The listed parameter should be array
                for key in params.keys():
                    value = params[key]
                    if key in webEndpoint.allowedMultiParams:
                        # Must be array
                        if not isinstance(value, (tuple, list)):
                            params[key] = (value, )
                    elif isinstance(value, (tuple, list)):
                        # Must not be array
                        if len(value) == 0:
                            del params[key]
                        elif len(value) == 1:
                            params[key] = value[0]
                        else:
                            raise BadRequestError
            else:
                # Unsupported value
                raise ValueError('Unsupported allowedMultiParams value [%s]' % webEndpoint.allowedMultiParams)
        else:
            # Unwrap all parameters out of array
            for key in params.keys():
                value = params[key]
                if isinstance(value, (tuple, list)):
                    # Must not be array
                    if len(value) == 0:
                        del params[key]
                    elif len(value) == 1:
                        params[key] = value[0]
                    else:
                        raise BadRequestError
        # Run next node
        return next()

