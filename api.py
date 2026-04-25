from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from models import Product, Category, StockMovement, User
from schema import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryResponse,
    StockMovementCreate, StockMovementResponse,
    LoginSchema
)
from jwt_auth import create_token, verify_token

router = APIRouter()

ENDPOINT = "/api/v1"


# ========================
# Auth API
# ========================

@router.post(ENDPOINT + "/login")
def api_login(data: LoginSchema):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == data.username).first()
        if not user or user.password != data.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = create_token(user.username)
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    finally:
        db.close()


# ========================
# Category API (Protected)
# ========================

@router.get(ENDPOINT + "/categories")
def api_category_list(user=Depends(verify_token)):
    db = SessionLocal()
    try:
        return db.query(Category).all()
    finally:
        db.close()


@router.get(ENDPOINT + "/categories/{id}")
def api_category_detail(id: int, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        category = db.get(Category, id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    finally:
        db.close()


@router.post(ENDPOINT + "/categories")
def api_category_create(data: CategoryCreate, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        category = Category(name=data.name)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    finally:
        db.close()


@router.put(ENDPOINT + "/categories/{id}")
def api_category_update(id: int, data: CategoryCreate, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        category = db.get(Category, id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        category.name = data.name
        db.commit()
        db.refresh(category)
        return category
    finally:
        db.close()


@router.delete(ENDPOINT + "/categories/{id}")
def api_category_delete(id: int, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        category = db.get(Category, id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db.delete(category)
        db.commit()
        return {"message": "Category deleted"}
    finally:
        db.close()


# ========================
# Product API (Protected)
# ========================

@router.get(ENDPOINT + "/products")
def api_product_list(user=Depends(verify_token)):
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "price": p.price,
                "quantity": p.quantity,
                "min_stock": p.min_stock,
                "category_id": p.category_id,
                "is_low_stock": p.is_low_stock,
                "image": p.image,
                "created_at": str(p.created_at)
            }
            for p in products
        ]
    finally:
        db.close()


@router.get(ENDPOINT + "/products/{id}")
def api_product_detail(id: int, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        product = db.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": product.price,
            "quantity": product.quantity,
            "min_stock": product.min_stock,
            "category_id": product.category_id,
            "is_low_stock": product.is_low_stock,
            "image": product.image,
            "created_at": str(product.created_at)
        }
    finally:
        db.close()


@router.post(ENDPOINT + "/products")
def api_product_create(data: ProductCreate, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        product = Product(
            name=data.name,
            sku=data.sku,
            price=data.price,
            quantity=data.quantity,
            min_stock=data.min_stock,
            category_id=data.category_id
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return {"message": "Product created", "id": product.id}
    finally:
        db.close()


@router.put(ENDPOINT + "/products/{id}")
def api_product_update(id: int, data: ProductUpdate, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        product = db.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if data.name is not None:
            product.name = data.name
        if data.sku is not None:
            product.sku = data.sku
        if data.price is not None:
            product.price = data.price
        if data.quantity is not None:
            product.quantity = data.quantity
        if data.min_stock is not None:
            product.min_stock = data.min_stock
        if data.category_id is not None:
            product.category_id = data.category_id
        db.commit()
        db.refresh(product)
        return {"message": "Product updated"}
    finally:
        db.close()


@router.delete(ENDPOINT + "/products/{id}")
def api_product_delete(id: int, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        product = db.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        db.delete(product)
        db.commit()
        return {"message": "Product deleted"}
    finally:
        db.close()


# ========================
# Stock Movement API (Protected)
# ========================

@router.get(ENDPOINT + "/stock-movements")
def api_stock_movement_list(user=Depends(verify_token)):
    db = SessionLocal()
    try:
        movements = db.query(StockMovement).order_by(StockMovement.created_at.desc()).all()
        return [
            {
                "id": m.id,
                "product_id": m.product_id,
                "product_name": m.product.name if m.product else None,
                "movement_type": m.movement_type,
                "quantity": m.quantity,
                "note": m.note,
                "created_at": str(m.created_at)
            }
            for m in movements
        ]
    finally:
        db.close()


@router.post(ENDPOINT + "/stock-movements")
def api_stock_movement_create(data: StockMovementCreate, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        product = db.get(Product, data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if data.movement_type == "IN":
            product.quantity += data.quantity
        elif data.movement_type == "OUT":
            if product.quantity < data.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock")
            product.quantity -= data.quantity
        else:
            raise HTTPException(status_code=400, detail="movement_type must be IN or OUT")

        movement = StockMovement(
            product_id=data.product_id,
            movement_type=data.movement_type,
            quantity=data.quantity,
            note=data.note
        )
        db.add(movement)
        db.commit()
        return {"message": "Stock movement recorded", "new_quantity": product.quantity}
    finally:
        db.close()


# ========================
# Low Stock Alert API (Protected)
# ========================

@router.get(ENDPOINT + "/alerts/low-stock")
def api_low_stock_alerts(user=Depends(verify_token)):
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.quantity <= Product.min_stock).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "quantity": p.quantity,
                "min_stock": p.min_stock,
                "category_id": p.category_id,
                "status": "OUT OF STOCK" if p.quantity == 0 else "LOW STOCK"
            }
            for p in products
        ]
    finally:
        db.close()


# ========================
# Dashboard API (Protected)
# ========================

@router.get(ENDPOINT + "/dashboard")
def api_dashboard(user=Depends(verify_token)):
    db = SessionLocal()
    try:
        total_products = db.query(Product).count()
        total_categories = db.query(Category).count()
        low_stock_count = db.query(Product).filter(Product.quantity <= Product.min_stock).count()
        out_of_stock_count = db.query(Product).filter(Product.quantity == 0).count()
        return {
            "total_products": total_products,
            "total_categories": total_categories,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count
        }
    finally:
        db.close()


# ========================
# Search API (Protected)
# ========================

@router.get(ENDPOINT + "/products/search")
def api_product_search(search: str = "", user=Depends(verify_token)):
    db = SessionLocal()
    try:
        products = db.query(Product).filter(
            Product.name.like(f"%{search}%")
        ).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "quantity": p.quantity,
                "min_stock": p.min_stock,
                "is_low_stock": p.is_low_stock
            }
            for p in products
        ]
    finally:
        db.close()
