from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    DATABASE_URL: str

    ODOO_URL: str
    ODOO_DATABASE: str
    ODOO_ADMIN_EMAIL: str
    ODOO_ADMIN_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
