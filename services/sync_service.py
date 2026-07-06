
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from adapters.odoo_adapters import OdooAdapter
from mappers.contact_mapper import ContactMapper
from mappers.product_mapper import ProductMapper
from mappers.sales_order_mapper import SaleOrderMapper
from repos.contact_repository import ContactRepository
from repos.product_repository import ProductRepository
from repos.sale_order_repository import SaleOrderRepository
from repos.sync_run_repository import SyncRunRepository
from models.orm_models import SyncRun
from utils.logger import logger


class SyncService:
    """
    Main service for synchronizing data from Odoo to PostgreSQL.
    Orchestrates the entire sync process using Adapter, Mapper, and Repository layers.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.adapter = OdooAdapter()
        
        # Initialize repositories
        self.contact_repo = ContactRepository(db)
        self.product_repo = ProductRepository(db)
        self.order_repo = SaleOrderRepository(db)
        self.sync_run_repo = SyncRunRepository(db)
        
        # Track errors per sync run
        self.error_count = 0
        self.errors: List[Dict[str, Any]] = []
    
    def sync_all(self, contact_limit: Optional[int] = None, 
                 product_limit: Optional[int] = None,
                 order_limit: Optional[int] = None) -> SyncRun:
        """
        Sync all data: contacts, products, and sale orders.
        This is the main entry point for full sync.
        """
        logger.info("Starting full sync", 
                   contact_limit=contact_limit,
                   product_limit=product_limit,
                   order_limit=order_limit)
        
        # Create sync run record
        sync_run = self.sync_run_repo.create_run()
        
        try:
            # Sync each entity type
            contacts_count = self.sync_contacts(limit=contact_limit)
            products_count = self.sync_products(limit=product_limit)
            orders_count = self.sync_sale_orders(limit=order_limit)
            
            # Mark sync as completed
            self.sync_run_repo.complete_run(
                sync_run,
                contacts_count=contacts_count,
                products_count=products_count,
                sale_orders_count=orders_count,
                error_count=self.error_count
            )
            
            logger.info("Full sync completed successfully",
                       contacts=contacts_count,
                       products=products_count,
                       orders=orders_count,
                       errors=self.error_count)
            
            return sync_run
            
        except Exception as e:
            logger.error("Full sync failed", error=str(e))
            self.sync_run_repo.fail_run(sync_run, str(e))
            raise
    
    def sync_contacts(self, limit: Optional[int] = None) -> int:
        """
        Sync contacts from Odoo to PostgreSQL.
        Continues processing even if individual records fail.
        """
        logger.info("Starting contact sync", limit=limit)
        
        try:
            # 1. Fetch from Odoo
            odoo_contacts = self.adapter.get_contacts(limit=limit)
            logger.info(f"Fetched {len(odoo_contacts)} contacts from Odoo")
            
            # 2. Map and save each contact
            saved_count = 0
            for odoo_contact in odoo_contacts:
                try:
                    # Map to internal format
                    contact = ContactMapper.to_internal(odoo_contact)
                    # Convert to dict for repository
                    contact_dict = self._to_dict(contact)
                    # Save using repository (handles duplicates)
                    self.contact_repo.upsert(contact_dict)
                    saved_count += 1
                except Exception as e:
                    self.error_count += 1
                    self.errors.append({
                        "entity": "contact",
                        "external_id": odoo_contact.get("id"),
                        "error": str(e)
                    })
                    logger.error("Failed to sync contact",
                               external_id=odoo_contact.get("id"),
                               error=str(e))
                    continue  # Continue with next contact
            
            logger.info(f"Successfully synced {saved_count} contacts",
                       total=len(odoo_contacts),
                       errors=self.error_count)
            return saved_count
            
        except Exception as e:
            logger.error("Contact sync failed", error=str(e))
            raise
    
    def sync_products(self, limit: Optional[int] = None) -> int:
        """
        Sync products from Odoo to PostgreSQL.
        Continues processing even if individual records fail.
        """
        logger.info("Starting product sync", limit=limit)
        
        try:
            # 1. Fetch from Odoo
            odoo_products = self.adapter.get_products(limit=limit)
            logger.info(f"Fetched {len(odoo_products)} products from Odoo")
            
            # 2. Map and save each product
            saved_count = 0
            for odoo_product in odoo_products:
                try:
                    # Map to internal format
                    product = ProductMapper.to_internal(odoo_product)
                    # Convert to dict for repository
                    product_dict = self._to_dict(product)
                    # Save using repository (handles duplicates)
                    self.product_repo.upsert(product_dict)
                    saved_count += 1
                except Exception as e:
                    self.error_count += 1
                    self.errors.append({
                        "entity": "product",
                        "external_id": odoo_product.get("id"),
                        "error": str(e)
                    })
                    logger.error("Failed to sync product",
                               external_id=odoo_product.get("id"),
                               error=str(e))
                    continue
            
            logger.info(f"Successfully synced {saved_count} products",
                       total=len(odoo_products),
                       errors=self.error_count)
            return saved_count
            
        except Exception as e:
            logger.error("Product sync failed", error=str(e))
            raise
    
    def sync_sale_orders(self, limit: Optional[int] = None) -> int:
        """
        Sync sale orders from Odoo to PostgreSQL.
        Continues processing even if individual records fail.
        """
        logger.info("Starting sale order sync", limit=limit)
        
        try:
            # 1. Fetch from Odoo
            odoo_orders = self.adapter.get_sale_orders(limit=limit)
            logger.info(f"Fetched {len(odoo_orders)} sale orders from Odoo")
            
            # 2. Map and save each order
            saved_count = 0
            for odoo_order in odoo_orders:
                try:
                    # Map to internal format
                    order = SaleOrderMapper.to_internal(odoo_order)
                    # Convert to dict for repository
                    order_dict = self._to_dict(order)
                    # Save using repository (handles duplicates)
                    self.order_repo.upsert(order_dict)
                    saved_count += 1
                except Exception as e:
                    self.error_count += 1
                    self.errors.append({
                        "entity": "sale_order",
                        "external_id": odoo_order.get("id"),
                        "error": str(e)
                    })
                    logger.error("Failed to sync sale order",
                               external_id=odoo_order.get("id"),
                               error=str(e))
                    continue
            
            logger.info(f"Successfully synced {saved_count} sale orders",
                       total=len(odoo_orders),
                       errors=self.error_count)
            return saved_count
            
        except Exception as e:
            logger.error("Sale order sync failed", error=str(e))
            raise
    
    def sync_sale_order_lines(self, order_external_id: int,
                              lines_data: List[Dict[str, Any]]) -> int:
        """
        Sync sale order lines for a specific order.
        Can be used to sync lines separately if needed.
        """
        logger.info("Starting sale order lines sync", 
                   order_external_id=order_external_id,
                   count=len(lines_data))
        
        try:
            saved_count = 0
            for line_data in lines_data:
                try:
                    # Ensure order reference
                    line_data["sale_order_id"] = order_external_id
                    # Save using repository
                    self.order_line_repo.upsert(line_data)
                    saved_count += 1
                except Exception as e:
                    self.error_count += 1
                    self.errors.append({
                        "entity": "sale_order_line",
                        "external_id": line_data.get("external_id"),
                        "error": str(e)
                    })
                    logger.error("Failed to sync sale order line",
                               external_id=line_data.get("external_id"),
                               error=str(e))
                    continue
            
            logger.info(f"Successfully synced {saved_count} sale order lines",
                       total=len(lines_data),
                       errors=self.error_count)
            return saved_count
            
        except Exception as e:
            logger.error("Sale order lines sync failed", error=str(e))
            raise
    
    def _to_dict(self, obj) -> Dict[str, Any]:
        """
        Convert SQLAlchemy model instance to dict.
        Excludes internal SQLAlchemy attributes and handles datetime objects.
        """
        if not obj:
            return {}
        
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            # Handle datetime objects
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        
        return result
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get status of the last sync run"""
        last_run = self.sync_run_repo.get_last_run()
        if not last_run:
            return {"status": "no_sync_run_found"}
        
        return {
            "id": last_run.id,
            "status": last_run.status,
            "started_at": last_run.started_at.isoformat() if last_run.started_at else None,
            "finished_at": last_run.finished_at.isoformat() if last_run.finished_at else None,
            "contacts_count": last_run.contacts_count,
            "products_count": last_run.products_count,
            "sale_orders_count": last_run.sale_orders_count,
            "error_count": last_run.error_count,
            "log_details": last_run.log_details
        }
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get errors from the last sync run"""
        return self.errors