"""
Script para poblar la base de datos con datos de ejemplo
Compatible con MongoDB Atlas
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os

# Configuración de la base de datos
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://kicristian250:980619casn@cluster0.zednc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sistema_inventario")

async def seed_database():
    """Poblar la base de datos con datos de ejemplo"""
    client = AsyncIOMotorClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    
    try:
        await client.admin.command('ping')
        print(f"✅ Conectado exitosamente a MongoDB Atlas")
        
        db = client[DATABASE_NAME]
        print(f"📊 Usando base de datos: {DATABASE_NAME}")
        print("🚀 Iniciando población de la base de datos...")
        
        productos_data = [
            {
                "codigo": "LECHE001",
                "nombre": "Leche Entera 1L",
                "categoria": "Lácteos",
                "precio": {"base": 4000, "moneda": "COP"},
                "descripcion": "Leche entera pasteurizada",
                "activo": True,
                "fecha_creacion": datetime.utcnow(),
                "variantes": [],
                "perecedero": True,
                "lotes": [],
                "promociones": []
            },
            {
                "codigo": "PAN001", 
                "nombre": "Pan Integral",
                "categoria": "Panadería",
                "precio": {"base": 3500, "moneda": "COP"},
                "descripcion": "Pan integral artesanal",
                "activo": True,
                "fecha_creacion": datetime.utcnow(),
                "variantes": [],
                "perecedero": True,
                "lotes": [],
                "promociones": []
            },
            {
                "codigo": "ARROZ001",
                "nombre": "Arroz Blanco 1kg",
                "categoria": "Granos",
                "precio": {"base": 2800, "moneda": "COP"},
                "descripcion": "Arroz blanco premium",
                "activo": True,
                "fecha_creacion": datetime.utcnow(),
                "variantes": [],
                "perecedero": False,
                "lotes": [],
                "promociones": []
            },
            {
                "codigo": "ACEITE001",
                "nombre": "Aceite de Girasol 1L",
                "categoria": "Aceites",
                "precio": {"base": 5200, "moneda": "COP"},
                "descripcion": "Aceite de girasol refinado",
                "activo": True,
                "fecha_creacion": datetime.utcnow(),
                "variantes": [],
                "perecedero": False,
                "lotes": [],
                "promociones": []
            },
            {
                "codigo": "YOGURT001",
                "nombre": "Yogurt Natural 200ml",
                "categoria": "Lácteos", 
                "precio": {"base": 2100, "moneda": "COP"},
                "descripcion": "Yogurt natural sin azúcar",
                "activo": True,
                "fecha_creacion": datetime.utcnow(),
                "variantes": [],
                "perecedero": True,
                "lotes": [],
                "promociones": []
            }
        ]
        
        # Insertar productos primero
        print("📦 Insertando productos...")
        await db.productos.delete_many({})
        result = await db.productos.insert_many(productos_data)
        print(f"✅ Insertados {len(result.inserted_ids)} productos")
        
        # Obtener los IDs de los productos insertados
        productos_insertados = await db.productos.find().to_list(100)
        producto_ids = {p["codigo"]: str(p["_id"]) for p in productos_insertados}
        
        inventario_data = [
            # Sucursal S01
            {
                "producto_id": producto_ids["LECHE001"],
                "sucursal_id": "S01",
                "stock_actual": 120,
                "stock_minimo": 20,
                "stock_maximo": 200,
                "fecha_vencimiento": datetime.utcnow() + timedelta(days=5),  # Próximo a vencer
                "ultima_actualizacion": datetime.utcnow(),
                "ajustes": []
            },
            {
                "producto_id": producto_ids["PAN001"],
                "sucursal_id": "S01", 
                "stock_actual": 45,
                "stock_minimo": 10,
                "stock_maximo": 100,
                "fecha_vencimiento": datetime.utcnow() + timedelta(days=2),  # Próximo a vencer
                "ultima_actualizacion": datetime.utcnow(),
                "ajustes": []
            },
            {
                "producto_id": producto_ids["ARROZ001"],
                "sucursal_id": "S01",
                "stock_actual": 280,
                "stock_minimo": 50,
                "stock_maximo": 500,
                "fecha_vencimiento": datetime.utcnow() + timedelta(days=365),
                "ultima_actualizacion": datetime.utcnow(),
                "ajustes": []
            },
            {
                "producto_id": producto_ids["ACEITE001"],
                "sucursal_id": "S01",
                "stock_actual": 75,
                "stock_minimo": 15,
                "stock_maximo": 150,
                "fecha_vencimiento": datetime.utcnow() + timedelta(days=180),
                "ultima_actualizacion": datetime.utcnow(),
                "ajustes": []
            },
            # Sucursal S02
            {
                "producto_id": producto_ids["LECHE001"],
                "sucursal_id": "S02",
                "stock_actual": 80,
                "stock_minimo": 20,
                "stock_maximo": 200,
                "fecha_vencimiento": datetime.utcnow() + timedelta(days=7),
                "ultima_actualizacion": datetime.utcnow(),
                "ajustes": []
            },
            {
                "producto_id": producto_ids["YOGURT001"],
                "sucursal_id": "S02",
                "stock_actual": 35,
                "stock_minimo": 10,
                "stock_maximo": 80,
                "fecha_vencimiento": datetime.utcnow() + timedelta(days=3),  # Próximo a vencer
                "ultima_actualizacion": datetime.utcnow(),
                "ajustes": []
            },
            # Sucursal S03
            {
                "producto_id": producto_ids["ARROZ001"],
                "sucursal_id": "S03",
                "stock_actual": 150,
                "stock_minimo": 50,
                "stock_maximo": 300,
                "fecha_vencimiento": datetime.utcnow() + timedelta(days=365),
                "ultima_actualizacion": datetime.utcnow(),
                "ajustes": []
            }
        ]
        
        clientes_data = [
            {
                "nombre": "Ana Pérez",
                "email": "ana@example.com",
                "telefono": "+57 300 123 4567",
                "direccion": "Calle 123 #45-67",
                "fecha_registro": datetime.utcnow() - timedelta(days=30),
                "activo": True
            },
            {
                "nombre": "Carlos Rodríguez", 
                "email": "carlos@example.com",
                "telefono": "+57 301 234 5678",
                "direccion": "Carrera 45 #12-34",
                "fecha_registro": datetime.utcnow() - timedelta(days=15),
                "activo": True
            },
            {
                "nombre": "María González",
                "email": "maria@example.com", 
                "telefono": "+57 302 345 6789",
                "direccion": "Avenida 67 #89-01",
                "fecha_registro": datetime.utcnow() - timedelta(days=60),
                "activo": True
            }
        ]
        
        # Insertar inventario
        print("📊 Insertando registros de inventario...")
        await db.inventario.delete_many({})
        result = await db.inventario.insert_many(inventario_data)
        print(f"✅ Insertados {len(result.inserted_ids)} registros de inventario")
        
        # Insertar clientes
        print("👥 Insertando clientes...")
        await db.clientes.delete_many({})
        result = await db.clientes.insert_many(clientes_data)
        print(f"✅ Insertados {len(result.inserted_ids)} clientes")
        
        # Obtener IDs de clientes insertados
        clientes_insertados = await db.clientes.find().to_list(100)
        cliente_ids = [str(c["_id"]) for c in clientes_insertados]
        
        transacciones_data = [
            {
                "transaccion_id": "T12345678",
                "cliente_id": cliente_ids[0],
                "sucursal_id": "S01",
                "fecha_creacion": datetime.utcnow() - timedelta(days=1),
                "fecha_finalizacion": datetime.utcnow() - timedelta(days=1),
                "estado": "finalizada",
                "productos": [
                    {
                        "producto_id": "LECHE001",
                        "cantidad": 2,
                        "precio_unitario": {"base": 4000, "moneda": "COP"},
                        "subtotal": {"base": 8000, "moneda": "COP"}
                    },
                    {
                        "producto_id": "PAN001", 
                        "cantidad": 1,
                        "precio_unitario": {"base": 3500, "moneda": "COP"},
                        "subtotal": {"base": 3500, "moneda": "COP"}
                    }
                ],
                "subtotal": {"base": 11500, "moneda": "COP"},
                "descuento_total": {"base": 0, "moneda": "COP"},
                "total": {"base": 11500, "moneda": "COP"},
                "metodo_pago": "tarjeta",
                "monto_recibido": {"base": 11500, "moneda": "COP"},
                "promociones": []
            },
            {
                "transaccion_id": "T12345679",
                "cliente_id": cliente_ids[1],
                "sucursal_id": "S01", 
                "fecha_creacion": datetime.utcnow() - timedelta(hours=5),
                "fecha_finalizacion": datetime.utcnow() - timedelta(hours=5),
                "estado": "finalizada",
                "productos": [
                    {
                        "producto_id": "ARROZ001",
                        "cantidad": 3,
                        "precio_unitario": {"base": 2800, "moneda": "COP"},
                        "subtotal": {"base": 8400, "moneda": "COP"}
                    },
                    {
                        "producto_id": "ACEITE001",
                        "cantidad": 1,
                        "precio_unitario": {"base": 5200, "moneda": "COP"},
                        "subtotal": {"base": 5200, "moneda": "COP"}
                    }
                ],
                "subtotal": {"base": 13600, "moneda": "COP"},
                "descuento_total": {"base": 1360, "moneda": "COP"},  # 10% descuento
                "total": {"base": 12240, "moneda": "COP"},
                "metodo_pago": "efectivo",
                "monto_recibido": {"base": 15000, "moneda": "COP"},
                "promociones": [
                    {
                        "promocion_id": "DESC10",
                        "tipo": "porcentaje",
                        "descuento": {"base": 1360, "moneda": "COP"},
                        "descripcion": "10% de descuento"
                    }
                ]
            },
            {
                "transaccion_id": "T12345680",
                "cliente_id": cliente_ids[2],
                "sucursal_id": "S02",
                "fecha_creacion": datetime.utcnow() - timedelta(hours=2),
                "fecha_finalizacion": datetime.utcnow() - timedelta(hours=2),
                "estado": "finalizada",
                "productos": [
                    {
                        "producto_id": "YOGURT001",
                        "cantidad": 4,
                        "precio_unitario": {"base": 2100, "moneda": "COP"},
                        "subtotal": {"base": 8400, "moneda": "COP"}
                    }
                ],
                "subtotal": {"base": 8400, "moneda": "COP"},
                "descuento_total": {"base": 0, "moneda": "COP"},
                "total": {"base": 8400, "moneda": "COP"},
                "metodo_pago": "tarjeta",
                "monto_recibido": {"base": 8400, "moneda": "COP"},
                "promociones": []
            }
        ]
        
        # Insertar transacciones
        print("💳 Insertando transacciones...")
        await db.transacciones.delete_many({})
        result = await db.transacciones.insert_many(transacciones_data)
        print(f"✅ Insertadas {len(result.inserted_ids)} transacciones")
        
        print("🎉 Base de datos poblada exitosamente!")
        print(f"🔗 Conectado a: {DATABASE_NAME} en MongoDB Atlas")
        print("\n📋 Datos de prueba creados:")
        print(f"   • {len(productos_data)} productos")
        print(f"   • {len(inventario_data)} registros de inventario")
        print(f"   • {len(clientes_data)} clientes")
        print(f"   • {len(transacciones_data)} transacciones")
        print("\n🧪 Códigos de productos para pruebas:")
        for producto in productos_data:
            print(f"   • {producto['codigo']}: {producto['nombre']}")
        
    except Exception as e:
        print(f"❌ Error al poblar la base de datos: {e}")
        print("💡 Verifica tu cadena de conexión de MongoDB Atlas y que tengas acceso a la red")
        raise e
    
    finally:
        client.close()
        print("🔌 Conexión cerrada")

if __name__ == "__main__":
    print("🌱 Iniciando script de población de datos para MongoDB Atlas...")
    asyncio.run(seed_database())
