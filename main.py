# main.py
import sys
import argparse
from database.session import SessionLocal, engine, Base
from services.sync_service import SyncService
from utils.logger import logger


def main():
    """Main entry point for the sync application"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Sync data from Odoo to PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            # Sync everything with default limits
            python main.py --all
            
            # Sync only contacts
            python main.py --contacts
            
            # Sync with specific limits
            python main.py --all --contacts-limit 50 --products-limit 100 --orders-limit 20
        """
    )
    parser.add_argument('--all', action='store_true',
                       help='Sync all data (contacts, products, orders)')
    parser.add_argument('--contacts', action='store_true',
                       help='Sync only contacts')
    parser.add_argument('--products', action='store_true',
                       help='Sync only products')
    parser.add_argument('--orders', action='store_true',
                       help='Sync only sale orders')
    parser.add_argument('--contacts-limit', type=int, default=None,
                       help='Limit number of contacts to sync')
    parser.add_argument('--products-limit', type=int, default=None,
                       help='Limit number of products to sync')
    parser.add_argument('--orders-limit', type=int, default=None,
                       help='Limit number of sale orders to sync')
    parser.add_argument('--status', action='store_true',
                       help='Show status of last sync run')
    
    args = parser.parse_args()
    
    # Create database tables if they don't exist
    logger.info("Checking database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified")
    
    # Create session
    db = SessionLocal()
    
    try:
        service = SyncService(db)
        
        # Show status if requested
        if args.status:
            status = service.get_sync_status()
            logger.info("Sync Status", **status)
            return
        
        # Determine what to sync
        sync_all = args.all or not (args.contacts or args.products or args.orders)
        
        if sync_all:
            # Sync everything
            logger.info("Starting full sync...")
            sync_run = service.sync_all(
                contact_limit=args.contacts_limit,
                product_limit=args.products_limit,
                order_limit=args.orders_limit
            )
            
            # Log results
            logger.info("✅ Sync completed successfully!", 
                       sync_run_id=sync_run.id,
                       status=sync_run.status,
                       contacts=sync_run.contacts_count,
                       products=sync_run.products_count,
                       orders=sync_run.sale_orders_count,
                       errors=sync_run.error_count)
            
            # Log errors if any
            if sync_run.error_count > 0:
                errors = service.get_errors()
                logger.warning(f"⚠️  {sync_run.error_count} errors occurred during sync")
                for error in errors[:5]:  # Show first 5 errors
                    logger.warning(f"   - {error['entity']} (ID: {error['external_id']}): {error['error']}")
                if len(errors) > 5:
                    logger.warning(f"   ... and {len(errors) - 5} more errors")
        
        elif args.contacts:
            # Sync only contacts
            logger.info("Syncing contacts...")
            count = service.sync_contacts(limit=args.contacts_limit)
            logger.info(f"✅ Synced {count} contacts")
            
        elif args.products:
            # Sync only products
            logger.info("Syncing products...")
            count = service.sync_products(limit=args.products_limit)
            logger.info(f"✅ Synced {count} products")
            
        elif args.orders:
            # Sync only sale orders
            logger.info("Syncing sale orders...")
            count = service.sync_sale_orders(limit=args.orders_limit)
            logger.info(f"✅ Synced {count} sale orders")
        
        logger.info("✅ Everything is ready for full sync!")
        
    except Exception as e:
        logger.error("❌ Sync failed", error=str(e))
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()