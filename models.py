from sqlalchemy import Column, DateTime, Integer, String, Float, Text, JSON, func
from database import Base  # Ajusta si tu importación varía

class StoreModel(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    layout_data = Column(JSON, nullable=True)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    store_slug = Column(String(100), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    stock = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())