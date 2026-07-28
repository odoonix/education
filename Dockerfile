FROM python:3.11-slim

WORKDIR /app

# اول فقط requirements رو کپی می‌کنیم که اگه کد عوض شد ولی وابستگی‌ها نه،
# Docker از cache استفاده کنه و rebuild سریع‌تر بشه.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# پیش‌فرض: Migration رو اجرا کن، بعد کانتینر رو زنده نگه دار (به‌جای اینکه
# بلافاصله بسته بشه). این باعث میشه بشه با «docker compose exec app ...»
# دستورات رو روی یه کانتینر پایدار و از‌قبل‌متصل‌به‌شبکه اجرا کرد، به‌جای
# اینکه هر بار «docker compose run» یه کانتینر تازه بسازه (که رو بعضی
# سیستم‌ها -- مخصوصاً Windows/WSL2 -- چند ثانیه طول می‌کشه تا شبکه‌اش
# کاملاً پایدار بشه و باعث خطای گذرای Connection Refused میشه).
CMD ["sh", "-c", "alembic upgrade head && tail -f /dev/null"]
