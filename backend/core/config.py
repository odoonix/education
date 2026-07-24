from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    odoo_url: str = "http://localhost:8069"
    odoo_db: str = "odoo"
    odoo_username: str = "admin"
    odoo_password: str = "admin"

    database_url: str
    log_level: str = "INFO"


def get_settings():
    return Settings()