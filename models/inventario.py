from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class Lote(BaseModel):
    numero_lote: str
    cantidad: int
    fecha_vencimiento: Optional[datetime] = None
    precio_compra: Optional[float] = None

class AjusteHistorial(BaseModel):
    fecha: datetime
    cantidad_anterior: int
    ajuste: int
    cantidad_nueva: int
    motivo: str
    tipo: str
    autorizado_por: str

class Inventario(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "sucursal_id": "S01",
                "producto_id": "P12345",
                "stock_actual": 120,
                "stock_minimo": 10,
                "stock_reservado": 10,
                "lotes": [
                    {
                        "numero_lote": "L001",
                        "cantidad": 50,
                        "fecha_vencimiento": "2024-12-31T00:00:00Z",
                        "precio_compra": 15.50
                    }
                ],
                "ultima_actualizacion": "2024-09-12T14:32:00Z"
            }
        }
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    sucursal_id: str
    producto_id: str
    stock_actual: int = Field(alias="stock")
    stock_minimo: int = 10
    stock_reservado: int = 0
    lotes: List[Lote] = []
    ajustes: List[AjusteHistorial] = []
    ultima_actualizacion: datetime = Field(default_factory=datetime.utcnow)

class InventarioCreate(BaseModel):
    sucursal_id: str
    producto_id: str
    stock_actual: int
    stock_minimo: int = 10
    stock_reservado: int = 0
    lotes: List[Lote] = []

class InventarioUpdate(BaseModel):
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None
    stock_reservado: Optional[int] = None
    lotes: Optional[List[Lote]] = None

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
