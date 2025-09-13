from fastapi import APIRouter, HTTPException, status
from typing import List
from models.productos import Producto, ProductoCreate, ProductoUpdate
from database import get_productos_collection
import uuid
from bson import ObjectId

router = APIRouter()

def convert_objectid(doc):
    """Convierte ObjectId a string para serialización"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("/", response_model=List[Producto])
async def get_productos():
    """Obtener todos los productos"""
    collection = await get_productos_collection()
    productos = await collection.find().to_list(1000)
    return [convert_objectid(producto) for producto in productos]

@router.get("/{producto_id}", response_model=Producto)
async def get_producto(producto_id: str):
    """Obtener un producto por ID"""
    collection = await get_productos_collection()
    producto = await collection.find_one({"_id": ObjectId(producto_id)})
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return convert_objectid(producto)

@router.post("/", response_model=Producto, status_code=status.HTTP_201_CREATED)
async def create_producto(producto: ProductoCreate):
    """Crear un nuevo producto"""
    collection = await get_productos_collection()
    
    # Generar ID único
    producto_id = f"P{str(uuid.uuid4())[:8].upper()}"
    
    producto_dict = producto.model_dump()
    producto_dict["_id"] = producto_id
    
    result = await collection.insert_one(producto_dict)
    
    if result.inserted_id:
        created_producto = await collection.find_one({"_id": producto_id})
        return convert_objectid(created_producto)
    
    raise HTTPException(status_code=400, detail="Error al crear el producto")

@router.put("/{producto_id}", response_model=Producto)
async def update_producto(producto_id: str, producto: ProductoUpdate):
    """Actualizar un producto"""
    collection = await get_productos_collection()
    
    # Filtrar campos no nulos
    update_data = {k: v for k, v in producto.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = await collection.update_one(
        {"_id": ObjectId(producto_id)}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    updated_producto = await collection.find_one({"_id": ObjectId(producto_id)})
    return convert_objectid(updated_producto)

@router.delete("/{producto_id}")
async def delete_producto(producto_id: str):
    """Eliminar un producto"""
    collection = await get_productos_collection()
    
    result = await collection.delete_one({"_id": ObjectId(producto_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return {"message": "Producto eliminado exitosamente"}

@router.get("/categoria/{categoria}", response_model=List[Producto])
async def get_productos_por_categoria(categoria: str):
    """Obtener productos por categoría"""
    collection = await get_productos_collection()
    productos = await collection.find({"categoria": categoria}).to_list(1000)
    return [convert_objectid(producto) for producto in productos]
