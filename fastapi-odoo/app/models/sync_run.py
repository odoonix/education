from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sync_type: Mapped[str] = mapped_column(String(255), nullable=False)
    sync_start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sync_end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_records: Mapped[int] = mapped_column(Integer, nullable=False)
    stored_records: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_records: Mapped[int] = mapped_column(Integer, nullable=False)
    error_records: Mapped[int] = mapped_column(Integer, nullable=False)
    sync_error: Mapped[str | None] = mapped_column(String(255), nullable=True)
        
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    logs: Mapped[list["SyncLog"]] = relationship(
        "SyncLog",
        back_populates="sync_run",
    )

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sync_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("sync_runs.id"), nullable=False)
    sync_run: Mapped["SyncRun"] = relationship("SyncRun", back_populates="logs")
    level: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
