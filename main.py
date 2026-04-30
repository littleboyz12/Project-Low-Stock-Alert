import os
from fastapi import FastAPI

# Models & Database
import models
from database import engine, SessionLocal
models.Base.metadata.create_all(bind=engine)

# Auto-seed ถ้าฐานข้อมูลว่างเปล่า (ไม่มี user)
def auto_seed():
    db = SessionLocal()
    try:
        user_count = db.query(models.User).count()
        if user_count == 0:
            import seed  # รัน seed.py
    except Exception as e:
        print(f"Auto-seed error: {e}")
    finally:
        db.close()

auto_seed()

app = FastAPI(title="Smart Inventory & Low Stock Alert")

# Session Middleware
from starlette.middleware.sessions import SessionMiddleware
SESSION_SECRET = os.environ.get("SESSION_SECRET_KEY", "inventory-session-secret-123")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Static files
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Register API router
from api import router
app.include_router(router)


# ========================
# Auth Helper
# ========================
from fastapi import Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from database import SessionLocal
from models import Product, Category, StockMovement, User


def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)
    return user


# ========================
# Login / Logout
# ========================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "login.html")


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and user.password == password:
            request.session["user"] = username
            return RedirectResponse("/", status_code=303)
        return templates.TemplateResponse(request, "login.html", {
            "error": "Invalid username or password"
        })
    finally:
        db.close()


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# ========================
# Dashboard (Home)
# ========================

