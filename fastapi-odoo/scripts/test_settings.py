from app.config.settings import get_settings

settings = get_settings()

print(settings.app_name)
print(settings.odoo_url)
print(settings.odoo_db)