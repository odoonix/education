.PHONY: help up down build logs restart migrate test shell seed clean

help:
	@echo "Available commands:"
	@echo "  make up        - Start all containers"
	@echo "  make down      - Stop all containers"
	@echo "  make build     - Build docker images"
	@echo "  make logs      - Show container logs"
	@echo "  make restart   - Restart containers"
	@echo "  make migrate   - Run database migrations"
	@echo "  make test      - Run tests"
	@echo "  make shell     - Open backend shell"
	@echo "  make seed      - Seed Odoo test data"
	@echo "  make clean     - Remove containers and volumes"


up:
	sudo docker compose up


build:
	sudo docker compose build


down:
	sudo docker compose down


restart:
	sudo docker compose restart


logs:
	sudo docker compose logs -f


migrate:
	sudo docker compose exec backend alembic upgrade head


build test:
	sudo docker compose --profile test build tests
	
test:
	sudo docker compose --profile test run --rm tests



shell:
	sudo docker compose exec backend bash


seed:
	sudo docker compose exec backend python -m scripts.seed_odoo.main


clean:
	sudo docker compose down -v