from __future__ import annotations

from odoo_sync.domain.sync import SyncRunSummary


def format_summary(summary: SyncRunSummary) -> str:
    return "\n".join(
        [
            f"sync_type={summary.sync_type.value}",
            f"start_time={summary.started_at.isoformat()}",
            f"finish_time={summary.finished_at.isoformat() if summary.finished_at else ''}",
            f"fetched_count={summary.counters.fetched}",
            f"inserted_count={summary.counters.inserted}",
            f"updated_count={summary.counters.updated}",
            f"unchanged_count={summary.counters.unchanged}",
            f"failed_count={summary.counters.failed}",
            f"status={summary.status.value}",
        ]
    )
