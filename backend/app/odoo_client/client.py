import logging
import xmlrpc.client
from typing import Any, Iterator

from app.exceptions import OdooConnectionError
from app.retry import retry

logger = logging.getLogger(__name__)


class OdooClient:
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self._uid: int | None = None
        self._common = xmlrpc.client.ServerProxy(
            f"{url}/xmlrpc/2/common", allow_none=True
        )
        self._models = xmlrpc.client.ServerProxy(
            f"{url}/xmlrpc/2/object", allow_none=True
        )

    @retry(
        max_attempts=5,
        initial_delay=2.0,
        exceptions=(ConnectionError, OSError, xmlrpc.client.ProtocolError),
    )
    def authenticate(self) -> int:
        try:
            uid = self._common.authenticate(self.db, self.username, self.password, {})
        except (ConnectionError, OSError, xmlrpc.client.ProtocolError):
            raise
        except Exception as exc:
            raise OdooConnectionError(f"authentication with Odoo failed: {exc}") from exc

        if not uid:
            raise OdooConnectionError(
                "Authentication with Odoo failed; check database/username/password"
            )
        self._uid = uid
        logger.info("connection to Odoo established (db=%s, uid=%s)", self.db, uid)
        return uid

    @property
    def uid(self) -> int:
        if self._uid is None:
            self.authenticate()
        return self._uid  # type: ignore[return-value]

    @retry(
        max_attempts=3,
        initial_delay=2.0,
        exceptions=(ConnectionError, OSError, xmlrpc.client.ProtocolError),
    )
    def _execute_kw(self, model: str, method: str, args: list, kwargs: dict | None = None):
        try:
            return self._models.execute_kw(
                self.db, self.uid, self.password, model, method, args, kwargs or {}
            )
        except (ConnectionError, OSError, xmlrpc.client.ProtocolError):
            raise
        except Exception as exc:  # noqa: BLE001
            raise OdooConnectionError(
                f"فراخوانی {model}.{method} با خطا مواجه شد: {exc}"
            ) from exc

    def search_read(
        self,
        model: str,
        domain: list,
        fields: list[str],
        offset: int = 0,
        limit: int = 100,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {"offset": offset, "limit": limit}
        if order:
            kwargs["order"] = order
        return self._execute_kw(model, "search_read", [domain, fields], kwargs)

    def iter_all(
        self,
        model: str,
        domain: list,
        fields: list[str],
        batch_size: int = 100,
    ) -> Iterator[dict[str, Any]]:
        """
        fetch all records of a model in a paginated way (page by page) and
        return a generator of records.
        """
        offset = 0
        while True:
            batch = self.search_read(
                model, domain, fields, offset=offset, limit=batch_size
            )
            if not batch:
                return
            yield from batch
            if len(batch) < batch_size:
                return
            offset += batch_size

    def create(self, model: str, values: dict) -> int:
        return self._execute_kw(model, "create", [values])
