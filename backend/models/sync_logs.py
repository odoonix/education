from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    DateTime,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base


class SyncLog(Base):

    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    sync_run_id: Mapped[int] = mapped_column(
        ForeignKey("sync_runs.id")
    )

    level: Mapped[str] = mapped_column(
        String(20)
    )

    message: Mapped[str] = mapped_column(
        Text
    )

    record_reference: Mapped[str | None] = mapped_column(
        String(255)
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )

    run = relationship(
        "SyncRun",
        back_populates="logs",
    )