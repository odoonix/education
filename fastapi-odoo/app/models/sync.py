from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SyncStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(primary_key=True)

    status: Mapped[SyncStatus] = mapped_column(
        String(20),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    contacts_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    products_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    sale_orders_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    sale_order_lines_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    logs: Mapped[list["SyncLog"]] = relationship(
        back_populates="sync_run",
        cascade="all, delete-orphan",
    )


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    sync_run_id: Mapped[int] = mapped_column(
        ForeignKey("sync_runs.id"),
        nullable=False,
    )

    level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    entity: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    action: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    record_odoo_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sync_run: Mapped["SyncRun"] = relationship(
        back_populates="logs",
    )