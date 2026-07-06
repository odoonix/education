import pytest
from mappers.contact_mapper import ContactMapper
from mappers.product_mapper import ProductMapper
from mappers.sales_order_mapper import SaleOrderMapper

class TestContactMapper:

    def test_contact_mapper_basics(self):
        
        odoo_data = {
            "id": 123,
            "name": "Test Company",
            "email": "test@example.com",
            "phone": "+1234567890",
            "city": "Tehran",
            "active": True
        }

        internal_data = ContactMapper.to_internal(odoo_data)

        assert internal_data.external_id == 123, "ID should be 123"
        assert internal_data.name == "Test Company", "Name should match"
        assert internal_data.email == "test@example.com", "Email should match"
        assert internal_data.phone == "+1234567890", "Phone should match"
        assert internal_data.city == "Tehran", "City should match"
        assert internal_data.active is True, "Active should be True"

    def test_contact_mapper_missing_fields(self):
        odoo_data = {
            "id": 123,
            "name": "Another company"
        }

        internal_data = ContactMapper.to_internal(odoo_data)

        assert internal_data.external_id == odoo_data["id"], "ids must match"
        assert internal_data.name == odoo_data["name"], "names must match"
        assert internal_data.email is None, "Missing email should be None"
        assert internal_data.phone is None, "Missing phone should be None"
        assert internal_data.city is None, "Missing city should be None"


class TestProductMapper:
    """
    Test the ProductMapper - converts Odoo products to our format.
    """
    
    def test_product_mapper_basic(self):
        """
        TEST: Can we convert a product with all fields?
        """
        # GIVEN - Odoo product data
        odoo_data = {
            "id": 456,
            "name": "Test Product",
            "default_code": "TEST001",
            "list_price": 99.99,
            "type": "product",
            "active": True
        }
        
        # WHEN - Convert
        result = ProductMapper.to_internal(odoo_data)
        
        # THEN - Check
        assert result.external_id == 456, "ID should match"
        assert result.name == "Test Product", "Name should match"
        assert result.internal_reference == "TEST001", "Reference should match"
        assert result.sale_price == 99.99, "Price should match"
        assert result.product_type == "product", "Type should match"
        assert result.active is True, "Active should be True"
    
    def test_product_mapper_missing_reference(self):
        """
        TEST: What happens when product has no internal reference?
        """
        # GIVEN - Odoo product without default_code
        odoo_data = {
            "id": 789,
            "name": "No Reference",
            "list_price": 50.00,
            "type": "service"
            # Notice: no default_code
        }
        
        # WHEN - Convert
        result = ProductMapper.to_internal(odoo_data)
        
        # THEN - Check
        assert result.external_id == 789
        assert result.internal_reference is None, "Missing reference should be None"


class TestSaleOrderMapper:
    """
    Test the SaleOrderMapper - converts Odoo sale orders to our format.
    """
    
    def test_sale_order_mapper_basic(self):
        """
        TEST: Can we convert a sale order with all fields?
        """
        # GIVEN - Odoo sale order data
        odoo_data = {
            "id": 789,
            "name": "S00001",
            "partner_id": [1, "Customer Name"],  # Odoo sends as [id, name]
            "date_order": "2026-01-01",
            "state": "sale",
            "amount_total": 1000.00,
            "amount_paid": 500.00,
            "is_expired": False
        }
        
        # WHEN - Convert
        result = SaleOrderMapper.to_internal(odoo_data)
        
        # THEN - Check
        assert result.external_id == 789
        assert result.order_number == "S00001"
        assert result.customer_id == 1, "Should extract ID from [id, name]"
        assert result.state == "sale"
        assert result.total_amount == 1000.00
        assert result.amount_paid == 500.00
        assert result.is_expired is False
    
    def test_sale_order_mapper_partner_as_int(self):
        """
        TEST: What happens when partner_id is a single number, not a list?
        """
        # GIVEN - Odoo data with partner_id as int
        odoo_data = {
            "id": 101,
            "name": "S00002",
            "partner_id": 2,
            "state": "done",
            "amount_total": 2000.00
        }
        
        # WHEN - Convert
        result = SaleOrderMapper.to_internal(odoo_data)
        
        # THEN - Check
        assert result.customer_id == 2, "Should handle int directly"