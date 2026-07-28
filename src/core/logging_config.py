"""
یک‌بار تو ابتدای main.py صدا زده میشه و کل سیستم Logging پروژه رو راه
می‌اندازه. لاگ‌ها هم‌زمان به دو جا میرن:
  ۱. Standard Output (خود Terminal) — برای دیدن آنی وضعیت
  ۲. فایل sync.log — برای بررسی بعدی یا اگه کسی Terminal رو نبینه

(علاوه بر این دوتا، جزئیات هر Sync Run تو جدول sync_runs/sync_logs هم
ذخیره میشه — اون بخش تو BaseSyncService انجام میشه.)
"""

import logging
import sys
from src.config.settings import settings
from logging.handlers import RotatingFileHandler

def setup_logging() -> None:
    #لاگ های فراتر از Info رو به من نمایش میده 
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # تعیین فرمت لاگ ها
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # تنظیمات لاگ ریشه
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # نمایش لاگ ها روی ترمینال
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # نگهداری لاگ فایل ها بامدیریت حجم
    file_handler = RotatingFileHandler(
        "sync.log",
        maxBytes=5 * 1024 * 1024, 
        backupCount=3,              
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # عدم ذخیره لاگ های کتاب خانه های جانبی مثل warning , info , ...
    NOISY_LOGGERS = ["urllib3", "requests", "sqlalchemy.engine", "psycopg2"]
    for logger_name in NOISY_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
