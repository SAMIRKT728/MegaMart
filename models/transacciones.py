from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProductoTransaccion(BaseModel):
    producto_id: str
    cantidad: int
    precio_unit: float
    descuento: float = 0

class Transaccion(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    sucursal_id: str
    fecha: datetime = Field(default_factory=datetime.utcnow)
    cliente_id: str
    productos: List[ProductoTransaccion]
    total: float
    metodo_pago: List[str]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "T56789",
                "sucursal_id": "S01",
                "fecha": "2024-09-12T19:05:00Z",
                "cliente_id": "C102",
                "productos": [
                    {"producto_id": "P12345", "cantidad": 2, "precio_unit": 4000, "descuento": 2000}
                ],
                "total": 6000,
                "metodo_pago": ["tarjeta", "puntos"]
            }
        }

class TransaccionCreate(BaseModel):
    sucursal_id: str
    cliente_id: str
    productos: List[ProductoTransaccion]
    total: float
    metodo_pago: List[str]

class TransaccionUpdate(BaseModel):
    productos: Optional[List[ProductoTransaccion]] = None
    total: Optional[float] = None
    metodo_pago: Optional[List[str]] = None
