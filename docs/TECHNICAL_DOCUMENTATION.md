# Technical Documentation

## معماری کلی

```
Odoo (XML-RPC)
      │
      ▼
OdooClient  (src/odoo_client/client.py)
      │  raw dict
      ▼
Mapper  (src/mappers/)
      │  Domain Model (dataclass تمیز)
      ▼
Service Layer  (src/services/)
      │  orchestration + error handling + logging
      ▼
Repository  (src/repositories/)
      │  Upsert (Idempotent)
      ▼
PostgreSQL  (src/db/models.py — SQLAlchemy ORM)
```

هر پیکان یک لایه‌ی مجزاست که فقط با لایه‌ی مجاور خودش کار می‌کنه. این
Layered Architecture باعث میشه:
- تغییر یک لایه (مثلاً عوض‌کردن Odoo با یه سیستم دیگه) بقیه رو خراب نکنه
- هر لایه جدا و مستقل تست بشه (`tests/unit/`)

## تصمیمات مهم معماری

### ۱. چرا Repository Pattern؟
Business Logic (Service Layer) نباید بدونه SQLAlchemy چطور کار می‌کنه.
Repositoryها این جزئیات رو مخفی می‌کنن و یک API ساده (`upsert`,
`get_by_odoo_id`) در اختیار Service Layer می‌ذارن.

### ۲. چطور Idempotency پیاده‌سازی شده؟
هر جدولی که از Odoo میاد یک ستون `odoo_id` با `UNIQUE constraint` داره.
`BaseRepository.upsert()` قبل از insert، با `odoo_id` جستجو می‌کنه:
- پیدا شد → فیلدها رو آپدیت می‌کنه
- پیدا نشد → رکورد جدید می‌سازه



پس اجرای مکرر `python -m src.main` هیچ‌وقت رکورد تکراری نمی‌سازه.



### ۳. مدیریت خطا بدون متوقف‌کردن کل فرآیند
از تکنیک **SAVEPOINT** (`session.begin_nested()`) استفاده شده. هر رکورد
داخل یک SAVEPOINT پردازش میشه؛ اگه اون رکورد خطا بده، فقط تغییرات همون
رکورد rollback میشه، نه کل Transaction. این یعنی رکورد ۱ و ۲ موفق می‌مونن
حتی اگه رکورد ۳ خطا بده و رکورد ۴ و ۵ هم پردازش بشن — دقیقاً طبق سناریوی
درخواستی.

### ۴. چرا Retry فقط روی خطاهای شبکه‌ای اعمال شده، نه همه‌چیز؟
اگه پسورد Odoo غلط باشه، retry کردن ۳ باره فایده‌ای نداره (نتیجه همیشه یکیه).
`src/core/retry.py` یک لیست `NON_RETRYABLE_EXCEPTIONS` داره
(`ValueError`, `TypeError`, `KeyError`, `AttributeError`, `IndexError`,
`KeyboardInterrupt`, `SystemExit`) که این خطاها **هیچ‌وقت** retry نمیشن —
حتی اگه صراحتاً تو پارامتر `exceptions` هم پاس داده بشن — چون این‌ها معمولاً
یعنی باگ تو کد یا داده، نه یه مشکل موقتی شبکه. Retry فقط برای خطاهای واقعاً
گذرا مثل `ConnectionError`, `OSError`, `TimeoutError` فعال شده، با
Exponential Backoff (و یک سقف `max_delay` که تأخیر بی‌نهایت زیاد نشه).

### ۵. Dependency Injection
`Session` و `OdooClient` همیشه از بیرون به Repository/Service تزریق میشن
(نه اینکه خودشون بسازنش). این باعث میشه تو تست‌ها بتونیم `OdooClient` رو با
`unittest.mock.MagicMock` جایگزین کنیم و به Odoo واقعی وصل نشیم.

## طراحی دیتابیس

جدول‌های اصلی: `contacts`, `products`, `sale_orders`, `sale_order_lines`

روابط:
- `sale_orders.customer_id` → FK به `contacts.id`
- `sale_order_lines.sale_order_id` → FK به `sale_orders.id`
- `sale_order_lines.product_id` → FK به `products.id`

جدول‌های Logging: `sync_runs` (خلاصه‌ی هر اجرای Sync)، `sync_logs`
(جزئیات هر خطا، وابسته به `sync_runs` با FK).

هر ۴ جدول اصلی یک ستون `odoo_id` (UNIQUE) دارن که کلید Idempotency هستن.

