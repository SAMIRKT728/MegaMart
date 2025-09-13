from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class VentaTiempoReal(BaseModel):
    ventas_hoy: float
    transacciones_hoy: int
    ticket_promedio: float
    productos_vendidos: int
    comparacion_ayer: Dict[str, float]

class ProductoTrending(BaseModel):
    producto_id: str
    nombre: str
    cantidad_vendida: int
    ingresos: float
    crecimiento_porcentaje: float

class PrediccionDemanda(BaseModel):
    producto_id: str
    demanda_estimada_7_dias: int
    demanda_estimada_30_dias: int
    tendencia: str  # "creciente", "decreciente", "estable"
    confianza: float  # 0-1
    factores: List[str]

class RecomendacionProducto(BaseModel):
    producto_id: str
    nombre: str
    score_recomendacion: float
    razon: str
    precio: float
