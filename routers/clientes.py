from fastapi import APIRouter, HTTPException, status
from typing import List
from models.clientes import Cliente, ClienteCreate, ClienteUpdate
from database import get_clientes_collection
import uuid
from bson import ObjectId

router = APIRouter()

def convert_objectid(doc):
    """Convierte ObjectId a string en un documento"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [convert_objectid(item) for item in doc]
    if isinstance(doc, dict):
        converted = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                converted[key] = str(value)
            elif isinstance(value, dict):
                converted[key] = convert_objectid(value)
            elif isinstance(value, list):
                converted[key] = convert_objectid(value)
            else:
                converted[key] = value
        return converted
    return doc

@router.get("/", response_model=List[Cliente])
async def get_clientes():
    """Obtener todos los clientes"""
    collection = await get_clientes_collection()
    clientes = await collection.find().to_list(1000)
    return convert_objectid(clientes)

@router.get("/{cliente_id}", response_model=Cliente)
async def get_cliente(cliente_id: str):
    """Obtener un cliente por ID"""
    collection = await get_clientes_collection()
    cliente = await collection.find_one({"_id": cliente_id})
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return convert_objectid(cliente)

@router.get("/email/{email}", response_model=Cliente)
async def get_cliente_por_email(email: str):
    """Obtener un cliente por email"""
    collection = await get_clientes_collection()
    cliente = await collection.find_one({"email": email})
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return convert_objectid(cliente)

@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
async def create_cliente(cliente: ClienteCreate):
    """Crear un nuevo cliente"""
    collection = await get_clientes_collection()
    
    # Verificar si el email ya existe
    existing_cliente = await collection.find_one({"email": cliente.email})
    if existing_cliente:
        raise HTTPException(status_code=400, detail="Ya existe un cliente con este email")
    
    # Generar ID único
    cliente_id = f"C{str(uuid.uuid4())[:8].upper()}"
    
    cliente_dict = cliente.model_dump()
    cliente_dict["_id"] = cliente_id
    
    result = await collection.insert_one(cliente_dict)
    
    if result.inserted_id:
        created_cliente = await collection.find_one({"_id": cliente_id})
        return convert_objectid(created_cliente)
    
    raise HTTPException(status_code=400, detail="Error al crear el cliente")

@router.put("/{cliente_id}", response_model=Cliente)
async def update_cliente(cliente_id: str, cliente: ClienteUpdate):
    """Actualizar un cliente"""
    collection = await get_clientes_collection()
    
    update_data = {k: v for k, v in cliente.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    # Si se está actualizando el email, verificar que no exista
    if "email" in update_data:
        existing_cliente = await collection.find_one({
            "email": update_data["email"],
            "_id": {"$ne": cliente_id}
        })
        if existing_cliente:
            raise HTTPException(status_code=400, detail="Ya existe un cliente con este email")
    
    result = await collection.update_one(
        {"_id": cliente_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    updated_cliente = await collection.find_one({"_id": cliente_id})
    return convert_objectid(updated_cliente)

@router.delete("/{cliente_id}")
async def delete_cliente(cliente_id: str):
    """Eliminar un cliente"""
    collection = await get_clientes_collection()
    
    result = await collection.delete_one({"_id": cliente_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return {"message": "Cliente eliminado exitosamente"}

@router.post("/{cliente_id}/puntos")
async def actualizar_puntos_cliente(cliente_id: str, puntos: int):
    """Actualizar puntos del programa de fidelidad"""
    collection = await get_clientes_collection()
    
    # Obtener cliente actual
    cliente = await collection.find_one({"_id": cliente_id})
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Calcular nuevos puntos
    puntos_actuales = cliente.get("programa_fidelidad", {}).get("puntos", 0)
    nuevos_puntos = puntos_actuales + puntos
    
    # Determinar nuevo nivel
    if nuevos_puntos >= 5000:
        nivel = "Platino"
    elif nuevos_puntos >= 3000:
        nivel = "Oro"
    elif nuevos_puntos >= 1000:
        nivel = "Plata"
    else:
        nivel = "Bronce"
    
    # Actualizar cliente
    result = await collection.update_one(
        {"_id": cliente_id},
        {"$set": {
            "programa_fidelidad.puntos": nuevos_puntos,
            "programa_fidelidad.nivel": nivel
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    updated_cliente = await collection.find_one({"_id": cliente_id})
    return convert_objectid(updated_cliente)
