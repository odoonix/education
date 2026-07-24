from __future__ import annotations

from functools import cached_property
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from odoo_sync.domain.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MIN_PAGE_SIZE


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    odoo_url: str = "http://odoo:8069"
    odoo_database: str = "odoo"
    odoo_username: str = "admin"
    odoo_password: str = "admin"
    odoo_request_timeout: float = Field(default=20.0, gt=0, le=120)
    retry_attempts: int = Field(default=3, ge=1, le=10)
    retry_delay_seconds: float = Field(default=0.5, ge=0, le=30)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE)

    sync_db_host: str = "sync-db"
    sync_db_port: int = Field(default=5432, ge=1, le=65535)
    sync_db_database: str = "odoo_sync"
    sync_db_username: str = "odoo_sync"
    sync_db_password: str = "odoo_sync"
    sync_lock_key: int = 741_017_001

    log_level: str = "INFO"
    log_format: Literal["text", "json"] = "json"

    @cached_property
    def sync_database_url(self) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.sync_db_username,
            password=self.sync_db_password,
            host=self.sync_db_host,
            port=self.sync_db_port,
            database=self.sync_db_database,
        )
