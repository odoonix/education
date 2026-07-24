FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir -e .

COPY migrations ./migrations
COPY alembic.ini ./alembic.ini

CMD ["sh", "-c", "alembic upgrade head && python -m backend.cli"]