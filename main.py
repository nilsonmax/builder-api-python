from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import re

import models
import schemas
from database import engine, get_db

# Importar las rutas del servicio de IA
from ai_services import router as ai_router

# Crear automáticamente las tablas en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

# Instancia PRINCIPAL de FastAPI (Solo una)
app = FastAPI(
    title="SaaS Builder API",
    description="API en Python (FastAPI) conectada a MySQL",
    version="1.0.0"
)

# Configuración de CORS para comunicarse con Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de Gemini / IA
app.include_router(ai_router)


# --- ESQUEMAS AUXILIARES ---

class StoreUpdatePayload(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None  # "draft" o "published"
    content: Optional[Any] = None  # Lista de bloques del editor


# --- FUNCIONES AUXILIARES ---

def generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug or "mi-tienda"


# --- RUTAS PRINCIPALES ---

@app.get("/")
def home():
    return {"status": "ok", "message": "API de FastAPI conectada a MySQL corriendo"}


# --- ENDPOINTS DE TIENDAS (STORES) ---

# 1. LISTAR TODAS LAS TIENDAS
@app.get("/api/stores", response_model=List[schemas.StoreResponse], tags=["Stores"])
def get_stores(db: Session = Depends(get_db)):
    try:
        stores = db.query(models.Store).order_by(models.Store.id.desc()).all()
        
        response = []
        for store in stores:
            # Manejo seguro de fechas para evitar AttributeError si es None
            formatted_date = (
                store.updated_at.strftime("%Y-%m-%d %H:%M") 
                if getattr(store, 'updated_at', None) 
                else "N/A"
            )
            
            response.append(
                schemas.StoreResponse(
                    id=str(store.id),
                    name=store.name,
                    slug=store.slug,
                    status=getattr(store, 'status', 'draft') or 'draft',
                    updatedAt=formatted_date
                )
            )
        return response

    except Exception as e:
        print(f"Error en GET /api/stores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


# 2. CREAR NUEVA TIENDA
# @app.post("/api/stores", response_model=schemas.StoreResponse, tags=["Stores"])
# def create_store(store_data: schemas.StoreCreate, db: Session = Depends(get_db)):
#     base_slug = generate_slug(store_data.name)
    
#     slug = base_slug
#     counter = 1
#     while db.query(models.Store).filter(models.Store.slug == slug).first():
#         slug = f"{base_slug}-{counter}"
#         counter += 1

#     new_store = models.Store(
#         name=store_data.name,
#         slug=slug,
#         status="draft",
#         content="[]"
#     )
    
#     db.add(new_store)
#     db.commit()
#     db.refresh(new_store)

#     return schemas.StoreResponse(
#         id=new_store.id,
#         name=new_store.name,
#         slug=new_store.slug,
#         status=new_store.status,
#         updatedAt=new_store.updated_at.strftime("%Y-%m-%d %H:%M")
#     )

@app.post("/api/stores", response_model=schemas.StoreResponse, tags=["Stores"])
def create_store(store_data: schemas.StoreCreate, db: Session = Depends(get_db)):
    base_slug = generate_slug(store_data.name)
    
    slug = base_slug
    counter = 1
    while db.query(models.Store).filter(models.Store.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Si viene contenido desde el frontend se convierte a texto JSON; si no, queda []
    content_value = "[]"
    if getattr(store_data, "content", None) is not None:
        content_value = json.dumps(store_data.content) if isinstance(store_data.content, (list, dict)) else str(store_data.content)

    new_store = models.Store(
        name=store_data.name,
        slug=slug,
        status="draft",
        content=content_value
    )
    
    db.add(new_store)
    db.commit()
    db.refresh(new_store)

    return schemas.StoreResponse(
        id=new_store.id,
        name=new_store.name,
        slug=new_store.slug,
        status=new_store.status,
        content=new_store.content,
        updatedAt=new_store.updated_at.strftime("%Y-%m-%d %H:%M")
    )

# 3. OBTENER UNA TIENDA POR ID (Para el Editor Visual)
# @app.get("/api/stores/{store_id}", tags=["Stores"])
# def get_store_by_id(store_id: str, db: Session = Depends(get_db)):
#     store = db.query(models.Store).filter(models.Store.id == store_id).first()
#     if not store:
#         raise HTTPException(status_code=404, detail="Tienda no encontrada")
    
#     # Parseamos el JSON de bloques si viene como texto
#     try:
#         content_data = json.loads(store.content) if isinstance(store.content, str) else store.content
#     except Exception:
#         content_data = []

#     return {
#         "id": store.id,
#         "name": store.name,
#         "slug": store.slug,
#         "status": store.status,
#         "content": content_data,
#         "updatedAt": store.updated_at.strftime("%Y-%m-%d %H:%M")
#     }


# # 4. OBTENER UNA TIENDA POR SLUG (Para la Tienda Pública)
# @app.get("/api/stores/slug/{slug}", tags=["Stores"])
# def get_store_by_slug(slug: str, db: Session = Depends(get_db)):
#     store = db.query(models.Store).filter(models.Store.slug == slug).first()
#     if not store:
#         raise HTTPException(status_code=404, detail="Tienda no encontrada")
    
#     try:
#         content_data = json.loads(store.content) if isinstance(store.content, str) else store.content
#     except Exception:
#         content_data = []

#     return {
#         "id": store.id,
#         "name": store.name,
#         "slug": store.slug,
#         "status": store.status,
#         "content": content_data
#     }

# 3. OBTENER UNA TIENDA (Acepta tanto ID como SLUG)
@app.get("/api/stores/{identifier}", tags=["Stores"])
def get_store(identifier: str, db: Session = Depends(get_db)):
    # Buscar primero por ID; si no existe, buscar por Slug
    store = db.query(models.Store).filter(
        (models.Store.id == identifier) | (models.Store.slug == identifier)
    ).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    
    # Parseamos el JSON de bloques si viene como texto
    try:
        content_data = json.loads(store.content) if isinstance(store.content, str) else store.content
    except Exception:
        content_data = []

    return {
        "id": store.id,
        "name": store.name,
        "slug": store.slug,
        "status": store.status,
        "content": content_data,
        "updatedAt": store.updated_at.strftime("%Y-%m-%d %H:%M") if getattr(store, 'updated_at', None) else "N/A"
    }

# 5. ACTUALIZAR TIENDA / GUARDAR BLOQUES (Desde el Editor Visual)
# @app.put("/api/stores/{store_id}", tags=["Stores"])
# def update_store(store_id: str, payload: StoreUpdatePayload, db: Session = Depends(get_db)):
#     store = db.query(models.Store).filter(models.Store.id == store_id).first()
#     if not store:
#         raise HTTPException(status_code=404, detail="Tienda no encontrada")

#     if payload.name is not None:
#         store.name = payload.name
#     if payload.status is not None:
#         store.status = payload.status
#     if payload.content is not None:
#         # Guardamos la estructura de bloques como cadena JSON
#         store.content = json.dumps(payload.content) if not isinstance(payload.content, str) else payload.content

#     db.commit()
#     db.refresh(store)

#     return {
#         "message": "Tienda actualizada correctamente",
#         "store_id": store.id,
#         "status": store.status
#     }

# 4. ACTUALIZAR TIENDA / GUARDAR BLOQUES (Desde el Editor Visual)
@app.put("/api/stores/{store_id}", response_model=schemas.StoreResponse, tags=["Stores"])
def update_store(store_id: str, store_data: schemas.StoreUpdate, db: Session = Depends(get_db)):
    db_store = db.query(models.Store).filter(models.Store.id == store_id).first()
    
    if not db_store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")

    if store_data.name is not None:
        db_store.name = store_data.name
    if store_data.status is not None:
        db_store.status = store_data.status
        
    # Guarda la información que envía el editor
    if store_data.content is not None:
        if isinstance(store_data.content, (list, dict)):
            db_store.content = json.dumps(store_data.content)
        else:
            db_store.content = str(store_data.content)

    db.commit()
    db.refresh(db_store)

    return schemas.StoreResponse(
        id=db_store.id,
        name=db_store.name,
        slug=db_store.slug,
        status=db_store.status,
        content=db_store.content,
        updatedAt=db_store.updated_at.strftime("%Y-%m-%d %H:%M")
    )

# --- ENDPOINTS DE PRODUCTOS ---

@app.get("/api/stores/{slug}/products", response_model=List[schemas.ProductResponse], tags=["Products"])
def get_store_products(slug: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.store_slug == slug).all()
    return products


@app.post("/api/stores/{slug}/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(slug: str, product_data: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(**product_data.model_dump(), store_slug=slug)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.delete("/api/stores/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(product)
    db.commit()
    return None


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