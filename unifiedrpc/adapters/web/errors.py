# encoding=utf8
# The web adapter error

"""The web adapter error
"""

from unifiedrpc.errors import *

# Bind errors to http status code
ERROR_BINDINGS = {
    BadRequestError:                400,
    BadRequestParameterError:       400,
    BadRequestBodyError:            400,
    UnauthorizedError:              401,
    ForbiddenError:                 403,
    NotFoundError:                  404,
    MethodNotAllowedError:          405,
    NotAcceptableError:             406,
    RequestTimeoutError:            408,
    LengthRequiredError:            411,
    RequestEntityTooLargeError:     413,
    UnsupportedMediaTypeError:      415,
    InternalServerError:            500,
}
