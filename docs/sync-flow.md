# Synchronization Flow

This document describes the complete synchronization lifecycle from Odoo to PostgreSQL.

---

# High-Level Flow

```
Odoo ERP

↓

XML-RPC

↓

OdooAdapter

↓

Sync Service

↓

SyncEngine

↓

Mapper

↓

Repository

↓

PostgreSQL
```

---

# Step 1 — Count Records

The synchronization starts by requesting the total number of records from Odoo.

Example

```
count_contacts()

↓

2450
```

The total count is used to determine pagination.

---

# Step 2 — Fetch a Batch

Records are fetched page by page.

```
Batch Size = 500

Page 1

↓

500 Records

↓

Page 2

↓

500 Records
```

This avoids loading the entire dataset into memory.

---

# Step 3 — Mapping

Every raw Odoo dictionary is transformed into a domain entity.

Example

Raw Odoo

```python
{
    "partner_id": [15, "John Doe"]
}
```

↓

Domain Entity

```python
contact_odoo_id = 15
```

---

# Step 4 — Upsert

Repositories perform an Upsert.

```
Exists?

↓

Yes → Update

No → Insert
```

This guarantees idempotent synchronization.

---

# Step 5 — Transaction

Every record runs inside a SAVEPOINT.

```
Batch

├── Record A ✓
├── Record B ✓
├── Record C ✗
├── Record D ✓
└── Record E ✓
```

If Record C fails

↓

Rollback Record C only

↓

Continue

---

# Step 6 — Commit

After the batch completes

```
Commit Batch
```

instead of

```
Commit Every Record
```

This significantly improves performance.

---

# Step 7 — Logging

During synchronization

SyncRun stores

- start time
- finish time
- statistics
- status

SyncLog stores

- failed record
- exception
- error message

---

# Step 8 — Graceful Shutdown

When SIGTERM or SIGINT is received

```
Signal

↓

Current Record

↓

Finish Batch

↓

Commit

↓

Save Status

↓

Exit
```

Synchronization status becomes

```
interrupted
```

instead of leaving incomplete transactions.

---

# Complete Sequence Diagram

```
sync_all.py

        │

        ▼

Sync Service

        │

        ▼

SyncEngine

        │

        ▼

Count Records

        │

        ▼

Fetch Batch

        │

        ▼

Map Record

        │

        ▼

Repository Upsert

        │

        ▼

SAVEPOINT

        │

        ▼

Commit Batch

        │

        ▼

Repeat

        │

        ▼

Finish

        │

        ▼

Update SyncRun
```

---

# Failure Handling

If a single record fails

```
Rollback Record

↓

Create SyncLog

↓

Continue

↓

Commit Batch
```

The synchronization never stops because of one invalid record.

---

# Summary

The synchronization process is designed around four primary goals:

- Reliability
- Idempotency
- Recoverability
- Maintainability

The generic SyncEngine allows new entity types to reuse the exact same synchronization workflow with minimal additional code.