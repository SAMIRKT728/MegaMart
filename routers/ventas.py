from fastapi import APIRouter, HTTPException, status
from typing import List
from models.ventas import (
    TransaccionVenta, IniciarTransaccionRequest, AgregarProductoRequest,
    AplicarPromocionRequest, FinalizarVentaRequest, ProductoCarrito,
    PromocionAplicada, EstadoTransaccion
)
from database import get_transacciones_collection, get_productos_collection, get_inventario_collection
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/iniciar-transaccion", response_model=TransaccionVenta, status_code=status.HTTP_201_CREATED)
async def iniciar_transaccion(request: IniciarTransaccionRequest):
    """Iniciar nueva venta"""
    collection = await get_transacciones_collection()
    
    transaccion_id = f"T{uuid.uuid4().hex[:8].upper()}"
    
    nueva_transaccion = TransaccionVenta(
        transaccion_id=transaccion_id,
        cliente_id=request.cliente_id,
        sucursal_id=request.sucursal_id
    )
    
    result = await collection.insert_one(nueva_transaccion.model_dump())
    
    if result.inserted_id:
        return nueva_transaccion
    
    raise HTTPException(status_code=400, detail="Error al iniciar la transacción")

@router.post("/agregar-producto/{transaccion_id}")
async def agregar_producto(transaccion_id: str, request: AgregarProductoRequest):
    """Agregar producto al carrito"""
    transacciones_collection = await get_transacciones_collection()
    productos_collection = await get_productos_collection()
    inventario_collection = await get_inventario_collection()
    
    # Verificar que la transacción existe y está activa
    transaccion = await transacciones_collection.find_one({"transaccion_id": transaccion_id})
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    if transaccion["estado"] != EstadoTransaccion.INICIADA:
        raise HTTPException(status_code=400, detail="La transacción no está activa")
    
    producto = await productos_collection.find_one({"codigo": request.producto_id})
    if not producto:
        raise HTTPException(status_code=404, detail=f"Producto con código {request.producto_id} no encontrado")
    
    producto_id = str(producto["_id"])
    
    inventario = await inventario_collection.find_one({
        "producto_id": producto_id,
        "sucursal_id": transaccion["sucursal_id"]
    })
    
    if not inventario:
        raise HTTPException(status_code=400, detail="Producto no disponible en esta sucursal")
    
    if inventario["stock_actual"] < request.cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {inventario['stock_actual']}")
    
    # Crear producto para el carrito
    producto_carrito = ProductoCarrito(
        producto_id=request.producto_id,  # Usar el código original
        cantidad=request.cantidad,
        precio_unitario=producto["precio"],
        subtotal=producto["precio"] * request.cantidad
    )
    
    # Actualizar transacción
    productos_actuales = transaccion.get("productos", [])
    productos_actuales.append(producto_carrito.model_dump())
    
    nuevo_subtotal = sum(p["subtotal"] for p in productos_actuales)
    nuevo_total = nuevo_subtotal - transaccion.get("descuento_total", 0)
    
    await transacciones_collection.update_one(
        {"transaccion_id": transaccion_id},
        {
            "$set": {
                "productos": productos_actuales,
                "subtotal": nuevo_subtotal,
                "total": nuevo_total
            }
        }
    )
    
    return {
        "message": "Producto agregado al carrito", 
        "producto": producto["nombre"],
        "subtotal": nuevo_subtotal, 
        "total": nuevo_total
    }

@router.post("/aplicar-promocion/{transaccion_id}")
async def aplicar_promocion(transaccion_id: str, request: AplicarPromocionRequest):
    """Validar y aplicar descuentos"""
    collection = await get_transacciones_collection()
    
    transaccion = await collection.find_one({"transaccion_id": transaccion_id})
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    # Simulación de validación de promoción
    promociones_validas = {
        "DESC10": {"tipo": "porcentaje", "descuento": 0.10, "descripcion": "10% de descuento"},
        "DESC20": {"tipo": "porcentaje", "descuento": 0.20, "descripcion": "20% de descuento"},
        "FIJO50": {"tipo": "fijo", "descuento": 50.0, "descripcion": "$50 de descuento"}
    }
    
    if request.codigo_promocion not in promociones_validas:
        raise HTTPException(status_code=400, detail="Código de promoción inválido")
    
    promo_data = promociones_validas[request.codigo_promocion]
    
    # Calcular descuento
    subtotal = transaccion.get("subtotal", 0)
    if promo_data["tipo"] == "porcentaje":
        descuento = subtotal * promo_data["descuento"]
    else:
        descuento = min(promo_data["descuento"], subtotal)
    
    promocion = PromocionAplicada(
        promocion_id=request.codigo_promocion,
        tipo=promo_data["tipo"],
        descuento=descuento,
        descripcion=promo_data["descripcion"]
    )
    
    promociones_actuales = transaccion.get("promociones", [])
    promociones_actuales.append(promocion.model_dump())
    
    descuento_total = sum(p["descuento"] for p in promociones_actuales)
    nuevo_total = subtotal - descuento_total
    
    await collection.update_one(
        {"transaccion_id": transaccion_id},
        {
            "$set": {
                "promociones": promociones_actuales,
                "descuento_total": descuento_total,
                "total": max(0, nuevo_total)
            }
        }
    )
    
    return {"message": "Promoción aplicada", "descuento": descuento, "total": max(0, nuevo_total)}

@router.post("/finalizar/{transaccion_id}")
async def finalizar_venta(transaccion_id: str, request: FinalizarVentaRequest):
    """Procesar pago y finalizar venta"""
    transacciones_collection = await get_transacciones_collection()
    inventario_collection = await get_inventario_collection()
    
    transaccion = await transacciones_collection.find_one({"transaccion_id": transaccion_id})
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    if transaccion["estado"] != EstadoTransaccion.INICIADA:
        raise HTTPException(status_code=400, detail="La transacción ya fue procesada")
    
    # Actualizar inventario
    for producto in transaccion.get("productos", []):
        await inventario_collection.update_one(
            {
                "producto_id": producto["producto_id"],
                "sucursal_id": transaccion["sucursal_id"]
            },
            {
                "$inc": {"stock_actual": -producto["cantidad"]},
                "$set": {"ultima_actualizacion": datetime.utcnow()}
            }
        )
    
    # Finalizar transacción
    await transacciones_collection.update_one(
        {"transaccion_id": transaccion_id},
        {
            "$set": {
                "estado": EstadoTransaccion.FINALIZADA,
                "fecha_finalizacion": datetime.utcnow(),
                "metodo_pago": request.metodo_pago,
                "monto_recibido": request.monto_recibido
            }
        }
    )
    
    return {"message": "Venta finalizada exitosamente", "transaccion_id": transaccion_id}
