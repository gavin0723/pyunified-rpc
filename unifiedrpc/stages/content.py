# encoding=utf8

""" The content related execution node
    Author: lipixun
    Created Time : Sat 21 Nov 2015 10:08:05 PM CST

    File Name: content.py
    Description:

"""

from unifiedrpc import context
from unifiedrpc.errors import BadRequestBodyError, ERRCODE_BADREQUEST_LACK_OF_BODY, ERRCODE_BADREQUEST_INVALID_BODY

class DataValidator(object):
    """The data validator
    """
    def __init__(self, dataType, notEmpty):
        """Create a new DataValidator
        """
        self.dataType = dataType
        self.notEmpty = notEmpty

    def __call__(self):
        """Validate the request data
        """
        if not context.request.content:
            raise BadRequestBodyError(ERRCODE_BADREQUEST_LACK_OF_BODY)
        if not isinstance(context.request.content.data, self.dataType):
            raise BadRequestBodyError(ERRCODE_BADREQUEST_INVALID_BODY)
        if self.notEmpty and not context.request.content.data:
            raise BadRequestBodyError(ERRCODE_BADREQUEST_INVALID_BODY)
