from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    odoo_id: int
    name: str
    email: str | None = None
    phone: str | None = None
    street: str | None = None
    city: str | None = None
    country: str | None = None
    is_company: bool
    created_at: datetime
    updated_at: datetime


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    odoo_id: int
    name: str
    default_code: str | None = None
    list_price: Decimal
    uom_name: str | None = None
    active: bool
    created_at: datetime
    updated_at: datetime


class SaleOrderLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    odoo_id: int
    sale_order_id: int
    product_id: int | None = None
    name: str
    product_uom_qty: Decimal
    price_unit: Decimal
    price_subtotal: Decimal
    created_at: datetime
    updated_at: datetime


class SaleOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    odoo_id: int
    name: str
    contact_id: int
    state: str
    amount_total: Decimal
    date_order: datetime | None = None
    created_at: datetime
    updated_at: datetime
    lines: list[SaleOrderLineRead] = Field(default_factory=list)


class SyncEntityResult(BaseModel):
    created: int = 0
    updated: int = 0
    errored: int = 0
    total: int = 0


class SyncResult(BaseModel):
    contacts: SyncEntityResult
    products: SyncEntityResult
    sale_orders: SyncEntityResult
    sale_order_lines: SyncEntityResult

class SyncRunCreate(BaseModel):
    sync_type: str = "sync_all"
    sync_start_time: datetime
    sync_end_time: datetime
    fetched_records: int = 0
    stored_records: int = 0
    updated_records: int = 0
    error_records: int = 0
    sync_error: str | None = None

class SyncLogCreate(BaseModel):
    sync_run_id: int = 1
    level: str = "log"
    message: str = ""
    data: dict
