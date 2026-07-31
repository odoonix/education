from __future__ import annotations

import socket
from http.client import HTTPConnection
from xmlrpc.client import Transport


class TimeoutTransport(Transport):
    def __init__(self, timeout: float) -> None:
        super().__init__()
        self.timeout = timeout

    def make_connection(self, host: tuple[str, dict[str, str]] | str) -> HTTPConnection:
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn


def is_transient_error(exc: BaseException) -> bool:
    return isinstance(exc, TimeoutError | socket.timeout | ConnectionError | OSError)
