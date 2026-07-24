#!/bin/sh
set -e

echo ">> Applying database migrations (alembic upgrade head)..."
alembic upgrade head

echo ">> Running sync pipeline..."
python -m app.main
