from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Precio(BaseModel):
    base: float
    moneda: str = "COP"

class Variante(BaseModel):
    tamaño: str
    codigo_barras: str

class Lote(BaseModel):
    lote_id: str
    fecha_venc: str
    stock: int

class Promocion(BaseModel):
    tipo: str
    vigencia: dict

class Producto(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    nombre: str
    categoria: str
    precio: Precio
    variantes: List[Variante] = []
    perecedero: bool = False
    lotes: List[Lote] = []
    promociones: List[Promocion] = []

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "P12345",
                "nombre": "Leche Entera 1L",
                "categoria": "Lácteos",
                "precio": {"base": 4000, "moneda": "COP"},
                "variantes": [
                    {"tamaño": "1L", "codigo_barras": "7701234567"}
                ],
                "perecedero": True,
                "lotes": [
                    {"lote_id": "L987", "fecha_venc": "2024-09-30", "stock": 200}
                ],
                "promociones": [
                    {"tipo": "3x2", "vigencia": {"inicio": "2024-09-10", "fin": "2024-09-20"}}
                ]
            }
        }

class ProductoCreate(BaseModel):
    nombre: str
    categoria: str
    precio: Precio
    variantes: List[Variante] = []
    perecedero: bool = False
    lotes: List[Lote] = []
    promociones: List[Promocion] = []

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    precio: Optional[Precio] = None
    variantes: Optional[List[Variante]] = None
    perecedero: Optional[bool] = None
    lotes: Optional[List[Lote]] = None
    promociones: Optional[List[Promocion]] = None
