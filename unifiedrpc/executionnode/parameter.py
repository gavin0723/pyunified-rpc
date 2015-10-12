# encoding=utf8
# The parameter related execution node

"""The parameter related execution node
"""

from unifiedrpc.protocol.endpoint import ExecutionNode
from unifiedrpc.errors import BadRequestParameterError, ERRCODE_BADREQUEST_INVALID_PARAMETER_TYPE

class ParameterTypeConversionNode(ExecutionNode):
    """The parameter type conversion node
    """
    def __call__(self, context, next):
        """Run the conversion logic
        """
        params, types = context.dispatch.params, context.dispatch.endpoint.signature.parameter.types
        for param, paramType in types.iteritems():
            if param in params:
                try:
                    params[param] = paramType(params[param])
                except Exception as error:
                    raise BadRequestParameterError(param, ERRCODE_BADREQUEST_INVALID_PARAMETER_TYPE, error.message)
        # Run next
        return next()

