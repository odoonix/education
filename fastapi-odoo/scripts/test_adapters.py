from app.adapters.contact_adapter import ContactAdapter
from app.adapters.odoo_client import OdooClient
from app.adapters.product_adapter import ProductAdapter
from app.adapters.sale_order_adapter import SaleOrderAdapter


client = OdooClient()

contact_adapter = ContactAdapter(client)
product_adapter = ProductAdapter(client)
sale_order_adapter = SaleOrderAdapter(client)


contacts = contact_adapter.fetch_contacts()
products = product_adapter.fetch_products()
orders = sale_order_adapter.fetch_orders()
lines = sale_order_adapter.fetch_order_lines()


print("Contacts:")
for contact in contacts:
    print(contact)


print("\nProducts:")
for product in products:
    print(product)


print("\nOrders:")
for order in orders:
    print(order)


print("\nOrder Lines:")
for line in lines:
    print(line)