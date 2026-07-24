# Odoo Sync Backend

A production-style backend service that synchronizes data from an Odoo ERP instance into PostgreSQL using a clean, modular, and testable architecture.

The project was designed with maintainability, scalability, and reliability in mind. It follows Hexagonal Architecture (Ports & Adapters), uses Repository Pattern for data access, and provides a generic synchronization engine capable of synchronizing multiple entity types with minimal duplication.

---

# Features

- Synchronize Contacts
- Synchronize Products
- Synchronize Sale Orders
- Synchronize Sale Order Lines

- Generic synchronization engine
- Batch processing
- Pagination support
- Idempotent upsert operations
- Transaction per record using SAVEPOINT
- Graceful shutdown support
- Detailed synchronization logs
- Synchronization history
- Automatic retry support
- Structured logging
- Alembic database migrations
- Docker support
- Unit and integration tests

---

# Architecture

The project follows **Hexagonal Architecture (Ports & Adapters)**.

```
                  Odoo ERP
                     │
                     │ XML-RPC
                     ▼
              Odoo Adapter
                     │
                     ▼
             Synchronization Services
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

Responsibilities are clearly separated:

- Adapter → communication with Odoo
- Mapper → converts Odoo records into domain entities
- Repository → persistence layer
- Service → orchestration
- SyncEngine → shared synchronization workflow

---

# Project Structure

```
backend/

├── adapters/
├── core/
├── database/
├── mappers/
├── migrations/
├── models/
├── repositories/
├── services/
├── tests/
├── sync_all.py
└── requirements.txt
```

---

# Technologies

- Python 3.12
- SQLAlchemy 2
- PostgreSQL
- Alembic
- Docker
- Pytest
- XML-RPC
- Faker

---

# Installation

Clone the repository

```bash
git clone <repository-url>
cd backend
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/mydb

ODOO_URL=http://localhost:8069
ODOO_DB=mydb
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

---

# Database Migration

Create migrations

```bash
alembic revision --autogenerate -m "initial"
```

Apply migrations

```bash
alembic upgrade head
```

---

# Running Synchronization

Run the complete synchronization process

```bash
python sync_all.py
```

Synchronization order

1. Contacts
2. Products
3. Sale Orders
4. Sale Order Lines

This order guarantees that all foreign key dependencies already exist before child records are synchronized.

---

# Running Tests

Run all tests

```bash
pytest
```

Run with coverage

```bash
pytest --cov --cov-report=term-missing
```

Using Docker

```bash
docker compose exec backend pytest

docker compose exec backend pytest --cov --cov-report=term-missing
```

---

# Synchronization Flow

For every entity:

```
Fetch page from Odoo

↓

Map raw data

↓

Create domain entity

↓

Repository Upsert

↓

Commit Batch

↓

Continue
```

---

# Error Handling

The synchronization process is designed so that one failing record never stops the entire synchronization.

Each record executes inside its own SAVEPOINT.

```
Batch

 ├── Record A ✓
 ├── Record B ✓
 ├── Record C ✗ rollback
 ├── Record D ✓
 └── Record E ✓
```

The failed record is logged while the remaining records continue processing normally.

---

# Graceful Shutdown

The application supports graceful shutdown using SIGTERM and SIGINT.

Instead of terminating immediately:

- current batch finishes
- current transaction commits
- synchronization state is saved
- sync status becomes "interrupted"

This prevents partial batch commits.

---

# Logging

Synchronization produces structured logs for:

- synchronization start
- progress
- errors
- completion
- interruption

Additionally:

- SyncRun stores synchronization history.
- SyncLog stores record-level failures.

---

# Testing

The project includes:

- Adapter tests
- Repository tests
- Mapper tests
- Service tests
- Retry tests
- Logger tests
- Shutdown tests
- PostgreSQL constraint tests
- Synchronization engine tests

Current status

```
53 tests

53 passed
0 failed
```

---

# Performance Considerations

Several techniques are used to improve synchronization performance.

- Pagination
- Batch Processing
- Lazy Odoo Authentication
- Cached XML-RPC Connection
- Generic Sync Engine
- Upsert instead of Insert
- Transaction per batch
- SAVEPOINT per record

---

# Design Principles

The implementation follows several software engineering principles.

- SOLID
- Separation of Concerns
- Repository Pattern
- Dependency Injection
- Single Responsibility Principle
- Idempotent Synchronization
- Clean Architecture

---

# Future Improvements

Possible future enhancements include:

- Incremental synchronization
- Soft delete synchronization
- Parallel workers
- RabbitMQ / Kafka integration
- Celery scheduling
- Webhook-based synchronization
- Metrics dashboard
- Prometheus integration
- OpenTelemetry tracing

---

# License

This project was developed as a technical assessment demonstrating software architecture, synchronization design, testing practices, and production-oriented backend development.