### ۶. چطور کل پروژه با `docker compose up` بالا میاد؟
`Dockerfile` سرویس `app` رو می‌سازه که به Backend پایتون تبدیلش می‌کنه.
پیش‌فرض این سرویس، فقط `alembic upgrade head` (ساخت جدول‌ها) رو اجرا
می‌کنه — چون ساخت دیتابیس Odoo (طبق سناریوی آزمون) یک قدم دستیه که باید
از طریق مرورگر انجام بشه، و نمی‌تونیم مطمئن باشیم قبل از اولین
`docker compose up` انجام شده یا نه. بعد از انجام اون قدم دستی، Sync واقعی
با این دستور اجرا میشه:
```
docker compose run --rm app python -m src.main
```
تنظیمات شبکه‌ای (`ODOO_URL=http://odoo:8069`, `APP_DB_HOST=app-db`) مستقیم
تو `docker-compose.yml` (بخش `environment` سرویس `app`) ست شدن، چون این
کانتینر داخل شبکه‌ی داکر اجرا میشه و باید از اسم سرویس‌ها استفاده کنه، نه
`localhost`. مقادیر حساس (پسورد و ...) از فایل `.env` (که هیچ‌وقت وارد
Docker Image نمیشه، طبق `.dockerignore`) خونده و به Container تزریق میشه.

### ۷. Incremental Sync
`BaseSyncService.get_last_successful_sync_time()` زمان شروع آخرین اجرای
موفق همون `operation_type` رو از جدول `sync_runs` پیدا می‌کنه. Serviceهای
فرزند این زمان رو به‌عنوان `since` به `OdooClient` پاس میدن، که فیلتر
`write_date >= since` رو به کوئری Odoo اضافه می‌کنه. یعنی از دومین اجرا به
بعد، فقط رکوردهایی که واقعاً تغییر کردن خونده میشن، نه کل جدول.

### ۸. Graceful Shutdown
وقتی `docker stop` یا Ctrl+C بزنی، سیگنال SIGTERM/SIGINT میاد. تو `main.py`
این سیگنال به `KeyboardInterrupt` تبدیل میشه. `BaseSyncService.run()` این
Exception رو جدا از خطاهای معمولی مدیریت می‌کنه: رکورد فعلی رو نیمه‌کاره
رها نمی‌کنه (به لطف SAVEPOINT، رکوردهای قبلی که موفق بودن سالم می‌مونن)،
وضعیت رو با `status="cancelled"` تو `sync_runs` ثبت می‌کنه، و بعد خارج
میشه — بدون قفل‌شدن یا خرابی داده.

## محدودیت‌های شناخته‌شده

- **Sync یک‌طرفه است**: فقط Odoo → PostgreSQL. تغییرات دستی مستقیم تو
  PostgreSQL به Odoo برنمی‌گرده (خارج از Scope این پروژه بود).
- **Delete پشتیبانی نمیشه**: اگه رکوردی تو Odoo حذف بشه، این Sync خودش
  رو تو PostgreSQL حذف نمی‌کنه (فقط Create/Update). اضافه‌کردنش امکان‌پذیره
  ولی نیاز به یک استراتژی جدا داره (مثلاً soft-delete بر اساس مقایسه‌ی
  لیست کامل odoo_idها).
- **ساخت دیتابیس Odoo دستیه**: طبق سناریوی آزمون، این کار (ساخت دیتابیس از
  طریق مرورگر، چون Odoo از قبل هیچ دیتابیسی نداره) یک قدم دستیه که با
  `docker compose up` به‌تنهایی خودکار نمیشه. به همین دلیل سرویس `app` تو
  Docker پیش‌فرض فقط Migration رو اجرا می‌کنه، نه Sync کامل رو (جزئیات تو
  User Documentation).
- **Concurrency**: اگه دو نمونه از این برنامه هم‌زمان اجرا بشن، ممکنه با
  race condition رو‌به‌رو بشیم (چون بین `get_by_odoo_id` و `insert` قفلی
  نیست). برای این پروژه (اجرای دستی/زمان‌بندی‌شده‌ی تکی) مشکلی ایجاد نمی‌کنه.
- **تست‌ها فقط Unit Test هستن**: به دلیل محدودیت زمانی، Integration Test
  رسمی (که مستقیم به یک Odoo/Postgres واقعی وصل بشه و end-to-end تست کنه)
  نوشته نشده؛ اسکریپت‌های `scripts/test_*.py` این نقش رو به‌صورت دستی ایفا
  می‌کنن.
- **Incremental Sync بر پایه‌ی `write_date`**: اگه یک رکورد بین دو اجرای
  Sync هم ساخته و هم حذف بشه (خیلی به‌ندرت پیش میاد)، ممکنه در حالت
  Incremental دیده نشه. برای Full Sync این مشکل وجود نداره.
