# User Documentation — راهنمای نصب و اجرا

این راهنما فرض می‌کنه پروژه رو تازه Clone/Fork کردی و می‌خوای از صفر اجراش کنی.

## پیش‌نیازها

- Docker و Docker Compose
- Python 3.11 یا بالاتر (فقط لازم داری اگه بخوای روش ۲ رو انجام بدی)

این پروژه رو میشه به ۲ روش اجرا کرد:
- **روش ۱ (پیشنهادی، طبق مستندات آزمون): کامل داخل Docker**
- **روش ۲: دستی روی سیستم خودت** (برای توسعه/دیباگ راحت‌تر)

---

## روش ۱: اجرای کامل با Docker

### مرحله ۱: بالا آوردن همه‌چیز

```bash
docker compose up -d
```

این دستور Odoo، دیتابیس اختصاصی Odoo، دیتابیس اپلیکیشن، و Backend پایتون
(سرویس `app`، که به‌محض بالا اومدن `alembic upgrade head` رو خودکار اجرا
می‌کنه) رو بالا میاره. با این دستور مطمئن شو `healthy` شدن:

```bash
docker compose ps
```

### مرحله ۲: ساخت دیتابیس در Odoo (یک‌بار، دستی)

این تنها قدمیه که خودکار نیست (چون Odoo تازه‌نصب‌شده هیچ دیتابیسی نداره و
ساختنش نیاز به وارد کردن دستی اطلاعات داره):

1. برو به `http://localhost:8069`
2. تو فرم "Create Database":
   - Database Name: `sync_test`
   - Email: هرچی دلت خواست
   - Password: یه پسورد بذار و یادت بمونه
   - تیک Demo Data رو بردار
3. بعد از ساخت، از منوی **Apps** اپ **Sales** رو نصب کن.

### مرحله ۳: فایل `.env` رو با پسورد واقعی پر کن

```bash
cp .env.example .env
```

`ODOO_PASSWORD` رو با پسوردی که تو مرحله‌ی ۲ ساختی جایگزین کن.
`docker-compose.yml` این مقدار رو از همین فایل می‌خونه و به کانتینر `app`
تزریق می‌کنه (بدون اینکه خود `.env` وارد Docker Image بشه).

اگه `.env` رو بعد از `docker compose up` عوض کردی:
```bash
docker compose up -d app
```

### مرحله ۴: ساخت داده‌ی تستی در Odoo

```bash
docker compose run --rm app python odoo/init_data.py
```

### مرحله ۵: اجرای Sync

```bash
docker compose run --rm app python -m src.main
```

هر چندبار بخوای می‌تونی دوباره اجراش کنی — به‌خاطر Idempotent Design، داده‌ی
تکراری ساخته نمیشه.

### مرحله ۶: اجرای تست‌ها

```bash
docker compose run --rm app pytest -v
```

---

## روش ۲: اجرای دستی روی سیستم خودت (برای توسعه)

### مرحله ۱: بالا آوردن Odoo و PostgreSQL

```bash
docker compose up -d odoo odoo-db app-db
```

(سرویس `app` رو صدا نمی‌زنیم، چون خودمون دستی کد رو اجرا می‌کنیم)

### مرحله ۲: ساخت دیتابیس در Odoo

مثل روش ۱، از طریق `http://localhost:8069`.

### مرحله ۳: تنظیم فایل `.env`

```bash
cp .env.example .env
```

مقادیر زیر رو با مقادیر واقعی خودت جایگزین کن:

```
ODOO_URL=http://localhost:8069
ODOO_DB=sync_test
ODOO_USERNAME=admin
ODOO_PASSWORD=<پسوردی که تو مرحله ۲ ساختی>

APP_DB_HOST=localhost
APP_DB_PORT=5433
```

> **نکته:** چون این‌بار کد رو مستقیم روی ویندوز/مک/لینوکس خودت اجرا
> می‌کنی (نه داخل کانتینر)، همیشه از `localhost` استفاده کن، نه اسم
> سرویس‌های داکر مثل `odoo` یا `app-db` (آن‌ها فقط از *داخل* شبکه‌ی
> داکر قابل‌شناساییند).

### مرحله ۴: نصب پکیج‌های پایتون

```bash
python -m venv .venv
source .venv/bin/activate        # ویندوز: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### مرحله ۵: ساخت جدول‌های PostgreSQL

```bash
alembic upgrade head
```

### مرحله ۶: ساخت داده‌ی تستی در Odoo

```bash
python odoo/init_data.py
```

این اسکریپت idempotent هست — اگه دوباره اجراش کنی، رکورد تکراری نمی‌سازه.

### مرحله ۷: اجرای فرآیند Sync اصلی

```bash
python -m src.main
```

خروجی موفق:
```
========== نتیجه‌ی Sync ==========
contacts_sync             | fetched=  3  created=  3  updated=  0  failed=  0  status=success
products_sync             | fetched=  3  created=  3  updated=  0  failed=  0  status=success
sale_orders_sync          | fetched=  3  created=  3  updated=  0  failed=  0  status=success
sale_order_lines_sync     | fetched=  5  created=  5  updated=  0  failed=  0  status=success
===================================
```

می‌تونی این دستور رو چندبار اجرا کنی؛ بار دوم به بعد باید `created=0` و
`updated>0` ببینی (یعنی رکورد تکراری ساخته نشده). از دومین اجرا به بعد،
Sync به‌شکل Incremental انجام میشه — یعنی فقط رکوردهایی که از آخرین Sync
موفق به بعد تو Odoo تغییر کردن خونده میشن، نه کل جدول.

لاگ‌ها هم‌زمان تو Terminal، فایل `sync.log`، و جدول‌های `sync_runs` /
`sync_logs` داخل PostgreSQL ثبت میشن.

### مرحله ۸: اجرای تست‌ها

```bash
pytest -v
```

برای دیدن Test Coverage:
```bash
pytest --cov=src --cov-report=term-missing
```

---

## بررسی مستقیم داده‌ها (اختیاری)

```bash
python -c "from src.db.session import get_session; from src.db.models import Contact; s = get_session(); print([c.name for c in s.query(Contact).all()])"
```

## تست Graceful Shutdown (اختیاری)

وسط اجرای `python -m src.main` یه Ctrl+C بزن (یا اگه داخل Docker اجرا شده،
`docker compose stop app` رو بزن). باید تو لاگ ببینی که پیام "سیگنال توقف
دریافت شد" چاپ میشه و برنامه تمیز بسته میشه، بدون خرابی داده. اگه دوباره
`sync_runs` رو چک کنی، یه ردیف با `status='cancelled'` می‌بینی.

## اگه چیزی کار نکرد

- **`ConnectionRefusedError`**: مطمئن شو `docker compose ps` نشون میده
  `odoo` و `app-db` روشن و healthy هستن.
- **خطای احراز هویت Odoo**: مقادیر `ODOO_USERNAME`/`ODOO_PASSWORD`/`ODOO_DB`
  رو تو `.env` با چیزی که موقع ساخت دیتابیس (مرحله ۲) وارد کردی مقایسه کن.
- **`could not translate host name`**: تو روش ۲ (اجرای دستی)، جایی تو
  `.env` از اسم سرویس داکر (`odoo`, `app-db`) به‌جای `localhost` استفاده
  شده. تو روش ۱ (Docker)، این پیام عادی نیست و یعنی سرویس `app` هنوز به
  شبکه‌ی داکر وصل نشده — `docker compose ps` رو چک کن.
