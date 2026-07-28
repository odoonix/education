"""
اینجا Engine (اتصال به دیتابیس) و Session (برای خواندن/نوشتن) ساخته میشه.
بقیه‌ی کد پروژه فقط از تابع get_session() استفاده می‌کنه، نباید مستقیم
اینجا رو import کنن و engine بسازن.
"""
import os
from pathlib import Path

# ۱. تعریف بیس مسیر پروژه
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ۲. بارگذاری محیط قبل از هرگونه import مربوط به تنظیمات
def _auto_load_env():
    env_file = BASE_DIR / ".env.local"
    if not env_file.exists():
        env_file = BASE_DIR / ".env"

    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


_auto_load_env()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings


engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session():
    """
    یک Session جدید می‌سازه. استفاده‌ی پیشنهادی با context manager:

        with get_session() as session:
            session.add(obj)
            session.commit()
    """
    return SessionLocal()
