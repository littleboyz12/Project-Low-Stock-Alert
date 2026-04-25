from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Category ---
class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True


# --- Product ---
class ProductCreate(BaseModel):
    name: str
    sku: str
    price: float
    quantity: int = 0
    min_stock: int = 10
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    min_stock: Optional[int] = None
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    price: float
    quantity: int
    min_stock: int
    category_id: int
    is_low_stock: bool
    created_at: datetime
    class Config:
        from_attributes = True


# --- Stock Movement ---
class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: str  # IN or OUT
    quantity: int
    note: Optional[str] = None

class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity: int
    note: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True


# --- Auth ---
class LoginSchema(BaseModel):
    username: str
    password: str
