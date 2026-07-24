from dataclasses import dataclass


@dataclass
class Contact:
    odoo_id: int
    name: str
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None