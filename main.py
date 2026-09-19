from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

# 1. IMPORTAR EL ROUTER DESDE ai_services.py
from ai_services import router as ai_router

# Crear automáticamente las tablas en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaaS Builder API",
    description="API en Python (FastAPI) conectada a MySQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. CONECTAR LAS RUTAS DE IA A LA APLICACIÓN PRINCIPAL
app.include_router(ai_router)


# --- ESQUEMAS DE TIENDAS ---

class PageBlock(BaseModel):
    type: str
    props: Dict[str, Any] = {}

class StoreData(BaseModel):
    name: str
    slug: str
    layout_data: List[PageBlock]


@app.get("/")
def home():
    return {"status": "ok", "message": "API de FastAPI conectada a MySQL corriendo"}


# --- ENDPOINTS DE TIENDAS ---

# GET: Obtener tienda desde MySQL
@app.get("/api/stores/{slug}")
def get_store(slug: str, db: Session = Depends(get_db)):
    store = db.query(models.StoreModel).filter(models.StoreModel.slug == slug).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada en la base de datos")
    
    return {
        "id": store.id,
        "name": store.name,
        "slug": store.slug,
        "layout_data": store.layout_data
    }

# POST: Crear o actualizar tienda en MySQL
@app.post("/api/stores")
def save_store(store: StoreData, db: Session = Depends(get_db)):
    db_store = db.query(models.StoreModel).filter(models.StoreModel.slug == store.slug).first()
    
    # Convierte directamente usando la sintaxis oficial de Pydantic V2
    layout_json = [block.model_dump() for block in store.layout_data]

    if db_store:
        db_store.name = store.name
        db_store.layout_data = layout_json
    else:
        db_store = models.StoreModel(
            name=store.name,
            slug=store.slug,
            layout_data=layout_json
        )
        db.add(db_store)

    db.commit()
    db.refresh(db_store)

    return {
        "message": "¡Tienda guardada con éxito en MySQL!",
        "store": {
            "id": db_store.id,
            "name": db_store.name,
            "slug": db_store.slug,
            "layout_data": db_store.layout_data
        }
    }


# --- ENDPOINTS DE PRODUCTOS ---

# GET: Listar productos de una tienda
@app.get("/api/stores/{slug}/products", response_model=List[schemas.ProductResponse], tags=["Products"])
def get_store_products(slug: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.store_slug == slug).all()
    return products

# POST: Crear un nuevo producto en una tienda
@app.post("/api/stores/{slug}/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(slug: str, product_data: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(**product_data.model_dump(), store_slug=slug)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# DELETE: Eliminar un producto por ID
@app.delete("/api/stores/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(product)
    db.commit()
    return None

# PUT: Actualizar un producto existente
@app.put("/api/stores/products/{product_id}", response_model=schemas.ProductResponse, tags=["Products"])
def update_product(product_id: int, product_data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product