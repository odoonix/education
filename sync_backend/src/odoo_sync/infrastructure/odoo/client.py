from __future__ import annotations

import logging
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from xmlrpc.client import Fault, ServerProxy

from odoo_sync.config import Settings
from odoo_sync.infrastructure.odoo.exceptions import OdooAuthenticationError
from odoo_sync.infrastructure.odoo.transport import TimeoutTransport, is_transient_error


class OdooClient:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger
        transport = TimeoutTransport(settings.odoo_request_timeout)
        self.common = ServerProxy(
            f"{settings.odoo_url}/xmlrpc/2/common", transport=transport, allow_none=True
        )
        self.object = ServerProxy(
            f"{settings.odoo_url}/xmlrpc/2/object", transport=transport, allow_none=True
        )
        self._uid: int | None = None

    @property
    def uid(self) -> int:
        if self._uid is None:
            uid = self._call_common(
                "authenticate",
                self.settings.odoo_database,
                self.settings.odoo_username,
                self.settings.odoo_password,
                {},
            )
            if not isinstance(uid, int):
                raise OdooAuthenticationError("Odoo authentication failed")
            self._uid = uid
        return self._uid

    def search_read(
        self,
        model: str,
        domain: list[Any],
        fields: Sequence[str],
        *,
        limit: int,
        order: str = "id asc",
    ) -> list[dict[str, Any]]:
        result = self._execute_kw(
            model, "search_read", [domain], {"fields": list(fields), "limit": limit, "order": order}
        )
        if not isinstance(result, list):
            raise RuntimeError("Odoo search_read returned unexpected result")
        return [row for row in result if isinstance(row, dict)]

    def now(self) -> datetime:
        return datetime.now(UTC)

    def _execute_kw(self, model: str, method: str, args: list[Any], kwargs: dict[str, Any]) -> Any:
        return self._retry(
            lambda: self.object.execute_kw(
                self.settings.odoo_database,
                self.uid,
                self.settings.odoo_password,
                model,
                method,
                args,
                kwargs,
            )
        )

    def _call_common(self, method: str, *args: Any) -> Any:
        return self._retry(lambda: getattr(self.common, method)(*args))

    def _retry(self, call: Any) -> Any:
        last: BaseException | None = None
        for attempt in range(1, self.settings.retry_attempts + 1):
            try:
                return call()
            except Fault:
                raise
            except Exception as exc:
                if not is_transient_error(exc) or attempt >= self.settings.retry_attempts:
                    raise
                last = exc
                self.logger.warning(
                    "retrying transient Odoo request",
                    extra={"attempt": attempt, "error_type": type(exc).__name__},
                )
                time.sleep(self.settings.retry_delay_seconds * attempt)
        raise RuntimeError("retry attempts exhausted") from last
