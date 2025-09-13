from fastapi import APIRouter, HTTPException, status
from typing import List
from models.transacciones import Transaccion, TransaccionCreate, TransaccionUpdate
from database import get_transacciones_collection
import uuid
from datetime import datetime
from bson import ObjectId

router = APIRouter()

def convert_objectid(doc):
    """Convierte ObjectId a string y ajusta estructura de datos"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    
    if doc and "productos" in doc:
        for producto in doc["productos"]:
            if "precio_unitario" in producto:
                # Convertir precio_unitario objeto a precio_unit float
                if isinstance(producto["precio_unitario"], dict):
                    producto["precio_unit"] = producto["precio_unitario"]["base"]
                else:
                    producto["precio_unit"] = producto["precio_unitario"]
                del producto["precio_unitario"]
            
            # Remover campos que no están en el modelo
            if "subtotal" in producto:
                del producto["subtotal"]
    
    if doc and "total" in doc and isinstance(doc["total"], dict):
        doc["total"] = doc["total"]["base"]
    
    if doc and "metodo_pago" in doc:
        if isinstance(doc["metodo_pago"], str):
            doc["metodo_pago"] = [doc["metodo_pago"]]
    else:
        # Si no existe metodo_pago, asignar None para transacciones iniciadas
        doc["metodo_pago"] = None
    
    return doc

@router.get("/", response_model=List[Transaccion])
async def get_transacciones():
    """Obtener todas las transacciones"""
    collection = await get_transacciones_collection()
    transacciones = await collection.find().to_list(1000)
    return [convert_objectid(t) for t in transacciones]

@router.get("/{transaccion_id}", response_model=Transaccion)
async def get_transaccion(transaccion_id: str):
    """Obtener una transacción por ID"""
    collection = await get_transacciones_collection()
    transaccion = await collection.find_one({"_id": ObjectId(transaccion_id)})
    if transaccion is None:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return convert_objectid(transaccion)

@router.get("/cliente/{cliente_id}", response_model=List[Transaccion])
async def get_transacciones_por_cliente(cliente_id: str):
    """Obtener transacciones por cliente"""
    collection = await get_transacciones_collection()
    transacciones = await collection.find({"cliente_id": cliente_id}).to_list(1000)
    return [convert_objectid(t) for t in transacciones]

@router.get("/sucursal/{sucursal_id}", response_model=List[Transaccion])
async def get_transacciones_por_sucursal(sucursal_id: str):
    """Obtener transacciones por sucursal"""
    collection = await get_transacciones_collection()
    transacciones = await collection.find({"sucursal_id": sucursal_id}).to_list(1000)
    return [convert_objectid(t) for t in transacciones]

@router.post("/", response_model=Transaccion, status_code=status.HTTP_201_CREATED)
async def create_transaccion(transaccion: TransaccionCreate):
    """Crear una nueva transacción"""
    collection = await get_transacciones_collection()
    
    # Generar ID único
    transaccion_id = f"T{str(uuid.uuid4())[:8].upper()}"
    
    transaccion_dict = transaccion.model_dump()
    transaccion_dict["_id"] = ObjectId(transaccion_id)
    transaccion_dict["fecha"] = datetime.utcnow()
    
    result = await collection.insert_one(transaccion_dict)
    
    if result.inserted_id:
        created_transaccion = await collection.find_one({"_id": result.inserted_id})
        return convert_objectid(created_transaccion)
    
    raise HTTPException(status_code=400, detail="Error al crear la transacción")

@router.put("/{transaccion_id}", response_model=Transaccion)
async def update_transaccion(transaccion_id: str, transaccion: TransaccionUpdate):
    """Actualizar una transacción"""
    collection = await get_transacciones_collection()
    
    update_data = {k: v for k, v in transaccion.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = await collection.update_one(
        {"_id": ObjectId(transaccion_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    updated_transaccion = await collection.find_one({"_id": ObjectId(transaccion_id)})
    return convert_objectid(updated_transaccion)

@router.delete("/{transaccion_id}")
async def delete_transaccion(transaccion_id: str):
    """Eliminar una transacción"""
    collection = await get_transacciones_collection()
    
    result = await collection.delete_one({"_id": ObjectId(transaccion_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    return {"message": "Transacción eliminada exitosamente"}
