# repos/product_repository.py
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.orm_models import Product
from repos.base_repository import BaseRepository

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)
    
    def upsert(self, product_data: Dict[str, Any]) -> Product:
        """Update existing product or create new one"""
        external_id = product_data.get("external_id")
        if not external_id:
            raise ValueError("external_id is required for upsert")
        
        existing = self.get_by_external_id(external_id)
        
        if existing:
            update_fields = ["name", "internal_reference", "sale_price", 
                           "product_type", "active"]
            for field in update_fields:
                if field in product_data:
                    setattr(existing, field, product_data[field])
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            new_product = Product(**product_data)
            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)
            return new_product
    
    def upsert_bulk(self, products_data: List[Dict[str, Any]]) -> List[Product]:
        """Bulk upsert for better performance"""
        results = []
        for product_data in products_data:
            try:
                result = self.upsert(product_data)
                results.append(result)
            except Exception as e:
                raise
        return results
    
    def get_by_reference(self, internal_reference: str) -> Optional[Product]:
        """Find product by internal reference code"""
        return self.db.query(Product).filter(
            Product.internal_reference == internal_reference
        ).first()
    
    def get_active_products(self) -> List[Product]:
        """Get only active products"""
        return self.db.query(Product).filter(Product.active == True).all()