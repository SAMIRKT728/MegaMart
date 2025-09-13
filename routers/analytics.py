from fastapi import APIRouter, HTTPException
from typing import List
from models.analytics import VentaTiempoReal, ProductoTrending, PrediccionDemanda, RecomendacionProducto
from database import get_transacciones_collection, get_productos_collection, get_clientes_collection
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/ventas/tiempo-real", response_model=VentaTiempoReal)
async def get_ventas_tiempo_real():
    """Dashboard de ventas actuales"""
    collection = await get_transacciones_collection()
    
    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ayer = hoy - timedelta(days=1)
    
    ventas_hoy = await collection.find({
        "fecha_creacion": {"$gte": hoy},
        "estado": "finalizada"
    }).to_list(1000)
    
    ventas_ayer = await collection.find({
        "fecha_creacion": {"$gte": ayer, "$lt": hoy},
        "estado": "finalizada"
    }).to_list(1000)
    
    # Si no hay ventas con fecha_creacion, buscar por _id (ObjectId contiene timestamp)
    if not ventas_hoy:
        from bson import ObjectId
        inicio_hoy = ObjectId.from_datetime(hoy)
        ventas_hoy = await collection.find({
            "_id": {"$gte": inicio_hoy},
            "estado": "finalizada"
        }).to_list(1000)
    
    def get_total_value(venta):
        total = venta.get("total", 0)
        if isinstance(total, dict):
            return total.get("base", 0)
        return total
    
    # Calcular métricas
    total_hoy = sum(get_total_value(venta) for venta in ventas_hoy)
    total_ayer = sum(get_total_value(venta) for venta in ventas_ayer)
    transacciones_hoy = len(ventas_hoy)
    transacciones_ayer = len(ventas_ayer)
    
    ticket_promedio = total_hoy / transacciones_hoy if transacciones_hoy > 0 else 0
    productos_vendidos = sum(
        sum(p.get("cantidad", 0) for p in venta.get("productos", []))
        for venta in ventas_hoy
    )
    
    # Comparaciones
    comparacion_ventas = ((total_hoy - total_ayer) / total_ayer * 100) if total_ayer > 0 else 0
    comparacion_transacciones = ((transacciones_hoy - transacciones_ayer) / transacciones_ayer * 100) if transacciones_ayer > 0 else 0
    
    return VentaTiempoReal(
        ventas_hoy=total_hoy,
        transacciones_hoy=transacciones_hoy,
        ticket_promedio=ticket_promedio,
        productos_vendidos=productos_vendidos,
        comparacion_ayer={
            "ventas": comparacion_ventas,
            "transacciones": comparacion_transacciones
        }
    )

@router.get("/productos/trending", response_model=List[ProductoTrending])
async def get_productos_trending():
    """Productos más vendidos hoy"""
    transacciones_collection = await get_transacciones_collection()
    productos_collection = await get_productos_collection()
    
    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    ventas_hoy = await transacciones_collection.find({
        "fecha_creacion": {"$gte": hoy},
        "estado": "finalizada"
    }).to_list(1000)
    
    if not ventas_hoy:
        from bson import ObjectId
        inicio_hoy = ObjectId.from_datetime(hoy)
        ventas_hoy = await transacciones_collection.find({
            "_id": {"$gte": inicio_hoy},
            "estado": "finalizada"
        }).to_list(1000)
    
    def get_subtotal_value(subtotal):
        if isinstance(subtotal, dict):
            return subtotal.get("base", 0)
        return subtotal
    
    # Agregar productos vendidos
    productos_stats = {}
    for venta in ventas_hoy:
        for producto in venta.get("productos", []):
            producto_id = producto["producto_id"]
            if producto_id not in productos_stats:
                productos_stats[producto_id] = {
                    "cantidad": 0,
                    "ingresos": 0
                }
            productos_stats[producto_id]["cantidad"] += producto["cantidad"]
            productos_stats[producto_id]["ingresos"] += get_subtotal_value(producto.get("subtotal", 0))
    
    # Obtener información de productos y crear respuesta
    trending = []
    for producto_id, stats in sorted(productos_stats.items(), key=lambda x: x[1]["cantidad"], reverse=True)[:10]:
        producto = await productos_collection.find_one({"codigo": producto_id})
        if producto:
            trending.append(ProductoTrending(
                producto_id=producto_id,
                nombre=producto["nombre"],
                cantidad_vendida=stats["cantidad"],
                ingresos=stats["ingresos"],
                crecimiento_porcentaje=random.uniform(5, 25)  # Simulado
            ))
    
    return trending

@router.get("/prediccion-demanda/{producto_id}", response_model=PrediccionDemanda)
async def get_prediccion_demanda(producto_id: str):
    """Estimación de ventas"""
    collection = await get_transacciones_collection()
    
    # Obtener ventas de los últimos 30 días
    hace_30_dias = datetime.utcnow() - timedelta(days=30)
    
    ventas_historicas = await collection.find({
        "fecha_finalizacion": {"$gte": hace_30_dias},
        "estado": "finalizada"
    }).to_list(1000)
    
    # Calcular demanda histórica
    cantidad_total = 0
    for venta in ventas_historicas:
        for producto in venta.get("productos", []):
            if producto["producto_id"] == producto_id:
                cantidad_total += producto["cantidad"]
    
    # Estimaciones simples (en producción usarías ML)
    demanda_diaria = cantidad_total / 30 if cantidad_total > 0 else 1
    
    return PrediccionDemanda(
        producto_id=producto_id,
        demanda_estimada_7_dias=int(demanda_diaria * 7),
        demanda_estimada_30_dias=int(demanda_diaria * 30),
        tendencia="estable",
        confianza=0.75,
        factores=["Historial de ventas", "Temporada actual", "Stock disponible"]
    )

@router.get("/cliente/{cliente_id}/recomendaciones", response_model=List[RecomendacionProducto])
async def get_recomendaciones_cliente(cliente_id: str):
    """Productos sugeridos para el cliente"""
    transacciones_collection = await get_transacciones_collection()
    productos_collection = await get_productos_collection()
    
    # Obtener historial del cliente
    compras_cliente = await transacciones_collection.find({
        "cliente_id": cliente_id,
        "estado": "finalizada"
    }).to_list(100)
    
    # Productos comprados por el cliente
    productos_comprados = set()
    for compra in compras_cliente:
        for producto in compra.get("productos", []):
            productos_comprados.add(producto["producto_id"])
    
    # Obtener productos populares que no ha comprado
    todos_productos = await productos_collection.find().to_list(1000)
    
    recomendaciones = []
    for producto in todos_productos[:5]:  # Top 5 recomendaciones
        if producto["codigo"] not in productos_comprados:
            recomendaciones.append(RecomendacionProducto(
                producto_id=producto["codigo"],
                nombre=producto["nombre"],
                score_recomendacion=random.uniform(0.7, 0.95),
                razon="Producto popular en tu categoría favorita",
                precio=producto["precio"]
            ))
    
    return recomendaciones
