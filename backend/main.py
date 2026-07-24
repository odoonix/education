import os
import time

print("Backend service started.", flush=True)
print("ODOO_URL =", os.getenv("ODOO_URL"), flush=True)
print("DATABASE_URL =", os.getenv("DATABASE_URL"), flush=True)

while True:
    print("heartbeat...", flush=True)
    time.sleep(30)