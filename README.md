# Odoo → PostgreSQL Sync

A backend service that pulls **Contacts, Products, Sale Orders and Sale Order
Lines** from Odoo (XML-RPC), maps them to an internal model, and stores them in
PostgreSQL. Re-runnable and idempotent (no duplicates), with per-record error
isolation and a full audit trail in `sync_runs` / `sync_logs`.

```
Odoo ──XML-RPC──▶ Python Backend ──Mapping / Upsert──▶ PostgreSQL
```

## Quick start (Docker)

```bash
docker compose up --build
```

This brings up the whole environment: Odoo + its database, seeds Odoo with test
data, then runs migrations and the sync. Watch the `odoo_backend` logs for the
result. See [docs/USER.md](docs/USER.md) for details and verification.

## Local run (without Docker)

```bash
cp .env.example .env        # then edit values
pip install -e .
alembic upgrade head        # create tables
python -m app.main          # run the sync
```

## Tests

```bash
pytest --cov=app
```

21 tests (entities, mappers, repositories, and the sync use case), ~77% coverage.

## Layout

```
app/
  domain/          entities, repository interfaces, ports
  application/     DTOs, mappers, sync services, use cases
  infrastructure/  Odoo client, SQLAlchemy models/repos, DI container
alembic/           database migrations
scripts/           Odoo test-data seeder
docs/              technical & user documentation
```

## Documentation

- [Technical documentation](docs/TECHNICAL.md) — architecture & design decisions
- [User documentation](docs/USER.md) — how to run and verify
