from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from contextlib import asynccontextmanager

from routers import productos, inventario, transacciones, clientes, ventas, analytics
from database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Sistema de Inventario API",
    description="API para gestión de productos, inventario, transacciones, clientes, ventas y analytics",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(productos.router, prefix="/api/v1/productos", tags=["productos"])
app.include_router(inventario.router, prefix="/api/v1/inventario", tags=["inventario"])
app.include_router(transacciones.router, prefix="/api/v1/transacciones", tags=["transacciones"])
app.include_router(clientes.router, prefix="/api/v1/clientes", tags=["clientes"])
app.include_router(ventas.router, prefix="/api/ventas", tags=["ventas"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Sistema de Inventario API - FastAPI + MongoDB"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
