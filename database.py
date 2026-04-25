import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ถ้ามี DATABASE_URL จาก environment (Render) ให้ใช้ PostgreSQL
# ถ้าไม่มี ใช้ SQLite (local development)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./inventory.sqlite3")

# Render ให้ DATABASE_URL เป็น postgres:// แต่ SQLAlchemy ต้องการ postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite ต้องการ check_same_thread=False แต่ PostgreSQL ไม่ต้องการ
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
