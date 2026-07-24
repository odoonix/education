
import signal


class ShutdownHandler:
    def __init__(self):
        self._shutdown_requested = False
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum, frame):
        self._shutdown_requested = True

    @property
    def shutdown_requested(self) -> bool:
        return self._shutdown_requested