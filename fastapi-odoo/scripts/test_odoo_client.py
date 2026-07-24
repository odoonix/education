from app.adapters.odoo_client import OdooClient


client = OdooClient()

contacts = client.search_read(
    model="res.partner",
    fields=[
        "id",
        "name",
        "email",
        "phone",
        "mobile",
    ],
)

for contact in contacts:
    print(contact)