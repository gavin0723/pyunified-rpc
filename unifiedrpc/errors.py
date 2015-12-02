# encoding=utf8
# The errors

"""The errors
"""

class RPCError(Exception):
    """The unified RPC error
    """
    def __init__(self, code = None, reason = None, detail = None):
        """Create a new RPCError
        """
        self.code = code
        self.reason = reason
        self.detail = detail

    def __str__(self):
        """Convert to string
        """
        return '%s: #%s - [%s] - [%s]' % (type(self).__name__, self.code or '', self.reason or '', self.detail or '')

    def __repr__(self):
        """Repr
        """
        return str(self)

class BadRequestError(RPCError):
    """The bad request error
    """

class BadRequestParameterError(BadRequestError):
    """The bad request parameter error
    """
    def __init__(self, parameter, code = None, reason = None, detail = None):
        """Create a new BadRequestParameterError
        """
        self.parameter = parameter
        # Super
        super(BadRequestParameterError, self).__init__(code, reason, detail)

    def __str__(self):
        """Convert to string
        """
        return '%s: #%s - [%s] - [%s] - [%s]' % (type(self).__name__, self.code or '', self.parameter, self.reason or '', self.detail or '')

class BadRequestBodyError(BadRequestError):
    """The bad request body error
    """

class UnauthorizedError(RPCError):
    """The unauthorized error
    """

class ForbiddenError(RPCError):
    """The forbidden error
    """

class NotFoundError(RPCError):
    """The not found error
    """

class NotAcceptableError(RPCError):
    """The not acceptable error
    """

class RequestTimeoutError(RPCError):
    """The request timeout error
    """

class LengthRequiredError(RPCError):
    """The length required error
    """

class RequestEntityTooLargeError(RPCError):
    """The request entity too large error
    """

class UnsupportedMediaTypeError(RPCError):
    """The unsupported media type error
    """
    def __init__(self, mimeType, code = None, reason = None, detail = None):
        """Create a new UnsupportedMediaTypeError
        """
        self.mimeType = mimeType
        # Super
        super(UnsupportedMediaTypeError, self).__init__(code, reason, detail)

    def __str__(self):
        """Convert to string
        """
        return '%s: #%s - [%s] - [%s] - [%s]' % (type(self).__name__, self.code or '', self.mimeType, self.reason or '', self.detail or '')

class InternalServerError(RPCError):
    """The internal server error
    """

# -*- ---------- The error codes and messages --------- -*-

ERRCODE_UNDEFINED                                           = 0x0                   # The undefined error

ERRCODE_BADREQUEST_INVALID_PARAMETER_TYPE                   = 0x0001001             # The parameter is invalid (cannot convert to the declared data type)
ERRCODE_BADREQUEST_UNKNOWN_PARAMETER                        = 0x0001002             # The parameter is unknown
ERRCODE_BADREQUEST_LACK_OF_PARAMETER                        = 0x0001003             # Lack of the necessary parameter
ERRCODE_BADREQUEST_INVALID_PARAMETER_COMBINATION            = 0x000104              # Invalid parameter combination
ERRCODE_BADREQUEST_LACK_OF_BODY                             = 0x0001010             # Lack of the request body
ERRCODE_BADREQUEST_INVALID_BODY                             = 0x0001011             # The request body is invalid
ERRCODE_BADREQUEST_BODY_NOT_SATISFIED                       = 0x0001012             # The request body is not satified with the specification

ERRCODE_UNAUTHORIZED_INVALID_CREDENTIAL                     = 0x0002001             # The provided credential is invalid
ERRCODE_UNAUTHORIZED_BLOCKED                                = 0x0002002             # The authentication or authorization is blocked by someone
