from datetime import datetime

from sqlalchemy import String, DateTime, func

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(primary_key=True)

    operation_type: Mapped[str] = mapped_column(String(50))   # مثلا "contacts_sync", "full_sync"

    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[datetime | None]

    records_fetched: Mapped[int] = mapped_column(default=0)
    records_created: Mapped[int] = mapped_column(default=0)
    records_updated: Mapped[int] = mapped_column(default=0)
    errors_count: Mapped[int] = mapped_column(default=0)

    status: Mapped[str] = mapped_column(String(30))   # running / success / failed

    logs = relationship("SyncLog", back_populates="run")