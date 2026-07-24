from dataclasses import dataclass


@dataclass
class ContactDTO:
    odoo_id: int
    name: str
    email: str | None
    phone: str | None
    mobile: str | None