@app.get("/", response_class=HTMLResponse)
def home(request: Request, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    db = SessionLocal()
    try:
        total_products = db.query(Product).count()
        total_categories = db.query(Category).count()
        low_stock = db.query(Product).filter(Product.quantity <= Product.min_stock, Product.quantity > 0).all()
        out_of_stock = db.query(Product).filter(Product.quantity == 0).all()
        recent_movements = db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(10).all()

        return templates.TemplateResponse(request, "index.html", {
            "user": user,
            "total_products": total_products,
            "total_categories": total_categories,
            "low_stock_count": len(low_stock),
            "out_of_stock_count": len(out_of_stock),
            "low_stock_items": low_stock,
            "out_of_stock_items": out_of_stock,
            "recent_movements": recent_movements
        })
    finally:
        db.close()


# ========================
# Product CRUD (Admin)
# ========================
from fastapi import UploadFile, File
import shutil
import os

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/products", response_class=HTMLResponse)
def product_list(request: Request, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        return templates.TemplateResponse(request, "product_list.html", {
            "user": user,
            "products": products
        })
    finally:
        db.close()


@app.get("/products/create", response_class=HTMLResponse)
def product_create_form(request: Request, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return templates.TemplateResponse(request, "product_form.html", {
            "user": user,
            "categories": categories
        })
    finally:
        db.close()


@app.post("/products/create")
def product_create(
    name: str = Form(...),
    sku: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(0),
    min_stock: int = Form(10),
    category_id: int = Form(...),
    image: UploadFile = File(None)
):
    db = SessionLocal()

    filename = None
    if image and image.filename:
        filename = image.filename
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    product = Product(
        name=name,
        sku=sku,
        price=price,
        quantity=quantity,
        min_stock=min_stock,
        category_id=category_id,
        image=filename
    )
    db.add(product)
    db.commit()
    db.close()
    return RedirectResponse("/products", status_code=303)


@app.get("/products/edit/{id}", response_class=HTMLResponse)
def product_edit_form(request: Request, id: int, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    db = SessionLocal()
    try:
        product = db.get(Product, id)
        categories = db.query(Category).all()
        return templates.TemplateResponse(request, "product_form.html", {
            "user": user,
            "product": product,
            "categories": categories
        })
    finally:
        db.close()


@app.post("/products/edit/{id}")
def product_update(
    id: int,
    name: str = Form(...),
    sku: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(0),
    min_stock: int = Form(10),
    category_id: int = Form(...),
    image: UploadFile = File(None)
):
    db = SessionLocal()
    product = db.get(Product, id)
    product.name = name
    product.sku = sku
    product.price = price
    product.quantity = quantity
    product.min_stock = min_stock
    product.category_id = category_id

    if image and image.filename:
        filename = image.filename
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        product.image = filename

    db.commit()
    db.close()
    return RedirectResponse("/products", status_code=303)


@app.get("/products/delete/{id}")
def product_delete(id: int):
    db = SessionLocal()
    product = db.get(Product, id)
    db.delete(product)
    db.commit()
    db.close()
    return RedirectResponse("/products", status_code=303)


# ========================
# Category CRUD (Admin)
# ========================

@app.get("/categories", response_class=HTMLResponse)
def category_list(request: Request, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return templates.TemplateResponse(request, "category_list.html", {
            "user": user,
            "categories": categories
        })
    finally:
        db.close()


@app.get("/categories/create", response_class=HTMLResponse)
def category_create_form(request: Request, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request, "category_form.html", {
        "user": user
    })


@app.post("/categories/create")
def category_create(name: str = Form(...)):
    db = SessionLocal()
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.close()
    return RedirectResponse("/categories", status_code=303)


@app.get("/categories/edit/{id}", response_class=HTMLResponse)
def category_edit_form(request: Request, id: int, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    db = SessionLocal()
    try:
        category = db.get(Category, id)
        return templates.TemplateResponse(request, "category_form.html", {
            "user": user,
            "category": category
        })
    finally:
        db.close()


@app.post("/categories/edit/{id}")
def category_update(id: int, name: str = Form(...)):
    db = SessionLocal()
    category = db.get(Category, id)
    category.name = name
    db.commit()
    db.close()
    return RedirectResponse("/categories", status_code=303)


@app.get("/categories/delete/{id}")
def category_delete(id: int):
    db = SessionLocal()
    category = db.get(Category, id)
    db.delete(category)
    db.commit()
    db.close()
    return RedirectResponse("/categories", status_code=303)


# ========================
# Stock Movement (Admin)
# ========================

@app.get("/stock", response_class=HTMLResponse)
def stock_movement_page(request: Request, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    db = SessionLocal()
    try:
        # Mark all movements as read when visiting this page
        db.query(StockMovement).filter(StockMovement.is_read == False).update({"is_read": True})
        db.commit()

        products = db.query(Product).all()
        movements = db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(50).all()
        return templates.TemplateResponse(request, "stock_movement.html", {
            "user": user,
            "products": products,
            "movements": movements
        })
    finally:
        db.close()


@app.post("/stock")
def stock_movement_create(
    product_id: int = Form(...),
    movement_type: str = Form(...),
    quantity: int = Form(...),
    note: str = Form("")
):
    db = SessionLocal()
    product = db.get(Product, product_id)

    if movement_type == "IN":
        product.quantity += quantity
    elif movement_type == "OUT":
        product.quantity -= quantity

    movement = StockMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity,
        note=note,
        is_read=False
    )
    db.add(movement)
    db.commit()
    db.close()
    return RedirectResponse("/stock", status_code=303)


# ========================
# Notifications
# ========================
from fastapi.responses import JSONResponse

@app.get("/notifications/count")
def notifications_count(request: Request):
    if not request.session.get("user"):
        return JSONResponse({"count": 0, "items": []})
    db = SessionLocal()
    try:
        unread = db.query(StockMovement).filter(StockMovement.is_read == False)\
            .order_by(StockMovement.created_at.desc()).limit(10).all()
        return JSONResponse({
            "count": len(unread),
            "items": [
                {
                    "id": m.id,
                    "product_name": m.product.name if m.product else "N/A",
                    "movement_type": m.movement_type,
                    "quantity": m.quantity,
                    "note": m.note or "",
                    "created_at": m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else ""
                }
                for m in unread
            ]
        })
    finally:
        db.close()


@app.post("/notifications/mark-read")
def notifications_mark_read(request: Request):
    if not request.session.get("user"):
        return JSONResponse({"status": "unauthorized"}, status_code=401)
    db = SessionLocal()
    try:
        db.query(StockMovement).filter(StockMovement.is_read == False).update({"is_read": True})
        db.commit()
        return JSONResponse({"status": "success"})
    finally:
        db.close()


# ========================
# Alerts Page (Admin)
# ========================

@app.get("/alerts", response_class=HTMLResponse)
def alerts_page(request: Request, user=Depends(get_current_user)):
    if isinstance(user, RedirectResponse):
        return user
    db = SessionLocal()
    try:
        low_stock = db.query(Product).filter(
            Product.quantity <= Product.min_stock,
            Product.quantity > 0
        ).all()
        out_of_stock = db.query(Product).filter(Product.quantity == 0).all()
        return templates.TemplateResponse(request, "alerts.html", {
            "user": user,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock
        })
    finally:
        db.close()
