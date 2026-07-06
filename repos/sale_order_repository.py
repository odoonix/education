# repos/sale_order_repository.py
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.orm_models import SaleOrder, SaleOrderLine
from repos.base_repository import BaseRepository

class SaleOrderRepository(BaseRepository[SaleOrder]):
    def __init__(self, db: Session):
        super().__init__(SaleOrder, db)
    
    def upsert(self, order_data: Dict[str, Any]) -> SaleOrder:
        """Update existing sale order or create new one"""
        external_id = order_data.get("external_id")
        if not external_id:
            raise ValueError("external_id is required for upsert")
        
        existing = self.get_by_external_id(external_id)
        
        if existing:
            update_fields = ["order_number", "customer_id", "order_date", 
                           "state", "total_amount", "amount_paid", "is_expired"]
            for field in update_fields:
                if field in order_data:
                    setattr(existing, field, order_data[field])
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            new_order = SaleOrder(**order_data)
            self.db.add(new_order)
            self.db.commit()
            self.db.refresh(new_order)
            return new_order
    
    def upsert_with_lines(self, order_data: Dict[str, Any], 
                          lines_data: List[Dict[str, Any]]) -> SaleOrder:
        """
        Save order with its lines in one transaction.
        This ensures data consistency.
        """
        # Save the order first
        order = self.upsert(order_data)
        
        # Handle lines if they exist
        if lines_data:
            # Delete existing lines if updating an existing order
            self.db.query(SaleOrderLine).filter(
                SaleOrderLine.sale_order_id == order.external_id
            ).delete()
            
            # Create new lines
            for line in lines_data:
                line["sale_order_id"] = order.external_id
                new_line = SaleOrderLine(**line)
                self.db.add(new_line)
            
            self.db.commit()
        
        return order
    
    def get_by_order_number(self, order_number: str) -> Optional[SaleOrder]:
        """Find order by its number"""
        return self.db.query(SaleOrder).filter(
            SaleOrder.order_number == order_number
        ).first()
    
    def get_orders_by_state(self, state: str) -> List[SaleOrder]:
        """Get orders by state (e.g., 'sale', 'done', 'cancel')"""
        return self.db.query(SaleOrder).filter(
            SaleOrder.state == state
        ).all()