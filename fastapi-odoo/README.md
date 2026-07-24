# Odoo Sync Service

A Python service that synchronizes data from Odoo 18 into a separate PostgreSQL database.

The service currently synchronizes:

* Contacts
* Products
* Sale Orders
* Sale Order Lines

The project uses:

* Python 3.12+
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL
* Docker Compose
* Odoo 18

## Project Structure

```text
.
├── app/
│   ├── adapters/       # Odoo API communication and DTO validation
│   ├── api/             # HTTP API endpoints
│   ├── config/          # Application configuration
│   ├── database/        # SQLAlchemy database setup
│   ├── models/          # Database models and DTOs
│   ├── repositories/    # Database access
│   └── services/        # Synchronization business logic
│
├── migrations/          # Alembic database migrations
├── scripts/             # Development and verification scripts
├── compose.yaml
├── Dockerfile
├── alembic.ini
├── pyproject.toml
├── .env.example
└── README.md
```

## Requirements

For the recommended Docker setup:

* Docker
* Docker Compose

For local development:

* Python 3.12+
* PostgreSQL

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

The application requires configuration for:

* Odoo
* Application PostgreSQL database
* Odoo authentication

When running the application inside Docker, Docker service names must be used instead of `localhost`.

For example:

```env
DATABASE_URL=postgresql+psycopg://app:app@app-db:5432/odoo_sync
ODOO_URL=http://odoo:8069
```

When running the Python application directly on the host machine, the database is exposed on port `5433`:

```env
DATABASE_URL=postgresql+psycopg://app:app@localhost:5433/odoo_sync
ODOO_URL=http://localhost:8069
```

## Running with Docker Compose

Start the complete environment:

```bash
docker compose up --build
```

This starts:

* Odoo
* PostgreSQL for Odoo
* PostgreSQL for the synchronization service
* The Python synchronization service

The services are available at:

```text
Odoo:
http://localhost:8069

Sync API:
http://localhost:8000

Swagger API documentation:
http://localhost:8000/docs
```

To stop the services:

```bash
docker compose down
```

To stop the services while removing orphan containers:

```bash
docker compose down --remove-orphans
```

## Database Migrations

The project uses Alembic for database migrations.

To apply migrations manually:

```bash
python -m alembic upgrade head
```

To create a new migration:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

When running the service in Docker, migrations are applied during container startup.

## API

### Health Check

```text
GET /health
```


### Run Full Synchronization

```text
POST /sync
```

The synchronization process runs in this order:

```text
1. Contacts
2. Products
3. Sale Orders
4. Sale Order Lines
```

The synchronization flow resolves relationships between Odoo records and local PostgreSQL records.

## Synchronization Behavior

The synchronization is idempotent.

Records are identified by their original Odoo ID.

On the first synchronization:

```text
Odoo record
    ↓
No local record found
    ↓
Create local record
```

On subsequent synchronizations:

```text
Odoo record
    ↓
Local record found by Odoo ID
    ↓
Update existing local record
```

This prevents duplicate records when synchronization is executed repeatedly.

## Development

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
pip install -e .
```

Run the application:

```powershell
python -m app.main
```

Alternatively:

```powershell
uvicorn app.main:app --reload
```

Run development scripts using module syntax:

```powershell
python -m scripts.test_settings
python -m scripts.test_database_connection
python -m scripts.test_adapters
```

## Architecture

The application follows a layered architecture:

```text
API
 │
 ▼
Services
 │
 ├── Adapters ───────► Odoo
 │
 └── Repositories ───► PostgreSQL
```

### Adapters

Adapters communicate with Odoo and convert Odoo responses into validated application data structures.

### Services

Services contain synchronization logic, including:

* Fetching data
* Finding existing records
* Creating new records
* Updating existing records
* Resolving relationships between entities
* Recording synchronization logs

### Repositories

Repositories handle database operations and isolate SQLAlchemy/database access from the synchronization logic.

### Database Models

The local PostgreSQL database stores synchronized data and synchronization history.

The main entities are:

* Contacts
* Products
* Sale Orders
* Sale Order Lines
* Sync Runs
* Sync Logs

## Notes

The Odoo instance is used as the source system. The local PostgreSQL database stores the synchronized application data.

The Odoo database and the application database are separate PostgreSQL databases.

The synchronization service communicates with both Odoo and the application database through the Docker Compose network when running in Docker.
