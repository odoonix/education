from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "FastAPI Odoo Service"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me"

    DATABASE_URL: str = "postgresql+psycopg2://app:app@localhost:5432/fastapi_app"

    ODOO_HOST: str = "localhost"
    ODOO_PORT: int = 8069
    ODOO_DB: str = "odoo"
    ODOO_USER: str = "admin"
    ODOO_PASSWORD: str = "admin"

    @property
    def odoo_url(self) -> str:
        return f"http://{self.ODOO_HOST}:{self.ODOO_PORT}"


settings = Settings()
