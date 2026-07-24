from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

import os

class Settings(BaseSettings):

    APP_NAME: str = "Odoo Sync Service"

    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"
        )

    ODOO_URL: str

    ODOO_DATABASE: str

    ODOO_USERNAME: str

    ODOO_PASSWORD: str
    
    log_level = os.environ.get("LOG_LEVEL", "INFO"),
    
    run_mode: str
    
    sync_interval_seconds: int
    
    log_level: str

@lru_cache
def get_settings() -> Settings:
    return Settings()