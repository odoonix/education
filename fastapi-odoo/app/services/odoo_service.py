from app.integrations.odoo_client import OdooClient, OdooClientError
from app.schemas.odoo import OdooHealth, OdooPartnerCreate, OdooPartnerRead


class OdooService:
    def __init__(self, client: OdooClient | None = None) -> None:
        self.client = client or OdooClient()

    def health(self) -> OdooHealth:
        return self.client.health()

    def list_partners(self, limit: int = 20) -> list[OdooPartnerRead]:
        try:
            return self.client.list_partners(limit=limit)
        except OdooClientError as exc:
            raise RuntimeError(str(exc)) from exc

    def create_partner(self, payload: OdooPartnerCreate) -> OdooPartnerRead:
        try:
            return self.client.create_partner(payload)
        except OdooClientError as exc:
            raise RuntimeError(str(exc)) from exc

    def seed_demo_data(self) -> dict[str, int | list[int]]:
        try:
            return self.client.seed_demo_data()
        except OdooClientError as exc:
            raise RuntimeError(str(exc)) from exc
