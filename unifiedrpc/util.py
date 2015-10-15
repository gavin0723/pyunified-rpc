# encoding=utf8
# The utility

"""The utility
"""

try:
    import simplejson as json

    from simplejson import JSONDecodeError
except ImportError:
    import json

    from json import JSONDecodeError

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

