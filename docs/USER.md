# User Documentation

## Prerequisites

- Docker + Docker Compose

## Run everything

```bash
docker compose up --build
```

Startup order (handled automatically via healthchecks / dependencies):

1. `postgres` — Odoo's database
2. `odoo_init` — creates the `odoo_test` DB and installs Sales *(first run: a few minutes)*
3. `odoo` — Odoo server
4. `odoo_seed` — inserts test data into Odoo (idempotent)
5. `app_db` — the sync target PostgreSQL
6. `odoo_backend` — runs `alembic upgrade head`, then the sync

Success looks like this in the `odoo_backend` logs:

```
[contacts]         status=success received=7  saved=7  failed=0
[products]         status=success received=5  saved=5  failed=0
[sale_orders]      status=success received=7  saved=7  failed=0
[sale_order_lines] status=success received=12 saved=12 failed=0
```

The backend is a batch job: it exits with code `0` when done (Odoo/DB keep running).

## Verify the data

```bash
docker compose exec app_db psql -U sync -d sync_db \
  -c "select operation_type, status, records_received, records_saved, records_updated from sync_runs order by id;"
```

Row counts:

```bash
docker compose exec app_db psql -U sync -d sync_db \
  -c "select 'contacts', count(*) from contacts union all select 'products', count(*) from products union all select 'sale_orders', count(*) from sale_orders union all select 'sale_order_lines', count(*) from sale_order_lines;"
```

## Re-run (idempotency)

```bash
docker compose up
```

The second run reports `updated` instead of `saved` — no duplicates are created.

## Reset everything

```bash
docker compose down -v      # also removes the database volumes
```

## Run locally (without Docker)

```bash
cp .env.example .env        # point it at your Odoo + PostgreSQL
pip install -e .
alembic upgrade head
python -m app.main
```

## Ports

- Odoo UI: http://localhost:8069 (login `admin` / `admin`)
- Sync target PostgreSQL: `localhost:5433` (user `sync`, db `sync_db`)
