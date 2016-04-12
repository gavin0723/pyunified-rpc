# encoding=utf8
# The parameter related execution node

"""The parameter related execution node
"""

from unifiedrpc import context
from unifiedrpc.errors import BadRequestParameterError, ERRCODE_BADREQUEST_INVALID_PARAMETER_TYPE
from unifiedrpc.protocol import CONFIG_ENDPOINT_PARAMETER_TYPE

class ParameterConverter(object):
    """The parameter converter
    """
    def __call__(self, next):
        """Convert parameter
        """
        params, types = context.dispatchResult.parameters, context.dispatchResult.endpoint.getConfig(CONFIG_ENDPOINT_PARAMETER_TYPE)
        if params and types:
            for param, _type in types.iteritems():
                if param in params:
                    try:
                        params[param] = _type(params[param])
                    except Exception as error:
                        raise BadRequestParameterError(param, ERRCODE_BADREQUEST_INVALID_PARAMETER_TYPE, error.message)
        # Run next
        return next()
