import logging
import uuid
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from models import *
from contextlib import contextmanager
from dataclasses import dataclass
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DomainError(Exception):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR", http_status: int = 400):
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(self.message)

class NotFoundError(DomainError):
    def __init__(self, entity: str, id: Any):
        super().__init__(f"{entity} with id {id} not found", "NOT_FOUND", 404)

class ValidationError(DomainError):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)

class InsufficientStockError(DomainError):
    def __init__(self, product_id: int, warehouse_id: int, requested: int, available: int):
        super().__init__(
            f"Insufficient stock: product={product_id}, warehouse={warehouse_id}, "
            f"requested={requested}, available={available}",
            "INSUFFICIENT_STOCK",
            409
        )

@dataclass
class StockReservation:
    product_id: int
    warehouse_id: int
    quantity: int
    reservation_id: str

class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event_type: str, data: Dict):
        pass

class LoggingEventPublisher(EventPublisher):
    def publish(self, event_type: str, data: Dict):
        logger.info(f"Event: {event_type}, Data: {data}")

class InventoryService:
    def __init__(self, db: Session, event_publisher: EventPublisher = None):
        self.db = db
        self.event_publisher = event_publisher or LoggingEventPublisher()
    
    def get_available_quantity(self, product_id: int, warehouse_id: int) -> int:
        inventory = self.db.query(Inventory).filter(
            and_(Inventory.product_id == product_id, Inventory.warehouse_id == warehouse_id)
        ).first()
        if not inventory:
            return 0
        return max(0, inventory.quantity - inventory.reserved_quantity)
    
    def reserve_stock(self, product_id: int, warehouse_id: int, quantity: int) -> StockReservation:
        inventory = self.db.query(Inventory).filter(
            and_(Inventory.product_id == product_id, Inventory.warehouse_id == warehouse_id)
        ).with_for_update().first()
        
        if not inventory:
            raise InsufficientStockError(product_id, warehouse_id, quantity, 0)
        
        available = inventory.quantity - inventory.reserved_quantity
        if available < quantity:
            raise InsufficientStockError(product_id, warehouse_id, quantity, available)
        
        reservation_id = str(uuid.uuid4())
        inventory.reserved_quantity += quantity
        
        self._create_transaction(
            product_id, warehouse_id, -quantity, "RESERVE",
            quantity_before=inventory.quantity,
            quantity_after=inventory.quantity,
            batch_id=reservation_id
        )
        
        self.db.flush()
        
        self.event_publisher.publish("stock_reserved", {
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": quantity,
            "reservation_id": reservation_id
        })
        
        logger.info(f"Stock reserved: product={product_id}, warehouse={warehouse_id}, "
                   f"qty={quantity}, reservation={reservation_id}")
        
        return StockReservation(product_id, warehouse_id, quantity, reservation_id)
    
    def commit_reservation(self, reservation: StockReservation):
        inventory = self.db.query(Inventory).filter(
            and_(
                Inventory.product_id == reservation.product_id,
                Inventory.warehouse_id == reservation.warehouse_id
            )
        ).with_for_update().first()
        
        if not inventory:
            raise DomainError("Inventory record not found")
        
        quantity_before = inventory.quantity
        inventory.quantity -= reservation.quantity
        inventory.reserved_quantity -= reservation.quantity
        
        self._create_transaction(
            reservation.product_id, reservation.warehouse_id,
            -reservation.quantity, "COMMIT",
            quantity_before=quantity_before,
            quantity_after=inventory.quantity,
            batch_id=reservation.reservation_id
        )
        
        self.db.flush()
        
        self.event_publisher.publish("reservation_committed", {
            "reservation_id": reservation.reservation_id,
            "product_id": reservation.product_id,
            "quantity": reservation.quantity
        })
    
    def release_reservation(self, reservation: StockReservation):
        inventory = self.db.query(Inventory).filter(
            and_(
                Inventory.product_id == reservation.product_id,
                Inventory.warehouse_id == reservation.warehouse_id
            )
        ).with_for_update().first()
        
        if inventory:
            inventory.reserved_quantity -= reservation.quantity
            
            self._create_transaction(
                reservation.product_id, reservation.warehouse_id,
                0, "RELEASE",
                quantity_before=inventory.quantity,
                quantity_after=inventory.quantity,
                batch_id=reservation.reservation_id
            )
            
            self.db.flush()
    
    def add_stock(self, product_id: int, warehouse_id: int, quantity: int, 
                  transaction_type: str, reference_type: str = None,
                  reference_id: int = None, batch_id: str = None) -> Inventory:
        inventory = self.db.query(Inventory).filter(
            and_(Inventory.product_id == product_id, Inventory.warehouse_id == warehouse_id)
        ).with_for_update().first()
        
        if not inventory:
            inventory = Inventory(product_id=product_id, warehouse_id=warehouse_id, quantity=0)
            self.db.add(inventory)
            self.db.flush()
            inventory = self.db.query(Inventory).filter(
                and_(Inventory.product_id == product_id, Inventory.warehouse_id == warehouse_id)
            ).with_for_update().first()
        
        quantity_before = inventory.quantity
        inventory.quantity += quantity
        
        self._create_transaction(
            product_id, warehouse_id, quantity, transaction_type,
            quantity_before=quantity_before,
            quantity_after=inventory.quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            batch_id=batch_id
        )
        
        self.db.flush()
        
        self.event_publisher.publish("stock_added", {
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": quantity,
            "type": transaction_type
        })
        
        logger.info(f"Stock added: product={product_id}, warehouse={warehouse_id}, "
                   f"qty={quantity}, type={transaction_type}")
        
        return inventory
    
    def remove_stock(self, product_id: int, warehouse_id: int, quantity: int,
                     transaction_type: str, reference_type: str = None,
                     reference_id: int = None, batch_id: str = None) -> Inventory:
        inventory = self.db.query(Inventory).filter(
            and_(Inventory.product_id == product_id, Inventory.warehouse_id == warehouse_id)
        ).with_for_update().first()
        
        if not inventory or inventory.quantity < quantity:
            available = inventory.quantity if inventory else 0
            raise InsufficientStockError(product_id, warehouse_id, quantity, available)
        
        quantity_before = inventory.quantity
        inventory.quantity -= quantity
        
        self._create_transaction(
            product_id, warehouse_id, -quantity, transaction_type,
            quantity_before=quantity_before,
            quantity_after=inventory.quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            batch_id=batch_id
        )
        
        self.db.flush()
        
        self.event_publisher.publish("stock_removed", {
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": quantity,
            "type": transaction_type
        })
        
        return inventory
    
    def _create_transaction(self, product_id: int, warehouse_id: int, 
                           quantity_change: int, transaction_type: str,
                           quantity_before: int, quantity_after: int,
                           reference_type: str = None, reference_id: int = None,
                           batch_id: str = None) -> InventoryTransaction:
        transaction = InventoryTransaction(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reference_type=reference_type,
            reference_id=reference_id,
            batch_id=batch_id or str(uuid.uuid4())
        )
        self.db.add(transaction)
        return transaction
    
    def get_product_inventory(self, product_id: int) -> List[Dict]:
        items = self.db.query(Inventory).filter(Inventory.product_id == product_id).all()
        return [{
            "warehouse_id": i.warehouse_id,
            "warehouse_name": i.warehouse.name,
            "warehouse_code": i.warehouse.code,
            "quantity": i.quantity,
            "reserved": i.reserved_quantity,
            "available": i.quantity - i.reserved_quantity,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None
        } for i in items]
    
    def get_total_stock(self, product_id: int) -> Dict:
        result = self.db.query(
            func.coalesce(func.sum(Inventory.quantity), 0).label('total'),
            func.coalesce(func.sum(Inventory.reserved_quantity), 0).label('reserved')
        ).filter(Inventory.product_id == product_id).first()
        
        return {
            "total": result.total,
            "reserved": result.reserved,
            "available": result.total - result.reserved
        }

