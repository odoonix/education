from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    ForeignKey, UniqueConstraint, Index, CheckConstraint, Text, Boolean
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime, timezone

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    inventory_items = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('purchase_price > 0', name='ck_product_purchase_price_positive'),
        CheckConstraint('selling_price > 0', name='ck_product_selling_price_positive'),
        CheckConstraint('selling_price >= purchase_price', name='ck_product_price_logic'),
        Index('idx_product_active', 'is_active'),
    )

class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), unique=True, nullable=False)
    location = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    inventory_items = relationship("Inventory", back_populates="warehouse", cascade="all, delete-orphan")

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    product = relationship("Product", back_populates="inventory_items")
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    
    __table_args__ = (
        UniqueConstraint('product_id', 'warehouse_id', name='uix_product_warehouse'),
        CheckConstraint('quantity >= 0', name='ck_inventory_quantity_non_negative'),
        CheckConstraint('reserved_quantity >= 0', name='ck_inventory_reserved_non_negative'),
        CheckConstraint('reserved_quantity <= quantity', name='ck_inventory_reserved_lte_quantity'),
        Index('idx_inventory_product', 'product_id'),
        Index('idx_inventory_warehouse', 'warehouse_id'),
        Index('idx_inventory_available', 'product_id', 'warehouse_id', 'quantity', 'reserved_quantity'),
    )

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    status = Column(String(20), nullable=False, default="DRAFT", index=True)
    total_amount = Column(Float, default=0)
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")
    warehouse = relationship("Warehouse")
    
    __table_args__ = (
        Index('idx_po_status_date', 'status', 'created_at'),
    )

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='ck_poi_quantity_positive'),
        CheckConstraint('unit_price > 0', name='ck_poi_price_positive'),
    )

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    status = Column(String(20), nullable=False, default="DRAFT", index=True)
    total_amount = Column(Float, default=0)
    backorder_allowed = Column(Boolean, default=False)
    created_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    
    items = relationship("SalesOrderItem", back_populates="order", cascade="all, delete-orphan")
    warehouse = relationship("Warehouse")
    
    __table_args__ = (
        Index('idx_so_status_date', 'status', 'created_at'),
    )

class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    fulfilled_quantity = Column(Integer, default=0)
    
    order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product")
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='ck_soi_quantity_positive'),
        CheckConstraint('unit_price > 0', name='ck_soi_price_positive'),
    )

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False, index=True)
    quantity_change = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    reference_type = Column(String(50))
    reference_id = Column(Integer)
    batch_id = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    notes = Column(Text)
    
    __table_args__ = (
        Index('idx_trans_product_date', 'product_id', 'created_at'),
        Index('idx_trans_warehouse_date', 'warehouse_id', 'created_at'),
        Index('idx_trans_batch', 'batch_id'),
    )