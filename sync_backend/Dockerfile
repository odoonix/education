FROM python:3.12-slim AS runtime

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/sync_backend/.venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 app

COPY --from=ghcr.io/astral-sh/uv:0.5.13 /uv /usr/local/bin/uv

WORKDIR /app
COPY sync_backend/pyproject.toml sync_backend/uv.lock* /app/sync_backend/
WORKDIR /app/sync_backend
RUN if [ -f uv.lock ]; then uv sync --frozen --no-dev; else uv sync --no-dev; fi

COPY sync_backend /app/sync_backend
RUN uv sync --frozen --no-dev --reinstall-package odoo-sync
RUN chown -R app:app /app
USER app

ENTRYPOINT []
CMD ["python", "-m", "odoo_sync", "sync", "--full"]

FROM runtime AS test
USER root
RUN uv sync --all-groups
RUN chown -R app:app /app
USER app
