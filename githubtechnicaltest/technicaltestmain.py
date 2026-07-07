import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Query, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from contextlib import contextmanager
import uvicorn

from models import Base, Warehouse, Product
from services import (
    ProductService, PurchaseService, SalesService,
    InventoryService, DomainError, NotFoundError, 
    ValidationError, LoggingEventPublisher
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "inventory_db")
AUTO_PURCHASE = os.getenv("AUTO_PURCHASE_ENABLED", "false").lower() == "true"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Enterprise Inventory Management System",
    description="High-performance inventory management with advanced stock reservation",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_inventory_service(db: Session = Depends(get_db)):
    return InventoryService(db, LoggingEventPublisher())

class ProductCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, regex="^[A-Z0-9-]+$")
    name: str = Field(..., min_length=1, max_length=200)
    purchase_price: float = Field(..., gt=0, le=999999999.99)
    selling_price: float = Field(..., gt=0, le=999999999.99)
    
    @validator('selling_price')
    def validate_prices(cls, v, values):
        if 'purchase_price' in values and v < values['purchase_price']:
            raise ValueError(f'Selling price ({v}) must be >= purchase price ({values["purchase_price"]})')
        return v

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    purchase_price: Optional[float] = Field(None, gt=0, le=999999999.99)
    selling_price: Optional[float] = Field(None, gt=0, le=999999999.99)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=999999)

class PurchaseOrderCreate(BaseModel):
    warehouse_id: int = Field(..., gt=0)
    items: List[OrderItem] = Field(..., min_items=1, max_items=100)
    notes: Optional[str] = Field(None, max_length=500)

class SalesOrderCreate(BaseModel):
    warehouse_id: int = Field(..., gt=0)
    items: List[OrderItem] = Field(..., min_items=1, max_items=100)
    allow_backorder: bool = False
    notes: Optional[str] = Field(None, max_length=500)

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": exc.code,
            "message": exc.message,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }
    )

@app.get("/")
def root():
    return {
        "system": "Enterprise Inventory Management System",
        "version": "3.0.0",
        "database": "PostgreSQL with advanced locking",
        "features": {
            "auto_purchase": "ENABLED" if AUTO_PURCHASE else "DISABLED",
            "stock_reservation": True,
            "pessimistic_locking": True,
            "event_sourcing": True
        },
        "documentation": "/docs"
    }

@app.get("/health")
def health_check():
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})

