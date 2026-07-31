#!/usr/bin/env bash
set -euo pipefail

cd /app/sync_backend
uv run alembic upgrade head
python3 /seed/seed_odoo.py seed
uv run python -m odoo_sync sync --full
