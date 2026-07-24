
# Integrate with Odoo

This project implements a backend synchronization service between Odoo ERP and PostgreSQL.

The solution runs Odoo and it's PostgreSQL database using Docker, then connects to Odoo through it's XML-RPC API. During synchronization, the backend retrieves Contacts, Products, Sale Orders, and Sale Order Lines, maps the external Odoo data into internal models, and persists them in a separate PostgreSQL database.

## How to run the project

clone the project

```bash
    git clone https://github.com/javadnr/education.git
```
    
build the docker images

```bash
    make build
```

run the container

```bash
    make up
```

connect to backend service to create alembic changes


```bash
    make shell
    alembic revision --autogenerate -m "init"
```

make migration to database

```bash
    make migrate
```


## how it works

After we ran the docker container the backend starts to get the data from api and sync to it's database I added 2 functions in the project to run the backend in loop or run it just 1 time.

you can specify the run type in .env file and I putted a .env.example file to see the vars you can set.

## tests
To run tests 

```bash
    make build test
```

## Architecture decisions

The application is designed using a layered architecture with clear separation of concerns. Odoo communication is isolated in an adapter layer, business logic is implemented in services, database access is encapsulated by repositories, and mapping logic is handled by dedicated mappers. This design keeps the system modular, testable, and easy to extend.


## Known Limitations

The current implementation satisfies the requirements of the technical assignment; however, several areas can be improved for a production-scale environment:

Synchronization is manually triggered and does not include a scheduling mechanism. In a production environment, it could be executed periodically using a scheduler such as Celery Beat or Cron.

The project currently performs synchronization in a single process. Queue-based processing (e.g., RabbitMQ with background workers) would improve scalability for high-volume workloads.

Conflict detection is limited to the Odoo ID. More advanced synchronization strategies, such as version comparison or timestamp-based conflict resolution, can be added if required.

Monitoring and metrics collection (e.g., Prometheus and Grafana) are outside the scope of this assignment.

Authentication, authorization, and API endpoints are not implemented because the assignment focuses on synchronization between Odoo and PostgreSQL rather than exposing a public backend API.