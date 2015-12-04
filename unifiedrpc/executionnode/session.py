# encoding=utf8

""" The session execnode
    Author: lipixun
    Created Time : Fri 04 Dec 2015 10:08:48 PM CST

    File Name: session.py
    Description:

"""

from unifiedrpc import context
from unifiedrpc.protocol.endpoint import ExecutionNode

class SessionValidationNode(ExecutionNode):
    """The session validation node
    """
    def __init__(self, key, validator, error):
        """Create a new SessionValidationNode
        """
        self.key = key
        self.validator = validator
        self.error = error

    def __call__(self, context, next):
        """Run the data validation
        """
        if not context.session or not self.key in context.session:
            error = ValueError('Session [%s] not found' % self.key)
            if self.error:
                self.error(error)
            else:
                raise error
        # Validate
        value = context.session[self.key]
        if self.validator:
            try:
                self.validator(value)
            except Exception as error:
                if self.error:
                    self.error(error)
                else:
                    raise
        # Done
        return next()

