from __future__ import annotations

import argparse
import sys

from pydantic import ValidationError

from odoo_sync.bootstrap import build_container
from odoo_sync.domain.pagination import PageSize
from odoo_sync.domain.sync import SyncStatus, SyncType
from odoo_sync.presentation.cli.output import format_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m odoo_sync")
    subparsers = parser.add_subparsers(dest="command", required=True)
    sync = subparsers.add_parser("sync")
    mode = sync.add_mutually_exclusive_group(required=True)
    mode.add_argument("--full", action="store_true")
    mode.add_argument("--incremental", action="store_true")
    sync.add_argument("--page-size", type=int, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        container = build_container()
        PageSize(args.page_size or container.settings.page_size)
        from odoo_sync.application.services.shutdown import install_shutdown_handlers

        install_shutdown_handlers(container.shutdown)
        sync_type = SyncType.FULL if args.full else SyncType.INCREMENTAL
        summary = container.sync_service.sync(
            sync_type=sync_type, page_size=args.page_size or container.settings.page_size
        )
        print(format_summary(summary))
        return 0 if summary.status is SyncStatus.SUCCESS else 2
    except (ValidationError, ValueError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"fatal error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
