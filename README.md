# Odoo Sync Backend Challenge

## Overview

This project is an implementation of an Odoo synchronization backend built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **Docker**, and **uv**.

The goal is to build a maintainable backend capable of synchronizing data between Odoo and a local PostgreSQL database using a layered architecture.

Due to time constraints, the project focuses on establishing a clean and extensible architecture rather than implementing every planned feature.

---

# Project Structure

```
.
├── addons/
├── backend/
│   ├── app/
│   │   ├── adapters/
│   │   ├── api/
│   │   ├── config/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── migrations/
│   └── tests/
│
├── docker/
├── seed/
└── docker-compose.yml
```

---

# Architecture

The backend follows a layered architecture in order to keep responsibilities separated and make the project easier to maintain and extend.

## API

Responsible only for exposing HTTP endpoints.

No business logic should live here.

---

## Services

Contains the application's business logic.

Services orchestrate repositories, adapters and external integrations.

---

## Repositories

Responsible for all database operations.

Business logic never communicates directly with SQLAlchemy models.

---

## Models

Database entities implemented using SQLAlchemy ORM.

---

## Database

Contains:

* SQLAlchemy Engine
* Session management
* Base model
* Dependency injection
* Alembic configuration

---

## Adapters

Responsible for communicating with external systems.

In this project the Odoo XML-RPC integration is intended to live here.

---

## Schemas

Pydantic request/response models.

---

## Utils

Common helper functions.

---

# Current Progress

## Docker Infrastructure

The project includes Docker configuration for:

* FastAPI
* PostgreSQL (Backend)
* PostgreSQL (Odoo)
* Odoo
* Nginx

Health checks are configured for all services.

Environment variables are loaded from `.env`.

---

## Seed Module

A standalone seed module has been implemented.

It connects to Odoo through XML-RPC and automatically inserts sample data.

The following records are created:

* Contacts
* Products
* Sale Orders
* Sale Order Lines

The seed module is intentionally isolated from the backend application.

A dedicated README is available inside the `seed/` directory describing how to execute it.

---

# Running the Seed

Before running the seed:

1. Start Docker services.
2. Wait until Odoo is ready.
3. Open Odoo in the browser.
4. Login as administrator.
5. Install the required Odoo applications:

   * Contacts
   * Sales
   * Inventory

After Odoo is initialized, execute the seed module following the instructions available inside:

```
seed/README.md
```

---

# Database

The database layer has been fully initialized.

Implemented components:

* SQLAlchemy Engine
* Session management
* Declarative Base
* Alembic configuration
* Initial database migration

Current database models:

* Contact
* Product
* SaleOrder
* SaleOrderLine

Relationships between models have also been defined.

---

# Repository Layer

A generic Base Repository has been implemented to avoid duplicated CRUD logic.

Concrete repositories currently include:

* ContactRepository
* ProductRepository
* SaleOrderRepository

Repository tests have been started as part of the project.

---

# Development Commands

All backend commands are executed through **uv** inside the backend container.

Examples:

Create migration:

```bash
docker compose exec backend uv run alembic revision --autogenerate -m "message"
```

Apply migrations:

```bash
docker compose exec backend uv run alembic upgrade head
```

Run tests:

```bash
docker compose exec backend uv run pytest
```

---

# Remaining Work

Because of the limited implementation time, the following components were planned but not completed:

* Odoo Adapter Layer
* Synchronization Services
* XML-RPC abstraction
* Sync Scheduler
* Retry mechanism
* Synchronization logging
* Sync history
* Error handling improvements
* API endpoints
* Complete test suite

The project structure has already been prepared for these components, allowing them to be implemented without major architectural changes.

---

# Design Decisions

Several design choices were made to keep the project maintainable:

* Layered Architecture
* Repository Pattern
* Environment-based configuration using Pydantic Settings
* Dockerized development environment
* Alembic migrations
* Generic repositories to reduce duplicated code
* Separation between Odoo integration and business logic
* Dedicated seed module isolated from the backend

---

# Notes

This repository represents the architectural foundation of the synchronization service.

The infrastructure, project organization, database layer, migration system, repository layer and automatic Odoo data seeding have all been completed.

The remaining work mainly consists of implementing synchronization workflows and business services on top of the existing architecture.
