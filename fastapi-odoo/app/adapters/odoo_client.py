import xmlrpc.client

from app.config.settings import get_settings


class OdooClient:
    def __init__(self) -> None:
        settings = get_settings()

        self._database = settings.odoo_db
        self._username = settings.odoo_username
        self._password = settings.odoo_password

        self._common = xmlrpc.client.ServerProxy(
            f"{settings.odoo_url}/xmlrpc/2/common",
        )

        self._models = xmlrpc.client.ServerProxy(
            f"{settings.odoo_url}/xmlrpc/2/object",
        )

        self._uid = self._authenticate()

    def _authenticate(self) -> int:
        uid = self._common.authenticate(
            self._database,
            self._username,
            self._password,
            {},
        )

        if not uid:
            raise RuntimeError(
                "Failed to authenticate with Odoo",
            )

        return uid

    def search_read(
            self,
            model: str,
            fields: list[str],
            domain: list | None = None,
    ) -> list[dict]:
        return self._models.execute_kw(
            self._database,
            self._uid,
            self._password,
            model,
            "search_read",
            [domain or []],
            {
                "fields": fields,
            },
        )
