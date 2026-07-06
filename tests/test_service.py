"""
Testing Services: These tests check if the business logic works.
Service orchestrates Adapter, Mapper, and Repository together.
"""

import pytest
from unittest.mock import Mock, patch
from database.session import SessionLocal
from services.sync_service import SyncService
from repos.contact_repository import ContactRepository
from repos.product_repository import ProductRepository
from repos.sale_order_repository import SaleOrderRepository
from repos.sync_run_repository import SyncRunRepository
from utils.logger import logger


class TestSyncService:
    """
    Test the SyncService - orchestrates the entire sync process.
    """
    
    def test_sync_contacts(self, db_session):
        """
        TEST: Can we sync contacts from Odoo to database?
        
        This test uses a MOCK adapter so we don't need to call real Odoo.
        """
        # GIVEN - Create service with test database session
        service = SyncService(db_session)
        
        # GIVEN - Mock the adapter to return test data instead of calling Odoo
        with patch.object(service.adapter, 'get_contacts') as mock_get:
            mock_get.return_value = [
                {"id": 1, "name": "Contact 1", "email": "test1@example.com"},
                {"id": 2, "name": "Contact 2", "email": "test2@example.com"},
                {"id": 3, "name": "Contact 3", "email": "test3@example.com"}
            ]
            
            # WHEN - Sync contacts
            count = service.sync_contacts(limit=3)
            
            # THEN - Three contacts should be saved
            assert count == 3, "Should have synced 3 contacts"
            assert service.error_count == 0, "No errors should occur"
            
            # THEN - Check contacts were actually saved to database
            repo = ContactRepository(db_session)
            contacts = repo.get_all()
            assert len(contacts) == 3, "Should have 3 contacts in database"
            
            # THEN - Check contact data is correct
            contact_names = [c.name for c in contacts]
            assert "Contact 1" in contact_names
            assert "Contact 2" in contact_names
            assert "Contact 3" in contact_names
    
    def test_sync_contacts_with_errors(self, db_session):
        """
        TEST: What happens when a contact fails to save?
        
        CRITICAL: Service should CONTINUE processing other contacts.
        """
        # GIVEN - Create service
        service = SyncService(db_session)
        
        # GIVEN - Mock data with 3 contacts
        with patch.object(service.adapter, 'get_contacts') as mock_get:
            mock_get.return_value = [
                {"id": 1, "name": "Contact 1"},
                {"id": 2, "name": "Contact 2"},
                {"id": 3, "name": "Contact 3"}
            ]
            
            # GIVEN - Make the repository fail on the second contact
            with patch.object(service.contact_repo, 'upsert') as mock_upsert:
                mock_upsert.side_effect = [
                    None,  # Contact 1 succeeds
                    Exception("Database error!"),  # Contact 2 fails
                    None  # Contact 3 succeeds
                ]
                
                # WHEN - Sync contacts
                count = service.sync_contacts(limit=3)
                
                # THEN - Only 2 contacts succeeded
                assert count == 2, "Should have synced 2 contacts"
                assert service.error_count == 1, "Should have 1 error"
                assert len(service.errors) == 1, "Error should be recorded"
                assert service.errors[0]["external_id"] == 2, "Error should be for contact 2"
                assert "Database error!" in service.errors[0]["error"], "Error message should be stored"
    
    def test_sync_products(self, db_session):
        """Test syncing products from Odoo"""
        # GIVEN - Create service
        service = SyncService(db_session)
        
        # GIVEN - Mock the adapter
        with patch.object(service.adapter, 'get_products') as mock_get:
            mock_get.return_value = [
                {"id": 1, "name": "Product 1", "default_code": "P001", "list_price": 10.99},
                {"id": 2, "name": "Product 2", "default_code": "P002", "list_price": 20.99}
            ]
            
            # WHEN - Sync products
            count = service.sync_products(limit=2)
            
            # THEN - Two products should be saved
            assert count == 2, "Should have synced 2 products"
            assert service.error_count == 0, "No errors should occur"
            
            # THEN - Check products were saved to database
            repo = ProductRepository(db_session)
            products = repo.get_all()
            assert len(products) == 2, "Should have 2 products in database"
            
            # THEN - Check product data
            product_names = [p.name for p in products]
            assert "Product 1" in product_names
            assert "Product 2" in product_names
    
    def test_sync_sale_orders(self, db_session):
        """Test syncing sale orders from Odoo"""
        # GIVEN - Create service
        service = SyncService(db_session)
        
        # GIVEN - First create a customer (contact) for the order to reference
        contact_repo = ContactRepository(db_session)
        contact_repo.upsert({"external_id": 100, "name": "Test Customer"})
        
        # GIVEN - Mock the adapter
        with patch.object(service.adapter, 'get_sale_orders') as mock_get:
            mock_get.return_value = [
                {
                    "id": 1,
                    "name": "S00001",
                    "partner_id": [100, "Test Customer"],
                    "state": "draft",
                    "amount_total": 500.00
                },
                {
                    "id": 2,
                    "name": "S00002",
                    "partner_id": [100, "Test Customer"],
                    "state": "sale",
                    "amount_total": 1000.00
                }
            ]
            
            # WHEN - Sync sale orders
            count = service.sync_sale_orders(limit=2)
            
            # THEN - Two orders should be saved
            assert count == 2, "Should have synced 2 orders"
            assert service.error_count == 0, "No errors should occur"
            
            # THEN - Check orders were saved to database
            repo = SaleOrderRepository(db_session)
            orders = repo.get_all()
            assert len(orders) == 2, "Should have 2 orders in database"
            
            # THEN - Check order data
            order_numbers = [o.order_number for o in orders]
            assert "S00001" in order_numbers
            assert "S00002" in order_numbers
    
    def test_sync_sale_orders_without_customer(self, db_session):
        """
        TEST: What happens when a sale order references a customer that doesn't exist?
        
        This tests foreign key integrity.
        """
        # GIVEN - Create service
        service = SyncService(db_session)
        
        # GIVEN - Mock the adapter with a non-existent customer ID (999)
        with patch.object(service.adapter, 'get_sale_orders') as mock_get:
            mock_get.return_value = [
                {
                    "id": 1,
                    "name": "S00001",
                    "partner_id": [999, "Non-existent Customer"],  # ← Customer doesn't exist
                    "state": "draft",
                    "amount_total": 500.00
                }
            ]
            
            # WHEN - Sync sale orders
            # This should fail because the customer doesn't exist
            # But the service should handle it gracefully
            with patch.object(service.order_repo, 'upsert') as mock_upsert:
                # Mock the upsert to raise an integrity error
                mock_upsert.side_effect = Exception("Foreign key violation: customer not found")
                
                # WHEN - Sync orders
                count = service.sync_sale_orders(limit=1)
                
                # THEN - Order should fail but service continues
                assert count == 0, "Should have synced 0 orders"
                assert service.error_count == 1, "Should have 1 error"
                assert service.errors[0]["external_id"] == 1, "Error should be for order 1"
    
    def test_full_sync(self, db_session):
        """
        TEST: Does full sync work correctly?
        
        This tests the complete orchestration: contacts + products + orders.
        """
        # GIVEN - Create service
        service = SyncService(db_session)
        
        # GIVEN - Mock all adapter methods
        with patch.object(service.adapter, 'get_contacts') as mock_contacts:
            mock_contacts.return_value = [
                {"id": 1, "name": "Contact 1", "email": "c1@test.com"},
                {"id": 2, "name": "Contact 2", "email": "c2@test.com"}
            ]
            
            with patch.object(service.adapter, 'get_products') as mock_products:
                mock_products.return_value = [
                    {"id": 1, "name": "Product 1", "default_code": "P001"},
                    {"id": 2, "name": "Product 2", "default_code": "P002"}
                ]
                
                with patch.object(service.adapter, 'get_sale_orders') as mock_orders:
                    mock_orders.return_value = [
                        {
                            "id": 1,
                            "name": "S00001",
                            "partner_id": [1, "Contact 1"],
                            "state": "draft",
                            "amount_total": 500.00
                        }
                    ]
                    
                    # WHEN - Run full sync
                    sync_run = service.sync_all(
                        contact_limit=2,
                        product_limit=2,
                        order_limit=1
                    )
                    
                    # THEN - Sync run should be completed
                    assert sync_run.status == "completed", "Status should be completed"
                    assert sync_run.contacts_count == 2, "Should have 2 contacts"
                    assert sync_run.products_count == 2, "Should have 2 products"
                    assert sync_run.sale_orders_count == 1, "Should have 1 order"
                    assert sync_run.error_count == 0, "No errors should occur"
                    
                    # THEN - Data should be in database
                    contact_repo = ContactRepository(db_session)
                    contacts = contact_repo.get_all()
                    assert len(contacts) == 2, "Should have 2 contacts in DB"
                    
                    product_repo = ProductRepository(db_session)
                    products = product_repo.get_all()
                    assert len(products) == 2, "Should have 2 products in DB"
                    
                    order_repo = SaleOrderRepository(db_session)
                    orders = order_repo.get_all()
                    assert len(orders) == 1, "Should have 1 order in DB"
    
    def test_sync_run_tracking(self, db_session):
        """
        TEST: Does the service track sync runs properly?
        
        Each sync should create a record in sync_runs table.
        """
        # GIVEN - Create service
        service = SyncService(db_session)
        
        # GIVEN - Mock all sync methods to return fake counts
        with patch.object(service, 'sync_contacts', return_value=5):
            with patch.object(service, 'sync_products', return_value=3):
                with patch.object(service, 'sync_sale_orders', return_value=2):
                    
                    # WHEN - Run full sync
                    sync_run = service.sync_all()
                    
                    # THEN - Sync run record should be created
                    assert sync_run.status == "completed"
                    assert sync_run.contacts_count == 5
                    assert sync_run.products_count == 3
                    assert sync_run.sale_orders_count == 2
                    assert sync_run.error_count == 0
                    
                    # THEN - It should be retrievable
                    repo = SyncRunRepository(db_session)
                    last_run = repo.get_last_run()
                    assert last_run.id == sync_run.id, "Should find the sync run in DB"
    
    def test_sync_run_failure(self, db_session):
        """
        TEST: What happens when sync fails?
        
        Failed sync should be tracked as 'failed' in sync_runs.
        """
        # GIVEN - Create service
        service = SyncService(db_session)
        
        # GIVEN - Mock sync to fail
        with patch.object(service, 'sync_contacts', side_effect=Exception("Odoo API Error")):
            # WHEN - Run full sync (should raise exception)
            with pytest.raises(Exception):
                service.sync_all()
        
        # THEN - Check sync run status
        repo = SyncRunRepository(db_session)
        last_run = repo.get_last_run()
        
        assert last_run is not None, "Should have a sync run record"
        assert last_run.status == "failed", "Status should be failed"
        assert last_run.log_details is not None, "Should have error details"
        assert "Odoo API Error" in last_run.log_details, "Error message should be stored"
    
    def test_get_sync_status(self, db_session):
        """
        TEST: Can we get the status of the last sync run?
        """
        # GIVEN - Create service and run a sync
        service = SyncService(db_session)
        
        with patch.object(service, 'sync_contacts', return_value=5):
            with patch.object(service, 'sync_products', return_value=3):
                with patch.object(service, 'sync_sale_orders', return_value=2):
                    service.sync_all()
        
        # WHEN - Get status
        status = service.get_sync_status()
        
        # THEN - Status should be correct
        assert status["status"] == "completed"
        assert status["contacts_count"] == 5
        assert status["products_count"] == 3
        assert status["sale_orders_count"] == 2
        assert status["error_count"] == 0
    
    def test_get_errors(self, db_session):
        """
        TEST: Can we retrieve errors from the last sync?
        """
        # GIVEN - Create service
        service = SyncService(db_session)
        
        # GIVEN - Create some errors
        service.error_count = 2
        service.errors = [
            {"entity": "contact", "external_id": 1, "error": "Invalid email"},
            {"entity": "product", "external_id": 2, "error": "Duplicate reference"}
        ]
        
        # WHEN - Get errors
        errors = service.get_errors()
        
        # THEN - Should return the errors
        assert len(errors) == 2
        assert errors[0]["entity"] == "contact"
        assert errors[1]["entity"] == "product"