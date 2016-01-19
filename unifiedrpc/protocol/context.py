# encoding=utf8
# The context object

"""The context object
"""

from unifiedrpc import CONFIG_REQUEST_CONTENT_PARSER, CONFIG_RESPONSE_CONTENT_CONTAINER, CONFIG_RESPONSE_CONTENT_BUILDER

class Context(object):
    """The context class
    Attributes:
        runtime                             The runtime object
        adapter                             The adapter of current request
        request
        session
        endpoint                            The active endpoint
        response                            The response of current request
    """
    def __init__(self, runtime, adapter, request = None, session = None, endpoint = None, parameters = None, response = None):
        """Create a new context
        """
        self.runtime = runtime
        self.adapter = adapter
        self.request = request
        self.session = session
        self.response = response
        self.endpoint = endpoint
        self.parameters = parameters
        self.components = Components()
        # Initialize the components: contentParser, contentBuilder, contentContainer
        self.components.contentParser = runtime.configs.get(CONFIG_REQUEST_CONTENT_PARSER)
        self.components.contentBuilder = runtime.configs.get(CONFIG_RESPONSE_CONTENT_BUILDER)
        self.components.contentContainer = runtime.configs.get(CONFIG_RESPONSE_CONTENT_CONTAINER)

class Components(object):
    """The components
    """
    pass
