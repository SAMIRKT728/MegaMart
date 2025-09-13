from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Crear conexión a MongoDB Atlas"""
    # URL de conexión a MongoDB Atlas (puedes cambiarla por tu configuración)
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://kicristian250:980619casn@cluster0.zednc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "sistema_inventario")
    
    # Configuración adicional para MongoDB Atlas
    db.client = AsyncIOMotorClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,  # Timeout de 5 segundos
        connectTimeoutMS=10000,         # Timeout de conexión de 10 segundos
        socketTimeoutMS=10000           # Timeout de socket de 10 segundos
    )
    
    # Verificar la conexión
    try:
        await db.client.admin.command('ping')
        db.database = db.client[DATABASE_NAME]
        print(f"✅ Conectado exitosamente a MongoDB Atlas: {DATABASE_NAME}")
    except Exception as e:
        print(f"❌ Error conectando a MongoDB Atlas: {e}")
        raise e

async def close_mongo_connection():
    """Cerrar conexión a MongoDB"""
    if db.client:
        db.client.close()
        print("Conexión a MongoDB cerrada")

# Funciones helper para obtener colecciones
async def get_productos_collection():
    database = await get_database()
    return database.productos

async def get_inventario_collection():
    database = await get_database()
    return database.inventario

async def get_transacciones_collection():
    database = await get_database()
    return database.transacciones

async def get_clientes_collection():
    database = await get_database()
    return database.clientes
