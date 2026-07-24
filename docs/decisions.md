# Architecture Decision Records (ADR)

This document explains the most important architectural decisions made during the implementation of the project.

---

# ADR-001: Hexagonal Architecture

## Decision

The project follows **Hexagonal Architecture (Ports & Adapters)**.

## Motivation

The synchronization process communicates with two completely different systems:

- Odoo ERP
- PostgreSQL

The business logic should not depend directly on either of them.

## Benefits

- Loose coupling
- Better maintainability
- Easier testing
- Infrastructure can change independently
- Clear separation of responsibilities

## Alternatives Considered

### Layered Architecture

Rejected because business logic would become tightly coupled to infrastructure.

### Direct SQL + XML-RPC

Rejected because responsibilities become mixed together.

---

# ADR-002: Repository Pattern

## Decision

Every database operation is encapsulated inside a Repository.

## Motivation

Repositories isolate SQLAlchemy from the business layer.

Instead of:

```
Service

↓

SQLAlchemy
```

we have:

```
Service

↓

Repository

↓

SQLAlchemy
```

## Benefits

- Cleaner services
- Easier testing
- Centralized persistence logic
- Easier future ORM replacement

---

# ADR-003: Generic Sync Engine

## Decision

A single reusable synchronization engine is responsible for synchronizing every entity.

## Motivation

Contacts, Products, Sale Orders and Sale Order Lines all perform exactly the same workflow.

Instead of duplicating synchronization logic four times, the common workflow was extracted into SyncEngine.

## Benefits

- No duplicated code
- Easier maintenance
- Easier testing
- Easier extension

Adding a new entity only requires:

- Mapper
- Repository
- Sync Service

No engine changes are required.

---

# ADR-004: Mapper Layer

## Decision

Raw Odoo responses are converted into domain entities before reaching repositories.

## Motivation

Odoo returns XML-RPC dictionaries that contain ERP-specific structures.

Example

```
partner_id

↓

[15, "John Doe"]
```

Repositories should not understand these structures.

The mapper transforms them into clean domain objects.

## Benefits

- Separation of concerns
- Cleaner repositories
- Easier validation
- Easier migration to another ERP

---

# ADR-005: Upsert Instead of Insert

## Decision

Repositories perform Upsert operations.

## Motivation

Synchronization must be idempotent.

Running synchronization multiple times must never create duplicate records.

## Benefits

- Safe re-execution
- Incremental updates
- Duplicate prevention

---

# ADR-006: Batch Processing

## Decision

Records are processed in configurable batches.

## Motivation

Loading every record into memory would not scale for large datasets.

## Benefits

- Lower memory usage
- Better performance
- Faster commits
- Better recovery after failures

---

# ADR-007: SAVEPOINT Per Record

## Decision

Each record is executed inside its own nested transaction.

```
Batch

↓

SAVEPOINT

↓

Record

↓

Release SAVEPOINT
```

## Motivation

One invalid record should never rollback an entire batch.

## Benefits

- Error isolation
- Better reliability
- Higher synchronization completion rate

---

# ADR-008: Commit Per Batch

## Decision

Transactions are committed once per batch.

## Motivation

Committing every record individually is expensive.

Committing the whole synchronization at once is risky.

Batch commits provide a good balance.

## Benefits

- Better performance
- Smaller transactions
- Easier recovery

---

# ADR-009: Graceful Shutdown

## Decision

Synchronization supports SIGINT and SIGTERM.

## Motivation

Production deployments may terminate containers unexpectedly.

Instead of stopping immediately, the application:

- finishes the current batch
- commits changes
- saves synchronization status
- exits safely

## Benefits

- No partial batch commits
- Better consistency
- Safer deployments

---

# ADR-010: Lazy Odoo Connection

## Decision

Connection to Odoo is established only when required.

Authentication is cached.

## Motivation

Creating XML-RPC connections for every request would be inefficient.

## Benefits

- Less network overhead
- Faster synchronization
- Lower authentication cost

---

# ADR-011: Structured Logging

## Decision

The project uses structured logging instead of print statements.

## Motivation

Synchronization jobs often execute unattended.

Detailed logs are required for monitoring and debugging.

The application logs:

- synchronization start
- progress
- failures
- completion
- interruption

---

# ADR-012: Synchronization History

## Decision

Synchronization metadata is stored in the database.

Two tables are maintained.

## SyncRun

Stores

- operation
- start time
- finish time
- status
- statistics

## SyncLog

Stores

- failed record
- error message
- synchronization run

## Benefits

- Auditing
- Monitoring
- Debugging
- Historical reporting

---

# ADR-013: Extensive Testing

## Decision

Testing is implemented across multiple layers.

The project includes:

- Adapter Tests
- Repository Tests
- Mapper Tests
- Service Tests
- Database Constraint Tests
- Retry Tests
- Shutdown Tests
- Synchronization Tests

## Motivation

Synchronization software interacts with external systems and persistent storage.

Comprehensive testing reduces regression risk and improves maintainability.

---

# ADR-014: Dependency Injection

## Decision

Dependencies are injected instead of being instantiated inside business logic.

Example

```
SyncEngine(
    count_fn=...,
    fetch_page_fn=...,
    map_fn=...,
    upsert_fn=...
)
```

instead of

```
SyncEngine()

↓

Create Adapter

↓

Create Repository

↓

Create Mapper
```

## Benefits

- Loose coupling
- Better testing
- Easier mocking
- Better extensibility

---

# Summary

The architecture emphasizes:

- Maintainability
- Reliability
- Testability
- Extensibility
- Production-readiness

The project favors clear separation of concerns, reusable components, and safe synchronization over short-term implementation simplicity.