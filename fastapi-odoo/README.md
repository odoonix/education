# FastAPI + Odoo Multi-Layer Project

FastAPI with layered architecture, PostgreSQL, SQLAlchemy/Alembic, and Odoo — all via Docker Compose.

## Services


| Service | URL                                                      | Role                |
| ------- | -------------------------------------------------------- | ------------------- |
| `api`   | [http://localhost:8000/docs](http://localhost:8080/docs) | FastAPI app         |
| `db`    | [http://localhost:5432](http://localhost:5432)           | PostgreSQL (shared) |
| `odoo`  | [http://localhost:8069](http://localhost:8069)           | Odoo 17             |


# User Manual

## Start everything

```bash
docker compose up --build
```

1. Open **[http://localhost:8069](http://localhost:8069)** and create an Odoo database named `odoo` (master password: `odoo` from `.env`).
2. Set admin email/password (defaults expected by the API: `admin` / `admin` — or update `ODOO_USER` / `ODOO_PASSWORD` in `.env`).
3. Open **[http://localhost:8080/docs](http://localhost:8000/docs)** and try:
  - `GET /api/v1/health`
  - `GET /api/v1/odoo/health`
  - `POST /api/v1/odoo/seed-demo` then `/api/v1/sync`


# Technical Docs

## Architecture

```
app/
├── api/            # Routers + DI
├── schemas/        # Pydantic models
├── services/       # Business logic
├── repositories/   # SQLAlchemy data access
├── models/         # ORM entities
├── integrations/   # Odoo XML-RPC client
├── core/           # Settings + DB session
└── main.py
```


## Odoo → FastAPI sync

Entities are synced from Odoo by `odoo_id`. Existing records are **updated**, new ones are **created**.


| Odoo model        | Local entity       |
| ----------------- | ------------------ |
| `res.partner`     | `contacts`         |
| `product.product` | `products`         |
| `sale.order`      | `sale_orders`      |
| `sale.order.line` | `sale_order_lines` |




### Workflow

1. Start stack: `docker compose up --build`
2. Will create Odoo DB  and activate the eCommerce in it at [http://localhost:8069](http://localhost:8069)
3. Seed demo data in Odoo: `POST /api/v1/odoo/seed-demo`
4. Sync into Postgres: `POST /api/v1/sync`
5. Read local data:
  - `GET /api/v1/contacts`
  - `GET /api/v1/products`
  - `GET /api/v1/sale-orders`

Re-run `POST /api/v1/sync` anytime — changed Odoo records will update existing rows.

Partial sync endpoints: `/api/v1/sync/contacts`, `/sync/products`, `/sync/sale-orders`.

## Useful API routes


| Method | Path                     | Description                     |
| ------ | ------------------------ | ------------------------------- |
| GET    | `/api/v1/health`         | API liveness                    |
| GET    | `/api/v1/odoo/health`    | Odoo XML-RPC connectivity       |
| POST   | `/api/v1/odoo/seed-demo` | Create sample Odoo records      |
| POST   | `/api/v1/sync`           | Full sync (upsert all entities) |
| GET    | `/api/v1/contacts`       | Local contacts                  |
| GET    | `/api/v1/products`       | Local products                  |
| GET    | `/api/v1/sale-orders`    | Local sale orders with lines    |




## BreakeThrought

In this project we implemented an automated setup of **odoo server** for a ***eCommerce*** website(within docker compose) and a **fastAPI backend** that can fetch its data including contacts, products, sale orders and sale order items(lines). for database we used a **postgresql** that host two db, one for odoo server and one for fastAPI service.

We used **SQLAlchemy** for ORM and **alembic** for migration managments. also used pydantic for better validation over tranfering data(DTOs).

We implemented a `XML-RPC client` for connecting to **odoo server** from our backend. for seeding demo data to our odoo server we implemented an additional method that stores *hard coded* demo data for all requested entities in the odoo client.

For syncing the data between **odoo server** and our **FastAPI** service we have a serive named `sync_service`and added routes to call this service`POST /api/v1/sync`. we can also implement a scheduled job(cronjob, apscheduler, fastapi scheduler, Celery) to call this service periodically or call it when some event happened, also there is some partial sync methods for when you know what part is not in sync between backend and odoo(based on the event that happened).

Syncing process is a step by step process, in the first we have to sync contacts and product(cant sync sale orders first) so when they are synced we can move to sale orders and for each of them can sync ther order items(lines). after syncing all of sale orders and their items syncing process is finished. by this knowledge in the partial sync of sale orders we should first sync the contacts and products first(prevent not exist refernces).

In the sync process we have two log mecanism, one for traking sync requests named `sync_run`, that work as a decorator that wrapes the public methods of `sync_service`(`sync_all`, `sync_contacts` and etc), the other one that persist logs about each records syncing named `sync_log`, and also related to the `sync_run`. it stores data about each record fetched from odoo and what happend for it in our backend system(insert, update or failed) and have been implemeted in the private methods of `sync_service` that operates on records on after another.

## Migrations

Any time you made achange to your models or add a new one first make sure it is imported in `fastapi-odoo\alembic\env.py` and the run the folowing commands for auto generation of migration and apply that migration to your database.

```bash
docker compose exec api alembic revision --autogenerate -m "describe change"
docker compose exec api alembic upgrade head
```



## Local API (optional)

If you wish to start the fastAPI app without the docker(deploy localy) run following commands in the terminal

```bash
python -m venv .venv
source .venv\bin\activate
pip install -r requirements.txt
cp .env.example .env
# Point DATABASE_URL at localhost, ODOO_HOST at localhost
alembic upgrade head
uvicorn app.main:app --reload
```

