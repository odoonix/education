# Odoonix Odoo Sync Backend

This branch adds a single-process Python backend that reads Odoo 17 Contacts, Products, Sale Orders, and Sale Order Lines through XML-RPC and stores them in a separate PostgreSQL 15 database.

## Delivered Capabilities

- Docker Compose stack with Odoo, Odoo PostgreSQL, Sync PostgreSQL, and backend services.
- Idempotent Odoo module initialization for `base`, `contacts`, and `sale_management`.
- Deterministic XML-RPC seed data: 5 Contacts, 5 Products, 3 Sale Orders, and 6 Sale Order Lines.
- Full and incremental synchronization with keyset pagination.
- Typed internal models, repository ports, SQLAlchemy repositories, and Unit of Work transaction ownership.
- Per-record failure isolation with aggregate run summaries and record-level sync logs.
- Alembic migrations, structured logging, bounded retry, and environment-backed settings.

## Architecture Summary

The backend follows a lightweight Ports and Adapters design:

```text
Odoo XML-RPC -> Odoo Adapter -> Sync Service -> Repository Ports + Unit of Work -> SQLAlchemy -> Sync PostgreSQL
```

Domain code is ORM-independent. Application code depends on ports. Infrastructure implements Odoo access, persistence, settings, and logging. `odoo_sync.bootstrap` wires the concrete objects.

## Technology Stack

Python 3.12, uv, SQLAlchemy 2, Alembic, Psycopg 3, Pydantic Settings 2, standard-library XML-RPC, Pytest, Ruff, MyPy, Docker Compose v2, Odoo 17, PostgreSQL 15.

## Prerequisites

- Docker Compose v2
- Python 3.12
- uv

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Odoo is exposed at `http://localhost:8069`.

## Service Topology

- `odoo-db`: PostgreSQL 15 for Odoo only.
- `odoo`: Odoo 17 runtime.
- `sync-db`: PostgreSQL 15 for synchronized data only.
- `backend`: applies migrations, seeds Odoo, runs one full sync, then exits.
- `backend-test`: optional test-profile backend image.

## Controlled Test Data

The seed script uses stable `ir.model.data` external IDs under `odoo_sync_seed`. This makes reruns update controlled records instead of creating duplicates.

## Sync Commands

```bash
docker compose run --rm backend python -m odoo_sync sync --full
docker compose run --rm backend python -m odoo_sync sync --incremental
```

Optional page size:

```bash
docker compose run --rm backend python -m odoo_sync sync --full --page-size 50
```

## Test Commands

```bash
cd sync_backend
uv lock --check
uv sync --frozen --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest -m unit
uv run pytest --cov=odoo_sync --cov-branch --cov-report=term-missing
cd ..
```

Docker-backed checks:

```bash
docker compose -p odoonix_acceptance --profile test run --rm backend-test uv run pytest -m integration
docker compose -p odoonix_acceptance --profile test run --rm backend-test uv run pytest -m end_to_end
```

## Configuration Summary

Runtime configuration is read from environment variables. See `.env.example` for local values covering Odoo URL/database/user/password, retry settings, page size, Sync PostgreSQL host/port/database/user/password, and log options.

## More Documentation

- [Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md)
- [User Documentation](docs/USER_DOCUMENTATION.md)

## Known Limitations

- Synchronization is one-way from Odoo to Sync PostgreSQL.
- Odoo deletions are not propagated.
- There is no automatic scheduler.
- There is no public HTTP API.
- XML-RPC polling is used instead of event ingestion.
- Incremental synchronization depends on Odoo `write_date`.
- Simultaneous sync execution is not coordinated.
- Per-record transactions favor failure isolation over maximum throughput.
- Deterministic seed data is intentionally small.
- `.env.example` values are for local development only.

## Repository and License

This work is added inside `PixyBoy/odoonix` and inherits the repository license.
