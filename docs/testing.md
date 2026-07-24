    # Testing Strategy

## Overview

The project includes a comprehensive test suite covering the most important layers of the application.

The goal of the tests is to verify correctness, reliability, and synchronization safety.

---

# Test Categories

## Adapter Tests

Location

```
tests/test_adapters
```

Purpose

- Odoo authentication
- XML-RPC requests
- Pagination
- Lazy connection
- Cached authentication

Covered components

- OdooAdapter

---

## Mapper Tests

Location

```
tests/test_mappers
```

Purpose

Verify that raw Odoo records are correctly transformed into domain entities.

Examples

- Many2One extraction
- Optional fields
- Type conversion

Covered components

- Contact Mapper
- Product Mapper
- Sale Order Mapper
- Sale Order Line Mapper

---

## Repository Tests

Location

```
tests/test_repositories
```

Purpose

Verify persistence logic.

Covered scenarios

- Insert
- Update
- Upsert
- Idempotency
- Foreign key resolution
- Missing dependency errors

---

## Service Tests

Location

```
tests/test_services
```

Purpose

Verify synchronization workflow.

Covered scenarios

- Successful synchronization
- Pagination
- Batch processing
- Record failures
- Re-running synchronization
- Empty pages

---

## Shutdown Tests

Location

```
tests/test_core
```

Purpose

Verify graceful shutdown.

Covered scenarios

- SIGTERM
- SIGINT
- Interrupted synchronization

---

## Retry Tests

Purpose

Verify retry mechanism.

Covered scenarios

- Retry succeeds
- Retry exhausted
- Unsupported exceptions

---

## Logger Tests

Purpose

Verify logging configuration.

---

## Database Tests

Location

```
tests/test_database
```

Executed against PostgreSQL.

Covered scenarios

- Unique constraints
- Foreign keys
- Cascade delete

---

# Test Isolation

Every unit test uses an isolated SQLite in-memory database.

Benefits

- Fast execution
- No shared state
- Repeatable tests

Database constraint tests execute against PostgreSQL because SQLite does not fully enforce PostgreSQL-specific constraints.

---

# Mocking Strategy

External systems are mocked.

Including

- Odoo XML-RPC
- Network communication
- Synchronization services

This keeps tests deterministic and independent of external infrastructure.

---

# Current Test Results

```
53 Tests

53 Passed

0 Failed
```

---

# Covered Components

✓ Odoo Adapter

✓ Sync Engine

✓ Sync Services

✓ Repositories

✓ Mappers

✓ Logger

✓ Retry

✓ Shutdown Handler

✓ PostgreSQL Constraints

✓ Synchronization Workflow

---

# Why These Tests Matter

Synchronization software interacts with external systems and persistent storage.

Testing ensures that:

- synchronization is deterministic
- failures are isolated
- retries work correctly
- database integrity is preserved
- synchronization remains idempotent
- infrastructure changes do not introduce regressions

---

# Future Test Improvements

Possible future additions include

- Performance tests
- Load tests
- Docker integration tests
- End-to-end synchronization tests
- Property-based tests
- Mutation testing