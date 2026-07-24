# odoo-sync

این پروژه اطلاعات مخاطبین، محصولات و سفارش‌های فروش را از **Odoo** دریافت می‌کند و داخل **PostgreSQL** ذخیره می‌کند.

فرآیند **Sync** به‌صورت **Idempotent** پیاده‌سازی شده؛ یعنی فرقی نمی‌کند یک بار اجرا شود یا چندین بار، رکورد تکراری ایجاد نمی‌شود و فقط اطلاعات موجود به‌روزرسانی خواهند شد.

## پیش‌نیازها

* Docker Desktop
* Python 3.12 یا بالاتر

## راه‌اندازی

ابتدا **Odoo**، دیتابیس آن و دیتابیس برنامه را اجرا کنید:

```powershell
docker compose up -d odoo-db odoo app-db
```

چند ثانیه صبر کنید تا سرویس‌ها بالا بیایند، سپس وضعیت آن‌ها را بررسی کنید:

```powershell
docker compose ps
```

### فقط برای اولین اجرا

مرورگر را باز کنید و وارد آدرس زیر شوید:

```text
http://localhost:8069
```

اگه لازم بود دیتابیس جدیدی بسازید، از تنظیمات زیر استفاده کنید:

* Database: `exam_db`
* Email: `admin`
* Password: `admin`
* Demo Data: `Skip`

اگر صفحه ورود نمایش داده شد، یعنی دیتابیس از قبل ساخته شده است با نام کاربری و رمز `admin` وارد شوید.

بعد از ورود، ماژول **Sales** را نصب کنید. این پروژه برای دریافت مخاطبین، محصولات و سفارش‌های فروش به این ماژول نیاز دارد.


### ایجاد داده‌های نمونه

```powershell
python scripts\seed_odoo.py
```

این اسکریپت چند مخاطب، محصول و سفارش فروش نمونه ایجاد می‌کند و در صورت اجرای دوباره هم مشکلی ایجاد نمی‌کند.

### ساخت جداول دیتابیس

```powershell
alembic upgrade head
```

## اجرای Sync

```powershell
python -m backend.cli
```

خروجی نمونه:

```text
Sync finished: fetched=99 created=99 updated=0 errors=0
```

اگر دوباره همین دستور را اجرا کنید، مقدار `created` دیگر افزایش پیدا نمی‌کند و به‌جای آن مقدار `updated` بیشتر میشه.

## اجرای پروژه با Docker

```powershell
docker compose up --build
```

این دستور Image برنامه را می‌سازد، منتظر آماده شدن **Odoo** و **PostgreSQL** می‌ماند، Migrationها را اجرا می‌کند و در نهایت فرآیند **Sync** را شروع می‌کند.

## اجرای تست‌ها

```powershell
docker compose up -d test-db
pytest -v
```

برای مشاهده **Coverage**:

```powershell
pytest --cov=backend --cov-report=term-missing
```

