import pytest
from repos.contact_repository import ContactRepository
from repos.product_repository import ProductRepository
from repos.sale_order_repository import SaleOrderRepository
from repos.sync_run_repository import SyncRunRepository

class TestContactRepository:

    def test_create_new_contact(self, db_session):
        """
        TEST: Can we create a new contact in the database?
        """
        contact_repo = ContactRepository(db_session)
        
        internal_odoo_dict = {
            "external_id": 999,
            "name": "Test Contact",
            "email": "test@example.com",
            "active": True
        }

        # returns either a new contact or an updated one
        result = contact_repo.upsert(internal_odoo_dict)

        # THEN - Contact was created
        assert result.id is not None, "Should have an auto-generated ID"
        assert result.external_id == 999, "External ID should match"
        assert result.name == "Test Contact", "Name should match"
        assert result.email == "test@example.com", "Email should match"


    def test_update_existing_contact(self, db_session):
        """
        TEST: Can we update an existing contact without creating duplicates?
        
        This is the KEY test for preventing duplicates
        """
        # GIVEN - Create repository
        repo = ContactRepository(db_session)
        
        # GIVEN - First, create a contact
        initial_data = {
            "external_id": 888,
            "name": "Original Name",
            "email": "original@example.com"
        }
        created = repo.upsert(initial_data)
        
        # WHEN - Update the same contact with new data
        updated_data = {
            "external_id": 888,  # Same external_id
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        updated = repo.upsert(updated_data)
        
        # THEN - It should be the same record, but with updated fields
        assert updated.id == created.id, "Should be the same record"
        assert updated.name == "Updated Name", "Name should be updated"
        assert updated.email == "updated@example.com", "Email should be updated"
        
        # THEN - There should still be only ONE contact with this external_id
        all_contacts = repo.get_all()
        same_id_contacts = [c for c in all_contacts if c.external_id == 888]
        assert len(same_id_contacts) == 1, "No duplicates should exist"


    def test_find_contact_by_external_id(self, db_session):
        """
        TEST: Can we find a contact by its Odoo ID?
        """
        # GIVEN - Create a contact
        repo = ContactRepository(db_session)
        repo.upsert({"external_id": 777, "name": "Find Me"})
        
        # WHEN - Search for it
        result = repo.get_by_external_id(777)
        
        # THEN - We find it
        assert result is not None, "Contact should be found"
        assert result.name == "Find Me", "Name should match"
    
    def test_get_all_contacts(self, db_session):
        """
        TEST: Can we get all contacts?
        """
        # GIVEN - Create multiple contacts
        repo = ContactRepository(db_session)
        repo.upsert({"external_id": 111, "name": "Contact 1"})
        repo.upsert({"external_id": 222, "name": "Contact 2"})
        repo.upsert({"external_id": 333, "name": "Contact 3"})
        
        # WHEN - Get all
        results = repo.get_all()
        
        # THEN - We get all 3
        assert len(results) == 3, "Should have 3 contacts"
        names = [c.name for c in results]
        assert "Contact 1" in names
        assert "Contact 2" in names
        assert "Contact 3" in names
    
    def test_delete_contact(self, db_session):
        """
        TEST: Can we delete a contact?
        """
        # GIVEN - Create a contact
        repo = ContactRepository(db_session)
        repo.upsert({"external_id": 666, "name": "Delete Me"})
        
        # WHEN - Delete it
        deleted = repo.delete_by_external_id(666)
        
        # THEN - It should be gone
        assert deleted is True, "Delete should succeed"
        result = repo.get_by_external_id(666)
        assert result is None, "Contact should no longer exist"
    
    def test_delete_nonexistent_contact(self, db_session):
        """
        TEST: What happens when we try to delete a contact that doesn't exist?
        """
        # GIVEN - Repository with no contacts
        repo = ContactRepository(db_session)
        
        # WHEN - Try to delete a contact that doesn't exist
        deleted = repo.delete_by_external_id(99999)
        
        # THEN - Should return False (not crash)
        assert deleted is False, "Deleting nonexistent contact should return False"


class TestProductRepository:
    """
    Test ProductRepository - database operations for products.
    """
    
    def test_create_product(self, db_session):
        """Test creating a product"""
        repo = ProductRepository(db_session)
        product_data = {
            "external_id": 555,
            "name": "Test Product",
            "internal_reference": "TEST001",
            "sale_price": 49.99
        }
        
        result = repo.upsert(product_data)
        
        assert result.id is not None, "Should have an ID"
        assert result.external_id == 555, "External ID should match"
        assert result.name == "Test Product", "Name should match"
        assert result.internal_reference == "TEST001", "Reference should match"
        assert result.sale_price == 49.99, "Price should match"
    
    def test_update_existing_product(self, db_session):
        """Test updating an existing product"""
        repo = ProductRepository(db_session)
        
        # Create initial
        initial_data = {
            "external_id": 444,
            "name": "Original Product",
            "sale_price": 100.00
        }
        created = repo.upsert(initial_data)
        
        # Update
        updated_data = {
            "external_id": 444,
            "name": "Updated Product",
            "sale_price": 200.00
        }
        updated = repo.upsert(updated_data)
        
        # THEN - Same record, updated fields
        assert updated.id == created.id, "Should be the same record"
        assert updated.name == "Updated Product", "Name should be updated"
        assert updated.sale_price == 200.00, "Price should be updated"
        
        # THEN - No duplicates
        all_products = repo.get_all()
        same_id_products = [p for p in all_products if p.external_id == 444]
        assert len(same_id_products) == 1, "No duplicates should exist"
    
    def test_find_product_by_reference(self, db_session):
        """Test finding a product by its internal reference"""
        repo = ProductRepository(db_session)
        product_data = {
            "external_id": 333,
            "name": "Reference Test",
            "internal_reference": "REF001"
        }
        repo.upsert(product_data)
        
        result = repo.get_by_reference("REF001")
        
        assert result is not None, "Product should be found"
        assert result.name == "Reference Test", "Name should match"
    
    def test_find_product_by_reference_not_found(self, db_session):
        """Test finding a product with a reference that doesn't exist"""
        repo = ProductRepository(db_session)
        
        result = repo.get_by_reference("NONEXISTENT")
        
        assert result is None, "Should return None when not found"
    
    def test_get_active_products(self, db_session):
        """Test getting only active products"""
        repo = ProductRepository(db_session)
        
        # Create active and inactive products
        repo.upsert({"external_id": 111, "name": "Active Product", "active": True})
        repo.upsert({"external_id": 222, "name": "Inactive Product", "active": False})
        repo.upsert({"external_id": 333, "name": "Another Active", "active": True})
        
        # WHEN - Get active products
        results = repo.get_active_products()
        
        # THEN - Only active products
        assert len(results) == 2, "Should have 2 active products"
        names = [p.name for p in results]
        assert "Active Product" in names
        assert "Another Active" in names
        assert "Inactive Product" not in names


class TestSaleOrderRepository:
    """
    Test SaleOrderRepository - database operations for sale orders.
    """
    
    def test_create_sale_order(self, db_session):
        """Test creating a sale order"""
        # First create a customer (contact)
        contact_repo = ContactRepository(db_session)
        contact_repo.upsert({"external_id": 111, "name": "Customer"})
        
        # Now create the order
        order_repo = SaleOrderRepository(db_session)
        order_data = {
            "external_id": 222,
            "order_number": "TEST001",
            "customer_id": 111,
            "state": "draft",
            "total_amount": 500.00
        }
        
        result = order_repo.upsert(order_data)
        
        assert result.id is not None, "Should have an ID"
        assert result.external_id == 222, "External ID should match"
        assert result.order_number == "TEST001", "Order number should match"
        assert result.customer_id == 111, "Customer ID should match"
        assert result.state == "draft", "State should match"
    
    def test_update_existing_order(self, db_session):
        """Test updating an existing sale order"""
        # Create customer
        contact_repo = ContactRepository(db_session)
        contact_repo.upsert({"external_id": 111, "name": "Customer"})
        
        # Create order
        order_repo = SaleOrderRepository(db_session)
        initial_data = {
            "external_id": 222,
            "order_number": "TEST001",
            "customer_id": 111,
            "state": "draft",
            "total_amount": 500.00
        }
        created = order_repo.upsert(initial_data)
        
        # Update order
        updated_data = {
            "external_id": 222,
            "order_number": "TEST001",
            "customer_id": 111,
            "state": "sale",  # Changed
            "total_amount": 600.00  # Changed
        }
        updated = order_repo.upsert(updated_data)
        
        # THEN - Same record, updated fields
        assert updated.id == created.id, "Should be the same record"
        assert updated.state == "sale", "State should be updated"
        assert updated.total_amount == 600.00, "Amount should be updated"
    
    def test_find_order_by_number(self, db_session):
        """Test finding an order by its order number"""
        # Create customer
        contact_repo = ContactRepository(db_session)
        contact_repo.upsert({"external_id": 111, "name": "Customer"})
        
        # Create order
        order_repo = SaleOrderRepository(db_session)
        order_data = {
            "external_id": 333,
            "order_number": "S00099",
            "customer_id": 111,
            "state": "draft",
            "total_amount": 100.00
        }
        order_repo.upsert(order_data)
        
        # Find by order number
        result = order_repo.get_by_order_number("S00099")
        
        assert result is not None, "Order should be found"
        assert result.external_id == 333, "External ID should match"
    
    def test_get_orders_by_state(self, db_session):
        """Test getting orders by their state"""
        # Create customer
        contact_repo = ContactRepository(db_session)
        contact_repo.upsert({"external_id": 111, "name": "Customer"})
        
        # Create orders with different states
        order_repo = SaleOrderRepository(db_session)
        order_repo.upsert({"external_id": 1, "order_number": "S001", "customer_id": 111, "state": "draft"})
        order_repo.upsert({"external_id": 2, "order_number": "S002", "customer_id": 111, "state": "sale"})
        order_repo.upsert({"external_id": 3, "order_number": "S003", "customer_id": 111, "state": "draft"})
        order_repo.upsert({"external_id": 4, "order_number": "S004", "customer_id": 111, "state": "cancel"})
        
        # WHEN - Get draft orders
        results = order_repo.get_orders_by_state("draft")
        
        # THEN - Only draft orders
        assert len(results) == 2, "Should have 2 draft orders"
        order_numbers = [o.order_number for o in results]
        assert "S001" in order_numbers
        assert "S003" in order_numbers
        assert "S002" not in order_numbers
        assert "S004" not in order_numbers


class TestSyncRunRepository:
    """
    Test SyncRunRepository - tracking sync runs.
    """
    
    def test_create_sync_run(self, db_session):
        """Test creating a sync run"""
        repo = SyncRunRepository(db_session)
        
        # WHEN - Create a sync run
        result = repo.create_run()
        
        # THEN - It should be created
        assert result.id is not None, "Should have an ID"
        assert result.status == "running", "Default status should be 'running'"
        assert result.started_at is not None, "Started at should be set"
        assert result.finished_at is None, "Finished at should be None initially"
    
    def test_complete_sync_run(self, db_session):
        """Test completing a sync run"""
        repo = SyncRunRepository(db_session)
        
        # GIVEN - Create a sync run
        sync_run = repo.create_run()
        
        # WHEN - Complete it
        result = repo.complete_run(
            sync_run,
            contacts_count=5,
            products_count=3,
            sale_orders_count=2,
            error_count=0
        )
        
        # THEN - It should be completed
        assert result.status == "completed", "Status should be 'completed'"
        assert result.finished_at is not None, "Finished at should be set"
        assert result.contacts_count == 5, "Contacts count should match"
        assert result.products_count == 3, "Products count should match"
        assert result.sale_orders_count == 2, "Orders count should match"
        assert result.error_count == 0, "Error count should match"
    
    def test_fail_sync_run(self, db_session):
        """Test failing a sync run"""
        repo = SyncRunRepository(db_session)
        
        # GIVEN - Create a sync run
        sync_run = repo.create_run()
        
        # WHEN - Fail it
        result = repo.fail_run(sync_run, "Connection to Odoo failed")
        
        # THEN - It should be failed
        assert result.status == "failed", "Status should be 'failed'"
        assert result.finished_at is not None, "Finished at should be set"
        assert result.log_details == "Connection to Odoo failed", "Error message should be stored"
    
    def test_get_last_run(self, db_session):
        """Test getting the most recent sync run"""
        repo = SyncRunRepository(db_session)
        
        # GIVEN - Create multiple sync runs
        run1 = repo.create_run()
        repo.complete_run(run1, contacts_count=10)
        
        run2 = repo.create_run()
        repo.complete_run(run2, contacts_count=20)
        
        # WHEN - Get last run
        result = repo.get_last_run()
        
        # THEN - Should be the most recent
        assert result.id == run2.id, "Should return the most recent run"
        assert result.contacts_count == 20, "Should have the most recent counts"
    
    def test_get_runs_by_status(self, db_session):
        """Test getting sync runs by status"""
        repo = SyncRunRepository(db_session)
        
        # GIVEN - Create runs with different statuses
        run1 = repo.create_run()
        repo.complete_run(run1, contacts_count=10)
        
        run2 = repo.create_run()
        repo.fail_run(run2, "Error")
        
        run3 = repo.create_run()
        repo.complete_run(run3, contacts_count=20)
        
        # WHEN - Get completed runs
        results = repo.get_runs_by_status("completed")
        
        # THEN - Only completed runs
        assert len(results) == 2, "Should have 2 completed runs"
        statuses = [r.status for r in results]
        assert "completed" in statuses
        assert "failed" not in statuses