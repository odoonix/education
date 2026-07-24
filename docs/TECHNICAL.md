# Technical Documentation

## Architecture

Clean / hexagonal architecture, dependencies point **inward**:

| Layer | Contents | Depends on |
|---|---|---|
| **domain** | entities, repository interfaces, `IDBConnection` port | nothing |
| **application** | DTOs, mappers, sync services, use cases | domain |
| **infrastructure** | Odoo XML-RPC client, SQLAlchemy models/repos, DI container | domain + application |

Flow of one sync run:

```
OdooClient ─▶ SyncService (fetch + map to entity)
                    │
             SyncEntityUseCase (upsert + error isolation + record run/logs)
                    │
             Repository (IDBConnection) ─▶ PostgreSQL
```

The **DI container** (`dependency-injector`) wires everything; `main.py` is the
composition root and orchestrator (runs the 4 use cases in FK-safe order).

## Key design decisions

- **Adapter separate from service** — Odoo access is isolated in `OdooClient`
  (infrastructure). Swapping ERPs means writing one adapter; services/use cases
  stay unchanged.
- **Repository pattern over a port** — repos depend on the `IDBConnection`
  abstraction, not on SQLAlchemy directly. Swapping PostgreSQL for another DB
  means one new adapter.
- **`odoo_id` as primary key** for the 4 synced tables — the source id *is* the
  identity, so foreign keys line up directly without id translation.
  `sync_runs` / `sync_logs` use their own auto-increment ids.
- **Idempotency (no duplicates)** — the use case looks up each record by
  `odoo_id`; found → `update`, missing → `save`. Re-runs update in place.
- **Per-record error isolation** — each record is processed in its own
  `try/except` and its own transaction. One failure is logged to `sync_logs`
  and counted; the batch continues. A single error never rolls back the run.
- **Type hints + generic interfaces** throughout; enums for run status / log level.

## Data model

`contacts`, `products`, `sale_orders`, `sale_order_lines` (+ FKs:
`sale_orders.customer_id → contacts`, `sale_order_lines → sale_orders, products`).

Observability: `sync_runs` (one row per operation: type, start/end, counts,
status) and `sync_logs` (per-error detail, FK → `sync_runs`, `ON DELETE CASCADE`).

Schema is managed by **Alembic** migrations.

## Defense notes

- **One error → full rollback?** No. Per-record transactions, so other records
  still commit. This matches the requirement to keep processing on failure.
- **Hundreds of thousands of orders?** Add pagination + batch reads on the Odoo
  side, bulk upserts, and indexing; move to incremental sync by `write_date`.
- **Extensibility** — a new entity type = one service + one repository + one use
  case provider; the generic `SyncEntityUseCase` is reused.

## Testing strategy

- **Unit** — entities, mappers, and the use case (error isolation, counting,
  status) with fakes; repositories against in-memory SQLite.
- **Integration** — the full pipeline is validated end-to-end via
  `docker compose up` (real Odoo + PostgreSQL).

## Known limitations

- No retry / pagination / incremental sync yet (single full pull per run).
- Odoo credentials are passed via environment; production should use a secrets
  manager.
- `odoo_init` re-installs modules on every `up` (slower, but non-destructive).
