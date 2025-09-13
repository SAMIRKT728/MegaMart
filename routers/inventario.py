from fastapi import APIRouter, HTTPException, status
from typing import List
from models.inventario import Inventario, InventarioCreate, InventarioUpdate, TransferenciaStock, AjusteStock
from database import get_inventario_collection, get_productos_collection
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter()

def convert_objectid(doc):
    """Convierte ObjectId a string en un documento"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("/", response_model=List[Inventario])
async def get_inventario():
    """Obtener todo el inventario"""
    collection = await get_inventario_collection()
    inventario = await collection.find().to_list(1000)
    return [convert_objectid(item) for item in inventario]

@router.get("/sucursal/{sucursal_id}", response_model=List[Inventario])
async def get_inventario_por_sucursal(sucursal_id: str):
    """Obtener inventario por sucursal"""
    collection = await get_inventario_collection()
    inventario = await collection.find({"sucursal_id": sucursal_id}).to_list(1000)
    return [convert_objectid(item) for item in inventario]

@router.get("/producto/{producto_id}", response_model=List[Inventario])
async def get_inventario_por_producto(producto_id: str):
    """Obtener inventario por producto"""
    collection = await get_inventario_collection()
    inventario = await collection.find({"producto_id": producto_id}).to_list(1000)
    return [convert_objectid(item) for item in inventario]

@router.post("/", response_model=Inventario, status_code=status.HTTP_201_CREATED)
async def create_inventario(inventario: InventarioCreate):
    """Crear registro de inventario"""
    collection = await get_inventario_collection()
    
    # Verificar si ya existe el registro
    existing = await collection.find_one({
        "sucursal_id": inventario.sucursal_id,
        "producto_id": inventario.producto_id
    })
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Ya existe un registro de inventario para este producto en esta sucursal"
        )
    
    inventario_dict = inventario.model_dump()
    inventario_dict["ultima_actualizacion"] = datetime.utcnow()
    
    result = await collection.insert_one(inventario_dict)
    
    if result.inserted_id:
        created_inventario = await collection.find_one({"_id": result.inserted_id})
        return convert_objectid(created_inventario)
    
    raise HTTPException(status_code=400, detail="Error al crear el registro de inventario")

@router.put("/sucursal/{sucursal_id}/producto/{producto_id}", response_model=Inventario)
async def update_inventario(sucursal_id: str, producto_id: str, inventario: InventarioUpdate):
    """Actualizar inventario"""
    collection = await get_inventario_collection()
    
    update_data = {k: v for k, v in inventario.model_dump().items() if v is not None}
    update_data["ultima_actualizacion"] = datetime.utcnow()
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    result = await collection.update_one(
        {"sucursal_id": sucursal_id, "producto_id": producto_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    
    updated_inventario = await collection.find_one({
        "sucursal_id": sucursal_id, 
        "producto_id": producto_id
    })
    return convert_objectid(updated_inventario)

@router.delete("/sucursal/{sucursal_id}/producto/{producto_id}")
async def delete_inventario(sucursal_id: str, producto_id: str):
    """Eliminar registro de inventario"""
    collection = await get_inventario_collection()
    
    result = await collection.delete_one({
        "producto_id": producto_id,
        "sucursal_id": sucursal_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    
    return {"message": "Registro de inventario eliminado exitosamente"}

@router.get("/disponibilidad/{codigo}")
async def verificar_disponibilidad(codigo: str):
    """Verificar stock en tiempo real"""
    inventario_collection = await get_inventario_collection()
    productos_collection = await get_productos_collection()
    
    producto = await productos_collection.find_one({"codigo": codigo})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto_id = str(producto["_id"])
    
    stock_sucursales = await inventario_collection.find({"producto_id": producto_id}).to_list(100)
    
    total_stock = sum(item["stock_actual"] for item in stock_sucursales)
    
    return {
        "producto_id": codigo,
        "nombre": producto["nombre"],
        "stock_total": total_stock,
        "stock_por_sucursal": [
            {
                "sucursal_id": item["sucursal_id"],
                "stock_actual": item["stock_actual"],
                "stock_minimo": item["stock_minimo"],
                "estado": "bajo" if item["stock_actual"] <= item["stock_minimo"] else "normal"
            }
            for item in stock_sucursales
        ],
        "disponible": total_stock > 0
    }

@router.post("/transferir")
async def transferir_stock(transferencia: TransferenciaStock):
    """Transferir stock entre sucursales"""
    collection = await get_inventario_collection()
    productos_collection = await get_productos_collection()
    
    producto = await productos_collection.find_one({"codigo": transferencia.producto_id})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto_id = str(producto["_id"])
    
    # Verificar stock en sucursal origen
    stock_origen = await collection.find_one({
        "producto_id": producto_id,
        "sucursal_id": transferencia.sucursal_origen
    })
    
    if not stock_origen:
        raise HTTPException(status_code=404, detail="Producto no encontrado en sucursal origen")
    
    if stock_origen["stock_actual"] < transferencia.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente en sucursal origen")
    
    # Verificar que existe registro en sucursal destino, si no existe lo creamos
    stock_destino = await collection.find_one({
        "producto_id": producto_id,
        "sucursal_id": transferencia.sucursal_destino
    })
    
    if not stock_destino:
        nuevo_registro = {
            "producto_id": producto_id,
            "sucursal_id": transferencia.sucursal_destino,
            "stock_actual": 0,
            "stock_minimo": 10,
            "stock_maximo": 1000,
            "ultima_actualizacion": datetime.utcnow()
        }
        await collection.insert_one(nuevo_registro)
    
    # Realizar transferencia
    await collection.update_one(
        {"producto_id": producto_id, "sucursal_id": transferencia.sucursal_origen},
        {
            "$inc": {"stock_actual": -transferencia.cantidad},
            "$set": {"ultima_actualizacion": datetime.utcnow()}
        }
    )
    
    await collection.update_one(
        {"producto_id": producto_id, "sucursal_id": transferencia.sucursal_destino},
        {
            "$inc": {"stock_actual": transferencia.cantidad},
            "$set": {"ultima_actualizacion": datetime.utcnow()}
        }
    )
    
    return {
        "message": "Transferencia realizada exitosamente",
        "transferencia": transferencia.model_dump()
    }

@router.get("/perecederos/vencimientos")
async def productos_proximos_vencer(dias: int = 7):
    """Productos próximos a vencer"""
    collection = await get_inventario_collection()
    productos_collection = await get_productos_collection()
    
    fecha_limite = datetime.utcnow() + timedelta(days=dias)
    
    inventario_perecedero = await collection.find({
        "fecha_vencimiento": {
            "$lte": fecha_limite, 
            "$gte": datetime.utcnow()
        }
    }).to_list(1000)
    
    productos_vencimiento = []
    for item in inventario_perecedero:
        # Buscar producto por ID
        try:
            if ObjectId.is_valid(item["producto_id"]):
                producto = await productos_collection.find_one({"_id": ObjectId(item["producto_id"])})
            else:
                producto = await productos_collection.find_one({"codigo": item["producto_id"]})
        except:
            producto = await productos_collection.find_one({"codigo": item["producto_id"]})
        
        if producto:
            fecha_venc = item.get("fecha_vencimiento")
            if fecha_venc:
                if isinstance(fecha_venc, str):
                    fecha_venc = datetime.fromisoformat(fecha_venc.replace('Z', '+00:00'))
                
                if fecha_venc <= fecha_limite and fecha_venc >= datetime.utcnow():
                    dias_restantes = (fecha_venc - datetime.utcnow()).days
                    productos_vencimiento.append({
                        "producto_id": item["producto_id"],
                        "codigo": producto.get("codigo", ""),
                        "nombre": producto["nombre"],
                        "sucursal_id": item["sucursal_id"],
                        "fecha_vencimiento": fecha_venc,
                        "dias_restantes": dias_restantes,
                        "stock_actual": item["stock_actual"]
                    })
    
    return productos_vencimiento

@router.put("/ajuste-stock")
async def ajustar_stock(ajuste: AjusteStock):
    """Ajustar inventario por pérdidas/mermas"""
    collection = await get_inventario_collection()
    productos_collection = await get_productos_collection()
    
    producto = await productos_collection.find_one({"codigo": ajuste.producto_id})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto_id = str(producto["_id"])
    
    # Verificar que existe el registro
    inventario = await collection.find_one({
        "producto_id": producto_id,
        "sucursal_id": ajuste.sucursal_id
    })
    
    if not inventario:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    
    nuevo_stock = inventario["stock_actual"] + ajuste.cantidad_ajuste
    
    if nuevo_stock < 0:
        raise HTTPException(status_code=400, detail="El ajuste resultaría en stock negativo")
    
    # Registrar el ajuste
    ajuste_registro = {
        "fecha": datetime.utcnow(),
        "cantidad_anterior": inventario["stock_actual"],
        "ajuste": ajuste.cantidad_ajuste,
        "cantidad_nueva": nuevo_stock,
        "motivo": ajuste.motivo,
        "tipo": ajuste.tipo_ajuste,
        "autorizado_por": ajuste.autorizado_por
    }
    
    # Actualizar inventario
    await collection.update_one(
        {"producto_id": producto_id, "sucursal_id": ajuste.sucursal_id},
        {
            "$set": {
                "stock_actual": nuevo_stock,
                "ultima_actualizacion": datetime.utcnow()
            },
            "$push": {"ajustes": ajuste_registro}
        }
    )
    
    return {
        "message": "Ajuste de stock realizado exitosamente",
        "stock_anterior": inventario["stock_actual"],
        "stock_nuevo": nuevo_stock,
        "ajuste": ajuste_registro
    }
