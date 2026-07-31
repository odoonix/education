from __future__ import annotations

import signal
from types import FrameType


class ShutdownFlag:
    def __init__(self) -> None:
        self.cancelled = False

    def request(self, _signum: int, _frame: FrameType | None) -> None:
        self.cancelled = True


def install_shutdown_handlers(flag: ShutdownFlag) -> None:
    signal.signal(signal.SIGINT, flag.request)
    signal.signal(signal.SIGTERM, flag.request)
