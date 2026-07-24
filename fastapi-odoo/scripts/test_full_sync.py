from app.container import create_full_sync_service
from app.database.connection import SessionLocal

with SessionLocal() as session:
    try:
        full_sync_service = create_full_sync_service(session)

        sync_run = full_sync_service.sync()

        session.commit()

        print(
            f"Sync {sync_run.id} completed successfully",
        )

    except Exception:
        session.rollback()

        raise
