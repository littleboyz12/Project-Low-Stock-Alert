from database import SessionLocal, engine
import models

# สร้างตารางถ้ายังไม่มี (ไม่ drop ของเดิม)
models.Base.metadata.create_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ========================
# Seed Users
# ========================
admin = models.User(username="admin", password="1234", role="admin")
db.add(admin)
db.commit()
print("User created: admin / 1234")

# ========================
# Seed Categories
# ========================
categories_data = ["Electronics", "Food & Beverage", "Office Supplies", "Cleaning", "Packaging"]
categories = []
for name in categories_data:
    cat = models.Category(name=name)
    db.add(cat)
    categories.append(cat)
db.commit()
print(f"Categories created: {len(categories)}")

# ========================
# Seed Products
# ========================
from datetime import datetime

products_data = [
    {"name": "Wireless Mouse", "sku": "ELEC-001", "price": 350.00, "quantity": 5, "min_stock": 10, "category_id": categories[0].id},
    {"name": "USB-C Cable", "sku": "ELEC-002", "price": 120.00, "quantity": 25, "min_stock": 15, "category_id": categories[0].id},
    {"name": "Bluetooth Speaker", "sku": "ELEC-003", "price": 890.00, "quantity": 0, "min_stock": 5, "category_id": categories[0].id},
    {"name": "Power Bank 10000mAh", "sku": "ELEC-004", "price": 550.00, "quantity": 3, "min_stock": 10, "category_id": categories[0].id},
    {"name": "Instant Noodles (Box)", "sku": "FOOD-001", "price": 180.00, "quantity": 50, "min_stock": 20, "category_id": categories[1].id},
    {"name": "Drinking Water 600ml", "sku": "FOOD-002", "price": 7.00, "quantity": 8, "min_stock": 30, "category_id": categories[1].id},
    {"name": "Coffee Mix 3in1", "sku": "FOOD-003", "price": 250.00, "quantity": 0, "min_stock": 10, "category_id": categories[1].id},
    {"name": "A4 Paper (Ream)", "sku": "OFFC-001", "price": 135.00, "quantity": 12, "min_stock": 10, "category_id": categories[2].id},
    {"name": "Ballpoint Pen (Box)", "sku": "OFFC-002", "price": 85.00, "quantity": 2, "min_stock": 5, "category_id": categories[2].id},
    {"name": "Stapler", "sku": "OFFC-003", "price": 65.00, "quantity": 20, "min_stock": 5, "category_id": categories[2].id},
    {"name": "Floor Cleaner 1L", "sku": "CLEN-001", "price": 75.00, "quantity": 4, "min_stock": 10, "category_id": categories[3].id},
    {"name": "Trash Bags (Roll)", "sku": "CLEN-002", "price": 45.00, "quantity": 0, "min_stock": 15, "category_id": categories[3].id},
    {"name": "Bubble Wrap 30m", "sku": "PACK-001", "price": 220.00, "quantity": 7, "min_stock": 5, "category_id": categories[4].id},
    {"name": "Cardboard Box (Medium)", "sku": "PACK-002", "price": 15.00, "quantity": 100, "min_stock": 30, "category_id": categories[4].id},
]

for p_data in products_data:
    product = models.Product(**p_data)
    db.add(product)
db.commit()
print(f"Products created: {len(products_data)}")

# ========================
# Seed Stock Movements
# ========================
products = db.query(models.Product).all()

movements_data = [
    {"product_id": products[0].id, "movement_type": "IN", "quantity": 20, "note": "Initial stock"},
    {"product_id": products[0].id, "movement_type": "OUT", "quantity": 15, "note": "Sold to customer"},
    {"product_id": products[1].id, "movement_type": "IN", "quantity": 30, "note": "Restocked from supplier"},
    {"product_id": products[1].id, "movement_type": "OUT", "quantity": 5, "note": "Used internally"},
    {"product_id": products[4].id, "movement_type": "IN", "quantity": 50, "note": "Bulk purchase"},
    {"product_id": products[7].id, "movement_type": "IN", "quantity": 20, "note": "Office supplies order"},
    {"product_id": products[7].id, "movement_type": "OUT", "quantity": 8, "note": "Distributed to departments"},
]

for m_data in movements_data:
    movement = models.StockMovement(is_read=True, **m_data)
    db.add(movement)
db.commit()
print(f"Stock movements created: {len(movements_data)}")

db.close()
print("\nSeed completed successfully!")
print("Login with: admin / 1234")
