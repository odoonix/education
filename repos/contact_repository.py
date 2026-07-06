
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.orm_models import Contact
from repos.base_repository import BaseRepository

class ContactRepository(BaseRepository[Contact]):
    def __init__(self, db: Session):
        super().__init__(Contact, db)
    
    def upsert(self, contact_data: Dict[str, Any]) -> Contact:
        """
        Update existing contact or create new one.
        This is the main method your service will use.
        """
        external_id = contact_data.get("external_id")
        if not external_id:
            raise ValueError("external_id is required for upsert")
        
        # Check if exists
        existing = self.get_by_external_id(external_id)
        
        if existing:
            # Update existing record
            update_fields = ["name", "email", "phone", "city", "active"]
            for field in update_fields:
                if field in contact_data:
                    setattr(existing, field, contact_data[field])
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new record
            new_contact = Contact(**contact_data)
            self.db.add(new_contact)
            self.db.commit()
            self.db.refresh(new_contact)
            return new_contact
    
    def upsert_bulk(self, contacts_data: List[Dict[str, Any]]) -> List[Contact]:
        """Bulk upsert for better performance with many records"""
        results = []
        for contact_data in contacts_data:
            try:
                result = self.upsert(contact_data)
                results.append(result)
            except Exception as e:
                # Log error but continue with other records
                # The service layer will handle this
                raise
        return results
    
    def get_by_email(self, email: str) -> Optional[Contact]:
        """Additional utility method"""
        return self.db.query(Contact).filter(Contact.email == email).first()
    
    def get_active_contacts(self) -> List[Contact]:
        """Get only active contacts"""
        return self.db.query(Contact).filter(Contact.active == True).all()