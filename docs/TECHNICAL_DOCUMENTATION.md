# Technical Documentation

## Architecture

The backend uses Ports and Adapters:

```text
Domain <- Application <- Infrastructure <- Composition Root
```

Domain contains typed Odoo-independent contracts. Application contains the synchronization use case and ports. Infrastructure implements XML-RPC access, SQLAlchemy persistence, settings, and logging. The composition root builds concrete dependencies and passes them into the service.

The Odoo Adapter is separate from the Sync Service because XML-RPC dictionaries, Odoo field names, retry handling, and mapping failures are infrastructure concerns. The service receives typed internal records only.

Repositories exist because persistence is a real boundary. Application code asks for `find_id_by_odoo_id` and `upsert`; SQLAlchemy models stay inside infrastructure.

Dependency injection is done in `odoo_sync.bootstrap`. It creates settings, logger, Odoo client/adapter, SQLAlchemy session factory, Unit of Work factory, and Sync Service.

## Odoo Mapping

Contacts map from `res.partner`: `id`, `name`, `email`, `phone`, `mobile`, `write_date`.

Products map from `product.product`: `id`, `name`, `default_code`, `list_price`, `detailed_type`, `write_date`.

Sale Orders map from `sale.order`: `id`, `name`, `partner_id`, `date_order`, `state`, `amount_total`, `write_date`.

Sale Order Lines map from `sale.order.line`: `id`, `order_id`, `product_id`, `product_uom_qty`, `price_unit`, `price_subtotal`, `write_date`.

Odoo `False` optional values become `None`. Amounts and quantities use `Decimal(str(value))`. Datetime strings become UTC-aware `datetime` values. Many2one fields are validated before IDs are extracted.

## Database Schema

The Sync PostgreSQL database contains `contacts`, `products`, `sale_orders`, `sale_order_lines`, `sync_runs`, and `sync_logs`.

Odoo-sourced tables have an internal primary key, unique `odoo_id`, nullable `odoo_write_date`, and timezone-aware `created_at`/`updated_at`.

Foreign keys connect Sale Orders to Contacts and Sale Order Lines to Sale Orders and Products. Sale Order deletion cascades to lines. Contact and Product deletion is restricted while referenced.

Duplicate prevention is enforced by repository upsert logic and unique `odoo_id` constraints.

## Transactions

The Unit of Work owns one SQLAlchemy session and repository set. Leaving it without commit rolls back. The sync service opens a fresh Unit of Work per record, so a failed record does not roll back prior successful records or affect later records.

## Error Handling and Logging

Mapping and persistence errors are recorded in `sync_logs` and processing continues. Fatal authentication or page-read failures stop the run and finalize `sync_runs` with failed status. Error text is sanitized before logging or storing. Successful records are aggregated in `sync_runs`; no success log row is written per record.

Logs are structured JSON by default. They cover run start/finish, entity processing, retries, record failures, and fatal failures without raw Odoo records or credentials.

## Pagination and Retry

Odoo reads use keyset pagination with `id > last_seen_id`, `id asc`, and a configurable page size. The cursor advances by raw Odoo ID even if one record fails mapping.

Retry is bounded and only for transport/timeout-style failures. Authentication, mapping, validation, and deterministic business errors are not retried.

## Incremental Sync

Incremental sync uses the latest successful run with an upper watermark as the lower watermark. At run start, the adapter captures one upper watermark. Reads apply `write_date > lower_watermark` and `write_date <= upper_watermark`. If no successful baseline exists, the incremental run fails clearly.

## Graceful Shutdown

`SIGINT` and `SIGTERM` set a shutdown flag. The active record finishes or rolls back through its Unit of Work. The service starts no new record, finalizes the run as cancelled, and exits non-zero without a shutdown traceback.

## Secret Management

Configuration comes from environment variables. Database URLs are built with SQLAlchemy URL utilities, not credential string concatenation. Passwords and credential-bearing URLs are not logged or documented beyond safe `.env.example` local values.

## Replacement Scenarios

Replacing Odoo with another ERP mainly requires a new ERP adapter that implements the Application ERP port and returns the same internal contracts.

Replacing PostgreSQL with MSSQL mainly requires new persistence implementations and migrations while keeping repository ports and application orchestration stable.

## Large Data Handling

For hundreds of thousands of Sale Orders, the current keyset pagination avoids loading a full entity type into memory. The main throughput limit is the per-record transaction model. That is intentional for failure isolation; higher throughput would require batching transactions with weaker isolation.

## Trade-offs

- Single-process CLI keeps operations simple.
- Per-record transactions isolate failures but cost more commits.
- XML-RPC polling is portable but less immediate than event ingestion.
- There is no concurrent-run coordination because it was not required.

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
