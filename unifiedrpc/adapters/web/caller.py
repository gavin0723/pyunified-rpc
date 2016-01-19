# encoding=utf8
# The endpoint pipeline execution nodes

"""The endpoint pipeline execution nodes
"""

from werkzeug.wrappers import Response as WKResponse

from unifiedrpc.errors import BadRequestError
from unifiedrpc.protocol import Caller

from util import getContentType

class ResponseFinalBuildCaller(Caller):
    """The final build of response
    """
    allowedAdapterTypes = [ 'web' ]

    def __call__(self, context, next):
        """Do final response build
        Returns:
            werkzeug.wrappers.Response object
        """
        value = next()
        # Check the response
        if isinstance(value, WKResponse):
            return value
        # Build the response
        # Set session
        if context.adapter.sessionManager:
            context.adapter.sessionManager.set(context.session, context.response)
        # Set the value to container
        context.response.container.setValue(value)
        # Build context
        context.response.content = context.components.contentBuilder.build(context)
        # Return the response
        return WKResponse(
            status = context.response.status,
            headers = context.response.headers,
            response = (context.response.content, ) if isinstance(context.response.content, basestring) else context.response.content,
            content_type = getContentType(context.response.mimeType, context.response.encoding)
            )

class ParameterValueSelectionCaller(Caller):
    """The parameter value selection caller
    NOTE:
        This calleris used to select the parameters from url / query array parameter values by endpoint config
    """
    allowedAdapterTypes = [ 'web' ]

    def __call__(self, context, next):
        """Run this node logic
        """
        webEndpoint, params = context.webEndpoint, context.params
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
