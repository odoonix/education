from fastapi import APIRouter

from app.api.routes import odoo, sync

api_router = APIRouter()
api_router.include_router(odoo.router)
api_router.include_router(sync.router)


@api_router.get("/health", tags=["health"])
def api_health() -> dict[str, str]:
    return {"status": "ok"}
