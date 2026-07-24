from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    odoo_url: str = "http://localhost:8069"
    odoo_db: str = "exam_db"
    odoo_username: str = "admin"
    odoo_password: str = "admin"

    app_db_host: str = "localhost"
    app_db_port: int = 5433
    app_db_name: str = "sync_backend"
    app_db_user: str = "sync_user"
    app_db_password: str = "sync_password"

    @property
    def app_db_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.app_db_user}:{self.app_db_password}"
            f"@{self.app_db_host}:{self.app_db_port}/{self.app_db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()