from pydantic import BaseModel, Field, field_validator


class OdooContact(BaseModel):
    odoo_id: int = Field(alias="id")
    name: str
    email: str | None
    phone: str | None
    mobile: str | None

    @field_validator(
        "email",
        "phone",
        "mobile",
        mode="before",
    )
    @classmethod
    def normalize_empty_values(
        cls,
        value: str | bool | None,
    ) -> str | None:
        if value is False:
            return None

        return value

    model_config = {
        "populate_by_name": True,
    }