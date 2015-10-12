# encoding=utf8
# The basic parameter types

"""The basic parameter types
"""

class Bool(object):
    """Bool type
    """
    def __init__(self, trues, falses):
        """Create a new Bool type
        """
        self.trues = trues
        self.falses = falses

boolean = Bool([ '1', 'true', 'yes', 'on' ], [ '0', 'false', 'no', 'off' ])

