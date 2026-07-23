from pydantic import BaseModel


class OdooPartnerCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None


class OdooPartnerRead(BaseModel):
    id: int
    name: str
    email: str | None = None
    phone: str | None = None


class OdooHealth(BaseModel):
    connected: bool
    version: str | None = None
    uid: int | None = None
    detail: str | None = None
