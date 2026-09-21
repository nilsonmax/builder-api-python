from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class StoreCreate(BaseModel):
    name: str

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    content: Optional[Any] = None  # Recibe los bloques/componentes del editor

class StoreResponse(BaseModel):
    id: str
    name: str
    slug: str
    status: str
    content: Optional[Any] = None  # Devuelve los bloques/componentes del editor
    updatedAt: str

    class Config:
        from_attributes = True

# Para crear un producto
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category: Optional[str] = None
    stock: Optional[int] = 10

# Para actualizar un producto
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    stock: Optional[int] = None

# Respuesta de la API
class ProductResponse(ProductCreate):
    id: int
    store_slug: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True # En Pydantic v1 usa orm_mode = True