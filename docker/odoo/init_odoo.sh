#!/usr/bin/env bash
set -euo pipefail

DB="${ODOO_DATABASE:-odoo}"

odoo \
  --config=/etc/odoo/odoo.conf \
  --database="${DB}" \
  --init=base,contacts,sale_management \
  --without-demo=all \
  --stop-after-init

exec odoo --config=/etc/odoo/odoo.conf --database="${DB}"
