# Architecture

## Overview

The project follows **Hexagonal Architecture (Ports & Adapters)** to separate business logic from infrastructure concerns.

Instead of allowing the business logic to depend directly on databases or external APIs, all infrastructure components communicate through clearly defined boundaries.

This makes the application easier to maintain, test, and extend.

---

# High-Level Architecture

```
                 Odoo ERP
                     │
               XML-RPC API
                     │
                     ▼
             Odoo Adapter
                     │
                     ▼
           Synchronization Service
                     │
                     ▼
              Generic Sync Engine
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
     Mapper                  Repository
        │                         │
        └────────────┬────────────┘
                     ▼
                 PostgreSQL
```

---

# Layers

## Adapter Layer

Location

```
adapters/
```

Responsibilities

- Connect to Odoo
- Authenticate
- Execute XML-RPC calls
- Fetch paginated records
- Hide XML-RPC implementation details

The rest of the application never communicates with XML-RPC directly.

---

## Mapper Layer

Location

```
mappers/
```

Responsibilities

- Convert raw Odoo dictionaries into domain entities
- Normalize optional values
- Extract Many2One identifiers
- Keep Odoo-specific logic outside repositories

Example

Odoo returns

```python
{
    "partner_id": [15, "John Doe"]
}
```

Mapper converts it into

```python
contact_odoo_id = 15
```

---

## Repository Layer

Location

```
repositories/
```

Responsibilities

- Persist entities
- Resolve foreign keys
- Execute Upsert operations
- Isolate SQLAlchemy from business logic

Repositories never know anything about Odoo.

---

## Service Layer

Location

```
services/
```

Responsibilities

- Coordinate synchronization
- Build SyncEngine
- Inject repositories
- Inject mappers
- Inject adapter methods

Each service is intentionally thin.

Example

```
sync_contacts()

↓

SyncEngine
```

---

## Generic Sync Engine

Location

```
services/sync_engine.py
```

The SyncEngine contains all synchronization workflow.

It receives:

- count function
- fetch function
- mapper
- repository upsert
- batch size

This allows every entity type to reuse exactly the same synchronization logic.

Instead of writing four different synchronization implementations, only one engine exists.

---

# Synchronization Workflow

```
Count records

↓

Fetch page

↓

Map record

↓

Create Entity

↓

Repository Upsert

↓

Commit Batch

↓

Repeat
```

---

# Dependency Direction

Dependencies always point inward.

```
Adapter

↓

Service

↓

SyncEngine

↓

Repository

↓

Database
```

The database never depends on services.

Repositories never depend on adapters.

Business logic never depends on XML-RPC.

---

# Why Hexagonal Architecture?

Advantages

- Loose coupling
- Easier testing
- Easier maintenance
- Infrastructure can change independently
- Clear separation of responsibilities
- High code reuse

For example, replacing Odoo XML-RPC with REST would only require implementing another adapter.

No repository or service would need to change.

---

# Repository Pattern

Repositories isolate persistence logic.

Instead of writing SQL throughout the application, all persistence is centralized.

Responsibilities include

- Upsert
- Query by Odoo ID
- Foreign key resolution
- Entity updates

Benefits

- Easier testing
- Cleaner services
- Better separation of concerns

---

# Mapper Pattern

Odoo data should never be used directly by repositories.

The Mapper layer transforms external DTOs into internal domain entities.

Benefits

- Cleaner repositories
- Easier validation
- Easier migration to another ERP
- Centralized transformation logic

---

# Batch Processing

Synchronization uses batch processing.

```
Batch 1

↓

Commit

↓

Batch 2

↓

Commit

↓

Batch 3
```

Benefits

- Lower memory usage
- Better scalability
- Faster recovery after failures

---

# Transaction Strategy

Every batch is committed separately.

Inside every batch, every record executes inside its own SAVEPOINT.

```
Batch

 ├── Record A ✓
 ├── Record B ✓
 ├── Record C ✗ rollback
 ├── Record D ✓
 └── Record E ✓

Commit Batch
```

A single invalid record never rolls back the entire batch.

---

# Graceful Shutdown

The synchronization process supports graceful shutdown.

When SIGINT or SIGTERM is received

```
Signal

↓

Current Record

↓

Finish Current Batch

↓

Commit

↓

Save Status

↓

Exit
```

This prevents partially committed batches.

---

# Error Handling

Failures are isolated.

Each failed record

- rolls back only itself
- creates a SyncLog entry
- increments error count
- allows synchronization to continue

---

# Synchronization Metadata

Two tables are maintained.

## SyncRun

Stores

- operation
- start time
- finish time
- status
- records fetched
- created
- updated
- errors

---

## SyncLog

Stores

- failed record
- exception message
- log level
- synchronization run

This allows synchronization history to be inspected later.

---

# Testing Strategy

The project uses multiple testing layers.

- Unit Tests
- Repository Tests
- Mapper Tests
- Adapter Tests
- Integration Tests
- PostgreSQL Constraint Tests
- Synchronization Tests
- Shutdown Tests

The architecture makes mocking dependencies straightforward because every layer has a single responsibility.

---

# Extensibility

Adding a new entity requires only four components.

```
New Mapper

↓

New Repository

↓

New Service

↓

Call SyncEngine
```

The synchronization engine itself does not require modification.

This follows the Open/Closed Principle by allowing extension without changing existing synchronization logic.