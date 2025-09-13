from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProgramaFidelidad(BaseModel):
    puntos: int = 0
    nivel: str = "Bronce"

class HistorialTransaccion(BaseModel):
    transaccion_id: str
    fecha: str

class Cliente(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    nombre: str
    email: str
    programa_fidelidad: ProgramaFidelidad = ProgramaFidelidad()
    historial: List[HistorialTransaccion] = []

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "C102",
                "nombre": "Ana Pérez",
                "email": "ana@example.com",
                "programa_fidelidad": {"puntos": 3200, "nivel": "Oro"},
                "historial": [
                    {"transaccion_id": "T56789", "fecha": "2024-09-12"}
                ]
            }
        }

class ClienteCreate(BaseModel):
    nombre: str
    email: str
    programa_fidelidad: Optional[ProgramaFidelidad] = ProgramaFidelidad()

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    programa_fidelidad: Optional[ProgramaFidelidad] = None