class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, code: str, name: str, purchase_price: float, selling_price: float) -> Product:
        if selling_price < purchase_price:
            raise ValidationError(f"Selling price ({selling_price}) must be >= purchase price ({purchase_price})")
        
        existing = self.db.query(Product).filter(Product.code == code).first()
        if existing:
            raise DomainError(f"Product with code '{code}' already exists", "DUPLICATE_CODE")
        
        product = Product(code=code, name=name, purchase_price=purchase_price, selling_price=selling_price)
        self.db.add(product)
        self.db.flush()
        logger.info(f"Product created: id={product.id}, code={code}")
        return product
    
    def get_by_id(self, product_id: int) -> Product:
        product = self.db.query(Product).filter(and_(Product.id == product_id, Product.is_active == True)).first()
        if not product:
            raise NotFoundError("Product", product_id)
        return product
    
    def list_all(self, search: str = None, active_only: bool = True) -> List[Product]:
        query = self.db.query(Product)
        if active_only:
            query = query.filter(Product.is_active == True)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(Product.name.ilike(search_term), Product.code.ilike(search_term))
            )
        return query.order_by(Product.name).all()
    
    def update(self, product_id: int, **kwargs) -> Product:
        product = self.get_by_id(product_id)
        
        if 'purchase_price' in kwargs and 'selling_price' not in kwargs:
            if kwargs['purchase_price'] > product.selling_price:
                raise ValidationError("Purchase price cannot exceed selling price")
        
        if 'selling_price' in kwargs and 'purchase_price' not in kwargs:
            if kwargs['selling_price'] < product.purchase_price:
                raise ValidationError("Selling price cannot be less than purchase price")
        
        if 'purchase_price' in kwargs and 'selling_price' in kwargs:
            if kwargs['selling_price'] < kwargs['purchase_price']:
                raise ValidationError("Selling price must be >= purchase price")
        
        for key, value in kwargs.items():
            if value is not None and hasattr(product, key):
                setattr(product, key, value)
        
        self.db.flush()
        return product

