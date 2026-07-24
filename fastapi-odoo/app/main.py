from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.sync import router as sync_router


app = FastAPI(
    title="Odoonix Sync Service",
    version="1.0.0",
)


app.include_router(
    health_router,
)

app.include_router(
    sync_router,
)