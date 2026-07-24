from sqlalchemy import text

from app.database.connection import SessionLocal


with SessionLocal() as session:
    result = session.execute(
        text("SELECT 1")
    )

    print(result.scalar())