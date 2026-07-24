#!/usr/bin/env bash
set -euo pipefail

DB="${ODOO_DATABASE:-odoo}"
DB_HOST="${HOST:-odoo-db}"
DB_PORT="${PORT:-5432}"

python3 - <<PY
import socket
import sys
import time

host = "${DB_HOST}"
port = int("${DB_PORT}")
deadline = time.monotonic() + 120
last_error = None

while time.monotonic() < deadline:
    try:
        socket.getaddrinfo(host, port)
        with socket.create_connection((host, port), timeout=5):
            sys.exit(0)
    except OSError as exc:
        last_error = exc
        time.sleep(2)

raise SystemExit(f"database {host}:{port} did not become reachable: {last_error}")
PY

odoo \
  --config=/etc/odoo/odoo.conf \
  --database="${DB}" \
  --init=base,contacts,sale_management \
  --without-demo=all \
  --stop-after-init

exec odoo --config=/etc/odoo/odoo.conf --database="${DB}"
