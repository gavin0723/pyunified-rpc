# encoding=utf8

""" The error handlers
    Author: lipixun
    Created Time : 三  6/ 8 16:54:37 2016

    File Name: errorhandlers.py
    Description:

"""

import logging

from unifiedrpc.util import json
from unifiedrpc.errors import *

ERROR_MAPPING = {
    400     : BadRequestError,
    401     : UnauthorizedError,
    403     : ForbiddenError,
    404     : NotFoundError,
    405     : MethodNotAllowedError,
    406     : NotAcceptableError,
    408     : RequestTimeoutError,
    411     : LengthRequiredError,
    413     : RequestEntityTooLargeError,
    415     : UnsupportedMediaTypeError,
    500     : InternalServerError,
    }

class UnhandledHttpError(RPCError):
    """The unhandled http error
    """
    def __init__(self, httpStatusCode):
        """Create a new UnhandledHttpError
        """
        self.httpStatusCode = httpStatusCode
        # Super
        super(UnhandledHttpError, self).__init__()

class Http2UnifiedRPCErrorHandler(object):
    """The http 2 unifiedrpc error handler
    This class will handle the requests response, raise error by unified-rpc errors
    """
    logger = logging.getLogger('unifiedrpc.adapters.requests.http2UnifiedRPCErrorHandler')

    def __init__(self, mapping = None):
        """Create a new HttpErrorHandler
        """
        self.mapping = mapping or ERROR_MAPPING

    def getUnifiedRPCError(self, response):
        """Get unifiedrpc error from response
        """
        # HTTP 200
        if response.status_code in (200, 201, 202):
            return
        # Find error from error mapping
        initKwargs = {}
        errorClass = self.mapping.get(response.status_code)
        if not errorClass:
            # OK, error class not found
            errorClass = UnhandledHttpError
            initKwargs['httpStatusCode'] = response.status_code
        # Try to decode the content as standard error
        # TODO: Support handling more response content format
        # Try to get error from header
        if 'X-SERVER-ERROR' in response.headers:
            # Load from header
            try:
                error = json.loads(response.headers['X-SERVER-ERROR'])
                if error.get('code'):
                    initKwargs['code'] = error['code']
                if error.get('reason'):
                    initKwargs['reason'] = error['reason']
                if error.get('detail'):
                    initKwargs['detail'] = error['detail']
            except:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.exception('Failed to load error content, skip')
        else:
            # Load from content
            try:
                error = json.loads(response.content)
                if error.get('code'):
                    initKwargs['code'] = error['code']
                if error.get('reason'):
                    initKwargs['reason'] = error['reason']
                if error.get('detail'):
                    initKwargs['detail'] = error['detail']
            except:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.exception('Failed to load error content, skip')
        # Done
        return errorClass(**initKwargs)

    def handle(self, response):
        """Raise error if any error occurred
        Returns:
            None if no error occurred
        """
        error = self.getUnifiedRPCError(response)
        if error:
            raise error
