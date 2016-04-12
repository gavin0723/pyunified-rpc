# encoding=utf8
# The utility

"""The utility
"""

try:
    import simplejson as json
    from simplejson import JSONDecodeError
except ImportError:
    import json
    JSONDecodeError = ValueError

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
