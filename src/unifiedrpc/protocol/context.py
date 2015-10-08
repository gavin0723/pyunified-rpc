# encoding=utf8
# The context object

"""The context object
"""

import threading

class Context(object):
    """The context
    """
    @classmethod
    def current(cls):
        """Get the current context
        """
    @classmethod
    def setCurrent(cls, context):
        """Set the current context
        """

