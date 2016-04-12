# encoding=utf8
# The base adapter definitions

"""The base adapter definitions
"""

from threading import Lock, Event

from unifiedrpc.protocol.execution import EndpointExecutionStage

class Adapter(object):
    """The adapter base class
    """
    GLOCK = Lock()

    def __init__(self, configs = None, stage = None):
        """Create a new AdapterBase
        """
        self._configs = configs or {}
        self._stage = stage or EndpointExecutionStage()
        self._server = None
        # Initialize the flags
        self._started = False
        self._stopEvent = Event()

    def __start__(self):
        """Start this adapter
        """
        raise NotImplementedError

    def __stop__(self):
        """Stop this adapter
        """
        raise NotImplementedError

    @property
    def started(self):
        """Get if the adapter is started
        """
        return self._started

    @property
    def stopEvent(self):
        """The stop event
        """
        return self._stopEvent

    def attach(self, server):
        """Attach this adapter to a server
        """
        if self._server:
            raise ValueError('This adapter has already attached to a server')
        self._server = server

    def start(self):
        """Start
        """
        with self.GLOCK:
            # Check flag
            if not self._server:
                raise ValueError('Adapter is not attached to a server')
            if self._started:
                raise ValueError('Adapter is already started')
            # Start adapter
            self.__start__()
            # Set flags
            self._started = True
            self._stopEvent.clear()

    def stop(self):
        """Stop
        """
        with self.GLOCK:
            # Check flag
            if not self._started:
                raise ValueError('Server is not started')
            # Stop adapter
            self.__stop__()
            # Set flags
            self._started = False
            self._stopEvent.set()
