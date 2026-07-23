# FastAPI + Odoo Multi-Layer Project

FastAPI with layered architecture, PostgreSQL, SQLAlchemy/Alembic, and Odoo — all via Docker Compose.

## Services

| Service | URL | Role |
|---------|-----|------|
| `api` | http://localhost:8000/docs | FastAPI app |
| `db` | localhost:5432 | PostgreSQL (shared) |
| `odoo` | http://localhost:8069 | Odoo 17 |

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

## Start everything

```bash
docker compose up --build
```

1. Open **http://localhost:8069** and create an Odoo database named `odoo` (master password: `odoo` from `.env`).
2. Set admin email/password (defaults expected by the API: `admin` / `admin` — or update `ODOO_USER` / `ODOO_PASSWORD` in `.env`).
3. Open **http://localhost:8000/docs** and try:
   - `GET /api/v1/health`
   - `GET /api/v1/odoo/health`
   - `POST /api/v1/items` then `POST /api/v1/items/{id}/sync-odoo`

## Odoo → FastAPI sync

Entities are synced from Odoo by `odoo_id`. Existing records are **updated**, new ones are **created**.

| Odoo model | Local entity |
|------------|--------------|
| `res.partner` | `contacts` |
| `product.product` | `products` |
| `sale.order` | `sale_orders` |
| `sale.order.line` | `sale_order_lines` |

### Workflow

1. Start stack: `docker compose up --build`
2. Create Odoo DB at http://localhost:8069 (name: `odoo`, master pwd: `odoo`)
3. Install the **Sales** app in Odoo (Apps → Sales → Activate)
4. Seed demo data in Odoo: `POST /api/v1/odoo/seed-demo`
5. Sync into Postgres: `POST /api/v1/sync`
6. Read local data:
   - `GET /api/v1/contacts`
   - `GET /api/v1/products`
   - `GET /api/v1/sale-orders`

Re-run `POST /api/v1/sync` anytime — changed Odoo records will update existing rows.

Partial sync endpoints: `/api/v1/sync/contacts`, `/sync/products`, `/sync/sale-orders`.

## Useful API routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | API liveness |
| GET | `/api/v1/odoo/health` | Odoo XML-RPC connectivity |
| POST | `/api/v1/odoo/seed-demo` | Create sample Odoo records |
| POST | `/api/v1/sync` | Full sync (upsert all entities) |
| GET | `/api/v1/contacts` | Local contacts |
| GET | `/api/v1/products` | Local products |
| GET | `/api/v1/sale-orders` | Local sale orders with lines |

## Migrations

```bash
docker compose exec api alembic revision --autogenerate -m "describe change"
docker compose exec api alembic upgrade head
```

## Local API (optional)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Point DATABASE_URL at localhost, ODOO_HOST at localhost
alembic upgrade head
uvicorn app.main:app --reload
```
