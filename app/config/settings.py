from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator, ValidationInfo
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):

    model_config = SettingsConfigDict(case_sensitive=True)

    # Database
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str

    # Odoo
    ODOO_URL: str
    ODOO_USERNAME: str
    ODOO_DB_NAME: str
    ODOO_PASSWORD: str

    POSTGRES_DATABASE_URL: PostgresDsn | None = None

    @field_validator("POSTGRES_DATABASE_URL", mode="after")
    def assemble_postgresql_url(cls, v: Optional[str], values: ValidationInfo):
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data["DATABASE_USER"],
            password=values.data["DATABASE_PASSWORD"],
            host=values.data["DATABASE_HOST"],
            port=int(values.data["DATABASE_PORT"]),
            path=values.data["DATABASE_NAME"],
        )


class GetSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        case_sensitive=True
    )

def get_settings() -> Settings:
    return GetSettings()


settings = get_settings()