@app.get("/init-demo")
def init_demo():
    with get_db() as db:
        try:
            if db.query(Warehouse).count() == 0:
                db.add_all([
                    Warehouse(code="WH-A", name="Warehouse A", location="Tehran"),
                    Warehouse(code="WH-B", name="Warehouse B", location="Isfahan"),
                    Warehouse(code="WH-C", name="Warehouse C", location="Shiraz")
                ])
                db.flush()
            
            ps = ProductService(db)
            if db.query(Product).count() == 0:
                ps.create("P001", "Laptop Dell XPS", 800.0, 1200.0)
                ps.create("P002", "Wireless Mouse", 20.0, 35.0)
                ps.create("P003", "Mechanical Keyboard", 50.0, 80.0)
                ps.create("P004", "27-inch Monitor", 300.0, 450.0)
                ps.create("P005", "Bluetooth Headphones", 60.0, 95.0)
            
            inv_service = InventoryService(db)
            purch_service = PurchaseService(db, inv_service)
            
            from models import PurchaseOrder
            if db.query(PurchaseOrder).count() == 0:
                po1 = purch_service.create_order(1, [
                    {"product_id": 1, "quantity": 50},
                    {"product_id": 2, "quantity": 100},
                    {"product_id": 3, "quantity": 75}
                ], "admin", "Initial stock for Warehouse A")
                purch_service.confirm_order(po1["id"])
                
                po2 = purch_service.create_order(2, [
                    {"product_id": 4, "quantity": 30},
                    {"product_id": 5, "quantity": 60}
                ], "admin", "Initial stock for Warehouse B")
                purch_service.confirm_order(po2["id"])
            
            return {"message": "Demo data initialized successfully", "status": "ok"}
        except Exception as e:
            logger.error(f"Failed to initialize demo data: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    with get_db() as db:
        ps = ProductService(db)
        p = ps.create(product.code, product.name, product.purchase_price, product.selling_price)
        return {
            "id": p.id, "code": p.code, "name": p.name,
            "purchase_price": p.purchase_price, "selling_price": p.selling_price,
            "is_active": p.is_active, "created_at": p.created_at.isoformat()
        }

@app.get("/api/products")
def list_products(search: Optional[str] = None, active_only: bool = True):
    with get_db() as db:
        ps = ProductService(db)
        products = ps.list_all(search, active_only)
        return [{
            "id": p.id, "code": p.code, "name": p.name,
            "purchase_price": p.purchase_price, "selling_price": p.selling_price,
            "is_active": p.is_active
        } for p in products]

@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    with get_db() as db:
        ps = ProductService(db)
        p = ps.get_by_id(product_id)
        return {
            "id": p.id, "code": p.code, "name": p.name,
            "purchase_price": p.purchase_price, "selling_price": p.selling_price,
            "is_active": p.is_active
        }

@app.put("/api/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    with get_db() as db:
        ps = ProductService(db)
        update_data = {k: v for k, v in product.dict().items() if v is not None}
        p = ps.update(product_id, **update_data)
        return {
            "id": p.id, "code": p.code, "name": p.name,
            "purchase_price": p.purchase_price, "selling_price": p.selling_price
        }

@app.get("/api/inventory/product/{product_id}")
def get_product_inventory(product_id: int):
    with get_db() as db:
        inv_service = InventoryService(db)
        return {
            "product_id": product_id,
            "stock_summary": inv_service.get_total_stock(product_id),
            "by_warehouse": inv_service.get_product_inventory(product_id)
        }

@app.post("/api/purchases/orders", status_code=status.HTTP_201_CREATED)
def create_purchase_order(order: PurchaseOrderCreate):
    with get_db() as db:
        inv_service = InventoryService(db)
        ps = PurchaseService(db, inv_service)
        return ps.create_order(order.warehouse_id, [i.dict() for i in order.items], "api", order.notes)

@app.post("/api/purchases/orders/{order_id}/confirm")
def confirm_purchase_order(order_id: int):
    with get_db() as db:
        inv_service = InventoryService(db)
        ps = PurchaseService(db, inv_service)
        return ps.confirm_order(order_id)

@app.post("/api/purchases/orders/{order_id}/return")
def return_purchase_order(order_id: int):
    with get_db() as db:
        inv_service = InventoryService(db)
        ps = PurchaseService(db, inv_service)
        return ps.return_order(order_id)

@app.get("/api/purchases/orders/{order_id}")
def get_purchase_order(order_id: int):
    with get_db() as db:
        from models import PurchaseOrder
        order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not order:
            raise NotFoundError("PurchaseOrder", order_id)
        inv_service = InventoryService(db)
        ps = PurchaseService(db, inv_service)
        return ps._to_dict(order)

@app.post("/api/sales/orders", status_code=status.HTTP_201_CREATED)
def create_sales_order(order: SalesOrderCreate):
    with get_db() as db:
        inv_service = InventoryService(db)
        ss = SalesService(db, inv_service, AUTO_PURCHASE)
        return ss.create_order(order.warehouse_id, [i.dict() for i in order.items],
                              order.allow_backorder, "api", order.notes)

@app.post("/api/sales/orders/{order_id}/confirm")
def confirm_sales_order(order_id: int):
    with get_db() as db:
        inv_service = InventoryService(db)
        ss = SalesService(db, inv_service, AUTO_PURCHASE)
        return ss.confirm_order(order_id)

@app.post("/api/sales/orders/{order_id}/return")
def return_sales_order(order_id: int):
    with get_db() as db:
        inv_service = InventoryService(db)
        ss = SalesService(db, inv_service)
        return ss.return_order(order_id)

@app.get("/api/sales/orders/{order_id}")
def get_sales_order(order_id: int):
    with get_db() as db:
        from models import SalesOrder
        order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise NotFoundError("SalesOrder", order_id)
        inv_service = InventoryService(db)
        ss = SalesService(db, inv_service)
        return ss._to_dict(order)

@app.get("/api/transactions")
def get_transactions(
    product_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
):
    with get_db() as db:
        from models import InventoryTransaction
        query = db.query(InventoryTransaction)
        if product_id:
            query = query.filter(InventoryTransaction.product_id == product_id)
        if warehouse_id:
            query = query.filter(InventoryTransaction.warehouse_id == warehouse_id)
        if transaction_type:
            query = query.filter(InventoryTransaction.transaction_type == transaction_type)
        
        transactions = query.order_by(InventoryTransaction.created_at.desc()).limit(limit).all()
        return [{
            "id": t.id,
            "product_id": t.product_id,
            "warehouse_id": t.warehouse_id,
            "type": t.transaction_type,
            "change": t.quantity_change,
            "before": t.quantity_before,
            "after": t.quantity_after,
            "reference_type": t.reference_type,
            "reference_id": t.reference_id,
            "batch_id": t.batch_id,
            "created_at": t.created_at.isoformat()
        } for t in transactions]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, workers=4)