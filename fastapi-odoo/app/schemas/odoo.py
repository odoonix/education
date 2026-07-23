from pydantic import BaseModel


class OdooHealth(BaseModel):
    connected: bool
    version: str | None = None
    uid: int | None = None
    detail: str | None = None
