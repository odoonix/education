from pydantic_settings import BaseSettings

from functools import lru_cache

class Settings(BaseSettings):
    # Odoo
    ODOO_URL: str
    ODOO_DB: str
    ODOO_API_KEY: str

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5433

    # App
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()