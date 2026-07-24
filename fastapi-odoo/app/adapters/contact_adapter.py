from app.adapters.odoo_client import OdooClient
from app.schemas.contact import OdooContact


class ContactAdapter:
    def __init__(self, client: OdooClient) -> None:
        self._client = client

    def fetch_contacts(self) -> list[OdooContact]:
        records = self._client.search_read(
            model="res.partner",
            fields=[
                "id",
                "name",
                "email",
                "phone",
                "mobile",
            ],
        )

        return [
            OdooContact.model_validate(record)
            for record in records
        ]