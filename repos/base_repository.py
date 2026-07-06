
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Dict, Any, List, Optional
from datetime import datetime
from models.orm_models import Base

ModelType = TypeVar("ModelType", bound=Any)

class BaseRepository(Generic[ModelType]):
    """
    Generic repository with common CRUD operations.
    Use this as a base for all entity-specific repositories.
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get_by_external_id(self, external_id: int) -> Optional[ModelType]:
        """Find record by external_id"""
        return self.db.query(self.model).filter(
            self.model.external_id == external_id
        ).first()
    
    def get_all(self, limit: int = None) -> List[ModelType]:
        """Get all records with optional limit"""
        query = self.db.query(self.model)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def save(self, instance: ModelType) -> ModelType:
        """Save a single instance (create or update)"""
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def save_all(self, instances: List[ModelType]) -> List[ModelType]:
        """Save multiple instances efficiently"""
        self.db.add_all(instances)
        self.db.commit()
        for instance in instances:
            self.db.refresh(instance)
        return instances
    
    def delete(self, instance: ModelType) -> None:
        """Delete a record"""
        self.db.delete(instance)
        self.db.commit()
    
    def delete_by_external_id(self, external_id: int) -> bool:
        """Delete record by external_id"""
        instance = self.get_by_external_id(external_id)
        if instance:
            self.delete(instance)
            return True
        return False