class PurchaseService:
    def __init__(self, db: Session, inventory_service: InventoryService):
        self.db = db
        self.inventory_service = inventory_service
    
    def create_order(self, warehouse_id: int, items: List[Dict], 
                    created_by: str = None, notes: str = None) -> Dict:
        warehouse = self.db.query(Warehouse).filter(
            and_(Warehouse.id == warehouse_id, Warehouse.is_active == True)
        ).first()
        if not warehouse:
            raise NotFoundError("Warehouse", warehouse_id)
        
        if not items:
            raise ValidationError("Order must have at least one item")
        
        order_number = f"PO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        order = PurchaseOrder(
            order_number=order_number,
            warehouse_id=warehouse_id,
            created_by=created_by,
            notes=notes
        )
        self.db.add(order)
        self.db.flush()
        
        total = 0
        for item in items:
            product = self.db.query(Product).filter(
                and_(Product.id == item["product_id"], Product.is_active == True)
            ).first()
            if not product:
                raise NotFoundError("Product", item["product_id"])
            
            item_total = item["quantity"] * product.purchase_price
            total += item_total
            
            order_item = PurchaseOrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item["quantity"],
                unit_price=product.purchase_price,
                total_price=item_total
            )
            self.db.add(order_item)
        
        order.total_amount = total
        self.db.flush()
        logger.info(f"Purchase order created: {order_number}, total={total}")
        return self._to_dict(order)
    
    def confirm_order(self, order_id: int) -> Dict:
        order = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not order:
            raise NotFoundError("PurchaseOrder", order_id)
        if order.status != "DRAFT":
            raise DomainError("Only DRAFT orders can be confirmed", "INVALID_STATUS")
        
        batch_id = str(uuid.uuid4())
        
        for item in order.items:
            self.inventory_service.add_stock(
                product_id=item.product_id,
                warehouse_id=order.warehouse_id,
                quantity=item.quantity,
                transaction_type="PURCHASE_RECEIVE",
                reference_type="PURCHASE_ORDER",
                reference_id=order.id,
                batch_id=batch_id
            )
        
        order.status = "CONFIRMED"
        order.confirmed_at = datetime.now(timezone.utc)
        self.db.flush()
        logger.info(f"Purchase order confirmed: {order.order_number}")
        return self._to_dict(order)
    
    def return_order(self, order_id: int) -> Dict:
        order = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not order:
            raise NotFoundError("PurchaseOrder", order_id)
        if order.status != "CONFIRMED":
            raise DomainError("Only CONFIRMED orders can be returned", "INVALID_STATUS")
        
        batch_id = str(uuid.uuid4())
        
        for item in order.items:
            self.inventory_service.remove_stock(
                product_id=item.product_id,
                warehouse_id=order.warehouse_id,
                quantity=item.quantity,
                transaction_type="PURCHASE_RETURN",
                reference_type="PURCHASE_ORDER",
                reference_id=order.id,
                batch_id=batch_id
            )
        
        order.status = "CANCELLED"
        order.cancelled_at = datetime.now(timezone.utc)
        self.db.flush()
        logger.info(f"Purchase order returned: {order.order_number}")
        return self._to_dict(order)
    
    def _to_dict(self, order: PurchaseOrder) -> Dict:
        return {
            "id": order.id,
            "order_number": order.order_number,
            "warehouse_id": order.warehouse_id,
            "warehouse_name": order.warehouse.name,
            "status": order.status,
            "total_amount": order.total_amount,
            "created_by": order.created_by,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "confirmed_at": order.confirmed_at.isoformat() if order.confirmed_at else None,
            "notes": order.notes,
            "items": [{
                "product_id": i.product_id,
                "product_code": i.product.code,
                "product_name": i.product.name,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
                "total_price": i.total_price
            } for i in order.items]
        }

class SalesService:
    def __init__(self, db: Session, inventory_service: InventoryService, 
                 auto_purchase_enabled: bool = False):
        self.db = db
        self.inventory_service = inventory_service
        self.auto_purchase_enabled = auto_purchase_enabled
    
    def create_order(self, warehouse_id: int, items: List[Dict],
                    allow_backorder: bool = False, created_by: str = None,
                    notes: str = None) -> Dict:
        warehouse = self.db.query(Warehouse).filter(
            and_(Warehouse.id == warehouse_id, Warehouse.is_active == True)
        ).first()
        if not warehouse:
            raise NotFoundError("Warehouse", warehouse_id)
        
        if not items:
            raise ValidationError("Order must have at least one item")
        
        can_fulfill = True
        for item in items:
            product = self.db.query(Product).filter(
                and_(Product.id == item["product_id"], Product.is_active == True)
            ).first()
            if not product:
                raise NotFoundError("Product", item["product_id"])
            
            available = self.inventory_service.get_available_quantity(
                item["product_id"], warehouse_id
            )
            if available < item["quantity"]:
                can_fulfill = False
                break
        
        if not can_fulfill and not allow_backorder:
            raise InsufficientStockError(
                item["product_id"], warehouse_id, item["quantity"], available
            )
        
        order_number = f"SO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        status = "DRAFT" if can_fulfill else "BACKORDER"
        
        order = SalesOrder(
            order_number=order_number,
          