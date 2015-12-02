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

    def __call__(self, s):
        """Convert string to bool
        """
        s = s.lower()
        if s in self.trues:
            return True
        if s in self.falses:
            return False
        raise ValueError('Cannot convert to bool')

boolean = Bool([ '1', 'true', 'yes', 'on' ], [ '0', 'false', 'no', 'off' ])

