"""
تمام تنظیمات پروژه از اینجا خونده میشه. اگه فردا خواستی یه env variable
جدید اضافه کنی، فقط همینجا اضافه‌اش می‌کنی و بقیه‌ی کد بدون تغییر می‌مونه.
"""

import os
from dotenv import load_dotenv
from pathlib import Path


#پیدا کردن مسیر ریشه از دو لایه بالاتر
BASE_DIR = Path(__file__).resolve().parent.parent.parent

#روی محیط local با .env.local کار میکنه و روی محیط پروداکشن با .env 
env_file = BASE_DIR / ".env.local"
if not env_file.exists():
    env_file = BASE_DIR / ".env"

if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=True)


class Settings:
    def __init__(self):
        #تنظمیات odoo
        self.ODOO_URL: str = os.getenv("ODOO_URL", "http://localhost:8069")
        self.ODOO_DB: str = os.getenv("ODOO_DB", "my_odoo_project") 
        self.ODOO_USERNAME: str = os.getenv("ODOO_USERNAME", "admin@gmail.com")
        self.ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD", "Mohamad@77")

        # تنظمیات postgresql
        self.APP_DB_HOST: str = os.getenv("APP_DB_HOST", "localhost")
        self.APP_DB_PORT: int = int(os.getenv("APP_DB_PORT", "5432")) 
        self.APP_DB_NAME: str = os.getenv("APP_DB_NAME", "syncdb")
        self.APP_DB_USER: str = os.getenv("APP_DB_USER", "syncuser")
        self.APP_DB_PASSWORD: str = os.getenv("APP_DB_PASSWORD", "syncpass")


        # تنظیمات لاگ ها
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        
    #اتصال به DB
    @property
    def database_url(self) -> str:
        """Connection string کامل برای SQLAlchemy."""
        return (
            f"postgresql+psycopg2://{self.APP_DB_USER}:{self.APP_DB_PASSWORD}"
            f"@{self.APP_DB_HOST}:{self.APP_DB_PORT}/{self.APP_DB_NAME}"
        )


settings = Settings()
