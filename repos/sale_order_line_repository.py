# repos/sale_order_line_repository.py
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.orm_models import SaleOrderLine
from repos.base_repository import BaseRepository

class SaleOrderLineRepository(BaseRepository[SaleOrderLine]):
    def __init__(self, db: Session):
        super().__init__(SaleOrderLine, db)
    
    def upsert(self, line_data: Dict[str, Any]) -> SaleOrderLine:
        """Update existing line or create new one"""
        external_id = line_data.get("external_id")
        if not external_id:
            raise ValueError("external_id is required for upsert")
        
        existing = self.get_by_external_id(external_id)
        
        if existing:
            update_fields = ["sale_order_id", "product_id", "quantity", 
                           "unit_price", "subtotal"]
            for field in update_fields:
                if field in line_data:
                    setattr(existing, field, line_data[field])
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            new_line = SaleOrderLine(**line_data)
            self.db.add(new_line)
            self.db.commit()
            self.db.refresh(new_line)
            return new_line
    
    def upsert_bulk(self, lines_data: List[Dict[str, Any]]) -> List[SaleOrderLine]:
        """Bulk upsert for better performance"""
        results = []
        for line_data in lines_data:
            try:
                result = self.upsert(line_data)
                results.append(result)
            except Exception as e:
                raise
        return results
    
    def get_by_order_id(self, order_external_id: int) -> List[SaleOrderLine]:
        """Get all lines for a specific order"""
        return self.db.query(SaleOrderLine).filter(
            SaleOrderLine.sale_order_id == order_external_id
        ).all()