# User Documentation

## Environment Setup

Install Docker Compose v2. For local Python checks, install Python 3.12 and uv.

Create local configuration:

```bash
cp .env.example .env
```

The example values are for local development only.

## Starting the Complete Stack

```bash
docker compose up --build
```

This starts Odoo PostgreSQL, Odoo 17, Sync PostgreSQL, and the backend. The backend applies migrations, runs the seed, runs one full sync, and exits.

## Stopping the Stack

```bash
docker compose down
```

## Accessing Odoo

Open `http://localhost:8069`.

Default local credentials from `.env.example`:

- Database: `odoo`
- Username: `admin`
- Password: `admin`

## Volumes

To preserve data, stop with:

```bash
docker compose down
```

To delete local databases and Odoo filestore:

```bash
docker compose down --volumes --remove-orphans
```

## Rerunning the Seed

```bash
docker compose run --rm backend python3 /seed/seed_odoo.py seed
docker compose run --rm backend python3 /seed/seed_odoo.py verify
```

The seed uses deterministic external IDs, so reruns update controlled records instead of creating duplicates.

## Running Sync

Full sync:

```bash
docker compose run --rm backend python -m odoo_sync sync --full
```

Incremental sync:

```bash
docker compose run --rm backend python -m odoo_sync sync --incremental
```

Incremental sync requires a prior successful run with a stored upper watermark.

## Running Tests

Local backend checks:

```bash
cd sync_backend
uv sync --frozen --all-groups
uv run pytest -m unit
uv run pytest --cov=odoo_sync --cov-branch --cov-report=term-missing
cd ..
```

Docker-backed checks:

```bash
docker compose -p odoonix_acceptance --profile test run --rm backend-test uv run pytest -m integration
docker compose -p odoonix_acceptance --profile test run --rm backend-test uv run pytest -m end_to_end
```

## Interpreting Results

The CLI prints sync type, start time, finish time, fetched count, inserted count, updated count, unchanged count, failed count, and status.

Exit code `0` means processing completed. Isolated record failures can still be present and are counted. Fatal configuration, connection, authentication, migration, page-read, or cancellation failures exit non-zero.

## Troubleshooting

Startup failures: run `docker compose ps` and `docker compose logs --no-color`.

Database failures: check that `odoo-db` and `sync-db` are healthy. Recreate local volumes only when you are comfortable deleting local data.

Migration failures: run `docker compose run --rm backend uv run alembic upgrade head` and inspect the error.

Odoo authentication failures: verify `ODOO_DATABASE`, `ODOO_USERNAME`, and `ODOO_PASSWORD` match the running Odoo database.

Connection failures: verify `ODOO_URL` is `http://odoo:8069` inside Compose and that Odoo is healthy before running backend commands.
