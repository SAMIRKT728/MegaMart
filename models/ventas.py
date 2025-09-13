from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class EstadoTransaccion(str, Enum):
    INICIADA = "iniciada"
    EN_PROCESO = "en_proceso"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"

class ProductoCarrito(BaseModel):
    producto_id: str
    cantidad: int
    precio_unitario: float
    descuento_aplicado: float = 0.0
    subtotal: float

class PromocionAplicada(BaseModel):
    promocion_id: str
    tipo: str
    descuento: float
    descripcion: str

class TransaccionVenta(BaseModel):
    transaccion_id: str
    cliente_id: Optional[str] = None
    sucursal_id: str
    productos: List[ProductoCarrito] = []
    promociones: List[PromocionAplicada] = []
    subtotal: float = 0.0
    descuento_total: float = 0.0
    total: float = 0.0
    estado: EstadoTransaccion = EstadoTransaccion.INICIADA
    fecha_inicio: datetime = Field(default_factory=datetime.utcnow)
    fecha_finalizacion: Optional[datetime] = None

class IniciarTransaccionRequest(BaseModel):
    cliente_id: Optional[str] = None
    sucursal_id: str

class AgregarProductoRequest(BaseModel):
    producto_id: str
    cantidad: int

class AplicarPromocionRequest(BaseModel):
    codigo_promocion: str

class FinalizarVentaRequest(BaseModel):
    metodo_pago: str
    monto_recibido: Optional[float] = None

class TransferenciaStock(BaseModel):
    producto_id: str
    sucursal_origen: str
    sucursal_destino: str
    cantidad: int
    motivo: str
    autorizado_por: str

class AjusteStock(BaseModel):
    producto_id: str
    sucursal_id: str
    cantidad_ajuste: int  # Positivo para aumentar, negativo para disminuir
    motivo: str
    tipo_ajuste: str  # "perdida", "merma", "correccion", "devolucion"
    autorizado_por: str
