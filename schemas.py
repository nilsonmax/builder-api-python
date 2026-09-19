from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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