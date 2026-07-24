#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] در حال اجرای migration های Alembic..."
alembic upgrade head
echo "Setting up admin permissions..."

# Wait for Odoo to be ready
sleep 5

python3 << EOF
import xmlrpc.client
import time

url = 'http://odoo:8069'
db = '${ODOO_DATABASE:-odoo}'

# Try to connect
for i in range(30):
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, 'admin', 'admin', {})
        print(uid)
        if uid:
            break
    except:
        pass
    time.sleep(2)

if uid:
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Get admin user
    admin_user = models.execute_kw(db, uid, 'admin', 'res.users', 'search_read',
        [[['login', '=', 'admin']]],
        {'fields': ['id', 'groups_id']}
    )[0]
    
    # Get Sales Administrator group
    sales_group = models.execute_kw(db, uid, 'admin', 'res.groups', 'search',
        [[['name', '=', 'Administrator'], ['category_id.name', '=', 'Sales']]]
    )
    
    if sales_group:
        models.execute_kw(db, uid, 'admin', 'res.users', 'write',
            [[admin_user['id']], {'groups_id': [(4, sales_group[0])]}]
        )
        print('✅ Sales Administrator permission added to admin user!')
    
    # Get Invoicing group
    invoice_group = models.execute_kw(db, uid, 'admin', 'res.groups', 'search',
        [[['name', '=', 'Invoicing'], ['category_id.name', '=', 'Invoicing']]]
    )
    
    if invoice_group:
        models.execute_kw(db, uid, 'admin', 'res.users', 'write',
            [[admin_user['id']], {'groups_id': [(4, invoice_group[0])]}]
        )
        print('✅ Invoicing group added to admin user!')
    
    print('✅ Permissions setup complete!')
else:
    print('❌ Could not connect to Odoo')
EOF
echo "[entrypoint] اجرای برنامه..."
exec python -m app.main
