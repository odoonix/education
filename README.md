# Odoo ⇄ PostgreSQL Sync

پروژه‌ی همگام‌سازی داده (Contacts, Products, Sale Orders, Sale Order Lines)
از Odoo به PostgreSQL، با معماری لایه‌ای (Layered Architecture)، طراحی
Idempotent، مدیریت خطای پیشرفته، Retry Mechanism، Incremental Sync و
Graceful Shutdown.

## معماری

```
Odoo (XML-RPC) → OdooClient → Mapper → Service Layer → Repository → PostgreSQL
```

جزئیات کامل معماری، تصمیمات طراحی و محدودیت‌های شناخته‌شده:
📄 [`docs/TECHNICAL_DOCUMENTATION.md`](docs/TECHNICAL_DOCUMENTATION.md)

## شروع سریع

راهنمای کامل قدم‌به‌قدم (هم روش Docker، هم روش دستی):
📄 [`docs/USER_DOCUMENTATION.md`](docs/USER_DOCUMENTATION.md)

خلاصه‌ی فوق‌فشرده (روش Docker):

```bash
docker compose up -d                              # بالا آوردن همه‌چیز
# ... ساخت دیتابیس Odoo از طریق مرورگر (جزئیات تو USER_DOCUMENTATION) ...
cp .env.example .env                               # و پر کردن پسورد
docker compose run --rm app python odoo/init_data.py   # داده‌ی تستی
docker compose run --rm app python -m src.main          # اجرای Sync
docker compose run --rm app pytest -v                    # اجرای تست‌ها
```

## ساختار پروژه

```
Dockerfile                 تصویر Docker برنامه‌ی Backend
docker-compose.yml          Odoo + دیتابیس‌ها + Backend
odoo/init_data.py           ساخت داده‌ی تستی در Odoo (idempotent)
src/
  odoo_client/               اتصال به Odoo (XML-RPC) + Retry + Incremental
  domain/                    Domain Models (dataclass تمیز)
  mappers/                   تبدیل داده‌ی خام Odoo به Domain Model
  repositories/               ذخیره در PostgreSQL با Upsert idempotent
  services/                   Orchestration + مدیریت خطا + Logging + Graceful Shutdown
  db/                         مدل‌های SQLAlchemy + Session
  core/                       Retry decorator + Logging config
  main.py                     نقطه‌ی ورود اصلی
migrations/                  Alembic migrations
tests/unit/                  Unit Testها (pytest + mock، بدون نیاز به Odoo واقعی)
scripts/                     اسکریپت‌های کمکی برای تست دستی هر لایه
docs/                        مستندات فنی و کاربری
```

## تکنولوژی‌ها

Python · SQLAlchemy · Alembic · PostgreSQL · Docker · Odoo (XML-RPC) · pytest

## وضعیت پروژه

- [x] Docker Compose (Odoo + PostgreSQL + Backend، همه با `docker compose up`)
- [x] داده‌ی تستی در Odoo (اسکریپت idempotent)
- [x] مدل‌های SQLAlchemy + Alembic Migration
- [x] Client اتصال به Odoo با Pagination
- [x] Domain Models + Mapper (با Abstract Base Class)
- [x] Repository Layer (Upsert idempotent)
- [x] Service Layer (Orchestration + مدیریت خطا با SAVEPOINT)
- [x] Retry Mechanism (Exponential Backoff) + Structured Logging
- [x] Incremental Sync (بر پایه‌ی `write_date`)
- [x] Graceful Shutdown (مدیریت SIGTERM/Ctrl+C)
- [x] Unit Tests (۲۳ تست، Mapper/Repository/Service/Retry)
- [x] مستندات فنی و کاربری
