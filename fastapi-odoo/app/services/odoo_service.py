from app.integrations.odoo_client import OdooClient, OdooClientError
from app.schemas.odoo import OdooHealth


class OdooService:
    def __init__(self, client: OdooClient | None = None) -> None:
        self.client = client or OdooClient()

    def health(self) -> OdooHealth:
        return self.client.health()

    def seed_demo_data(self) -> dict[str, int | list[int]]:
        try:
            return self.client.seed_demo_data()
        except OdooClientError as exc:
            raise RuntimeError(str(exc)) from exc
