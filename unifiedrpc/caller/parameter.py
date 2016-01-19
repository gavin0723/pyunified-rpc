# encoding=utf8
# The parameter related execution node

"""The parameter related execution node
"""

from unifiedrpc.protocol import Caller, CONFIG_ENDPOINT_PARAMETER_TYPE
from unifiedrpc.errors import BadRequestParameterError, ERRCODE_BADREQUEST_INVALID_PARAMETER_TYPE

class ParameterTypeConversionCaller(Caller):
    """The parameter type conversion caller
    """
    def __call__(self, context, next):
        """Run the conversion logic
        """
        params, types = context.params, context.endpoint.configs.get(CONFIG_ENDPOINT_PARAMETER_TYPE)
        if params and types:
            for param, _type in types.iteritems():
                if param in params:
                    try:
                        params[param] = _type(params[param])
                    except Exception as error:
                        raise BadRequestParameterError(param, ERRCODE_BADREQUEST_INVALID_PARAMETER_TYPE, error.message)
        # Run next
        return next()
