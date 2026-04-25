# Smart Inventory & Low Stock Alert

ระบบจัดการสินค้าคงคลัง พร้อมแจ้งเตือนสินค้าใกล้หมด/หมดสต็อก พัฒนาด้วย FastAPI + SQLAlchemy + JWT

## Features

- **Admin Web Panel** (Session Authentication)
  - Dashboard สรุปข้อมูลสินค้า
  - CRUD Products / Categories
  - Stock Movement (IN/OUT) tracking
  - Low Stock & Out of Stock Alerts
- **REST API** (JWT Authentication)
  - `/api/v1/login` - ขอ access token
  - `/api/v1/products` - CRUD products
  - `/api/v1/categories` - CRUD categories
  - `/api/v1/stock-movements` - บันทึกการเคลื่อนไหวสต็อก
  - `/api/v1/alerts/low-stock` - รายการสินค้าใกล้หมด
- **Real-time Notifications**
  - 🔔 Bell icon + badge บน navbar
  - 🟢/🔴 Toast pop-up เมื่อมี movement ใหม่
  - 🔊 เสียงแจ้งเตือน
  - Auto-polling ทุก 5 วินาที

## Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM + SQLite
- **Jinja2** - HTML templates
- **PyJWT** - JWT authentication for API
- **Bootstrap 5** - UI framework

## Setup

```bash
# 1. ติดตั้ง dependencies
pip install -r requirements.txt

# 2. สร้างฐานข้อมูล + seed data
python seed.py

# 3. รัน server
python -m uvicorn main:app --reload
```

## Access

- **Web Admin**: http://localhost:8000 (login: `admin` / `1234`)
- **API Docs (Swagger)**: http://localhost:8000/docs

## Project Structure

```
.
├── main.py             # Web routes + session auth
├── api.py              # REST API endpoints (JWT protected)
├── jwt_auth.py         # JWT create/verify
├── models.py           # SQLAlchemy models
├── schema.py           # Pydantic schemas
├── database.py         # DB connection
├── seed.py             # Seed sample data
├── requirements.txt
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
└── templates/
    ├── master.html
    ├── login.html
    ├── index.html
    ├── product_list.html
    ├── product_form.html
    ├── category_list.html
    ├── category_form.html
    ├── stock_movement.html
    └── alerts.html
```

## Database Models

- **User** - admin users (username, password, role)
- **Category** - product categories
- **Product** - products with quantity, min_stock threshold
- **StockMovement** - IN/OUT tracking with is_read flag
