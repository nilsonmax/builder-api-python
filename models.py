from sqlalchemy import Column, DateTime, Integer, String, Float, Text, JSON, DateTime, Enum, func
from database import Base  # Ajusta si tu importación varía
import datetime
import uuid

class Store(Base):
    __tablename__ = "stores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="draft")  # draft o published
    content = Column(Text, nullable=True)  # Estructura JSON de bloques del editor   #layout_data = Column(JSON, nullable=True) estaba en el codigo anterior
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    

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
    