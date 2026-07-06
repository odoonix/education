#### check contacts

```command
docker exec -it odoo_sync_db psql -U postgres -d odoo_sync -c "SELECT id, external_id, name, email, phone, city FROM contacts ORDER BY id DESC;"
```

#### check products

```command
docker exec -it odoo_sync_db psql -U postgres -d odoo_sync -c "SELECT id, external_id, name, internal_reference, sale_price, product_type FROM products ORDER BY id DESC;"
```

#### check Sale Orders

```command
docker exec -it odoo_sync_db psql -U postgres -d odoo_sync -c "SELECT id, external_id, order_number, customer_id, state, total_amount FROM sale_orders ORDER BY id DESC;"
```

#### check Sale Order Lines

```command
docker exec -it odoo_sync_db psql -U postgres -d odoo_sync -c "SELECT id, external_id, sale_order_id, product_id, quantity, unit_price, subtotal FROM sale_order_lines ORDER BY id DESC;"
```

#### Check Sync Runs (History)

```command
docker exec -it odoo_sync_db psql -U postgres -d odoo_sync -c "SELECT id, started_at, finished_at, status, contacts_count, products_count, sale_orders_count, error_count FROM sync_runs ORDER BY id DESC;"
```

#### Check all tables

```command
docker exec -it odoo_sync_db psql -U postgres -d odoo_sync -c "\dt"
```