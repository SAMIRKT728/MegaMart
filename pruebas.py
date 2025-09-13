"""
Ejemplos de uso para todos los endpoints de la API
Ejecuta estos ejemplos después de tener la API corriendo en http://localhost:8000
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_response(response, title):
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
    except:
        print(f"Response: {response.text}")

# ============================================================================
# ENDPOINTS DE VENTAS
# ============================================================================

def ejemplos_ventas():
    print("\n🛒 EJEMPLOS DE ENDPOINTS DE VENTAS")
    
    # 1. Iniciar nueva transacción
    print("\n1. POST /api/ventas/iniciar-transaccion - Iniciar nueva venta")
    data = {
        "cliente_id": "C12345678",
        "sucursal_id": "S001"
    }
    response = requests.post(f"{BASE_URL}/api/ventas/iniciar-transaccion", json=data)
    print_response(response, "Iniciar Transacción")
    
    if response.status_code == 201:
        transaccion_id = response.json()["transaccion_id"]
        
        # 2. Agregar producto al carrito
        print("\n2. POST /api/ventas/agregar-producto - Agregar producto al carrito")
        data = {
            "producto_id": "P12345678",
            "cantidad": 2
        }
        response = requests.post(f"{BASE_URL}/api/ventas/agregar-producto/{transaccion_id}", json=data)
        print_response(response, "Agregar Producto")
        
        # 3. Aplicar promoción
        print("\n3. POST /api/ventas/aplicar-promocion - Validar y aplicar descuentos")
        data = {
            "codigo_promocion": "DESC10"
        }
        response = requests.post(f"{BASE_URL}/api/ventas/aplicar-promocion/{transaccion_id}", json=data)
        print_response(response, "Aplicar Promoción")
        
        # 4. Finalizar venta
        print("\n4. POST /api/ventas/finalizar - Procesar pago y finalizar venta")
        data = {
            "metodo_pago": "tarjeta_credito",
            "monto_recibido": 100.00
        }
        response = requests.post(f"{BASE_URL}/api/ventas/finalizar/{transaccion_id}", json=data)
        print_response(response, "Finalizar Venta")

# ============================================================================
# ENDPOINTS DE INVENTARIO
# ============================================================================

def ejemplos_inventario():
    print("\n📦 EJEMPLOS DE ENDPOINTS DE INVENTARIO")
    
    # 1. Verificar disponibilidad
    print("\n1. GET /api/inventario/disponibilidad/:codigo - Verificar stock en tiempo real")
    response = requests.get(f"{BASE_URL}/api/v1/inventario/disponibilidad/P12345678")
    print_response(response, "Verificar Disponibilidad")
    
    # 2. Transferir stock
    print("\n2. POST /api/inventario/transferir - Transferir stock entre sucursales")
    data = {
        "producto_id": "P12345678",
        "sucursal_origen": "S001",
        "sucursal_destino": "S002",
        "cantidad": 10,
        "motivo": "Rebalanceo de inventario",
        "autorizado_por": "admin@empresa.com"
    }
    response = requests.post(f"{BASE_URL}/api/v1/inventario/transferir", json=data)
    print_response(response, "Transferir Stock")
    
    # 3. Productos próximos a vencer
    print("\n3. GET /api/inventario/perecederos/vencimientos - Productos próximos a vencer")
    response = requests.get(f"{BASE_URL}/api/v1/inventario/perecederos/vencimientos?dias=7")
    print_response(response, "Productos Próximos a Vencer")
    
    # 4. Ajustar stock
    print("\n4. PUT /api/inventario/ajuste-stock - Ajustar inventario por pérdidas/mermas")
    data = {
        "producto_id": "P12345678",
        "sucursal_id": "S001",
        "cantidad_ajuste": -5,  # Reducir 5 unidades
        "motivo": "Producto dañado durante transporte",
        "tipo_ajuste": "perdida",
        "autorizado_por": "supervisor@empresa.com"
    }
    response = requests.put(f"{BASE_URL}/api/v1/inventario/ajuste-stock", json=data)
    print_response(response, "Ajustar Stock")

# ============================================================================
# ENDPOINTS DE ANALYTICS
# ============================================================================

def ejemplos_analytics():
    print("\n📊 EJEMPLOS DE ENDPOINTS DE ANALYTICS")
    
    # 1. Dashboard de ventas en tiempo real
    print("\n1. GET /api/analytics/ventas/tiempo-real - Dashboard de ventas actuales")
    response = requests.get(f"{BASE_URL}/api/analytics/ventas/tiempo-real")
    print_response(response, "Ventas Tiempo Real")
    
    # 2. Productos trending
    print("\n2. GET /api/analytics/productos/trending - Productos más vendidos hoy")
    response = requests.get(f"{BASE_URL}/api/analytics/productos/trending")
    print_response(response, "Productos Trending")
    
    # 3. Predicción de demanda
    print("\n3. GET /api/analytics/prediccion-demanda/:producto - Estimación de ventas")
    response = requests.get(f"{BASE_URL}/api/analytics/prediccion-demanda/P12345678")
    print_response(response, "Predicción de Demanda")
    
    # 4. Recomendaciones para cliente
    print("\n4. GET /api/cliente/:id/recomendaciones - Productos sugeridos")
    response = requests.get(f"{BASE_URL}/api/analytics/cliente/C12345678/recomendaciones")
    print_response(response, "Recomendaciones Cliente")

# ============================================================================
# EJEMPLOS CON CURL
# ============================================================================

def generar_ejemplos_curl():
    print("\n🔧 EJEMPLOS CON CURL")
    
    curl_examples = """
# ============================================================================
# VENTAS
# ============================================================================

# Iniciar transacción
curl -X POST "http://localhost:8000/api/ventas/iniciar-transaccion" \\
  -H "Content-Type: application/json" \\
  -d '{
    "cliente_id": "C12345678",
    "sucursal_id": "S001"
  }'

# Agregar producto (reemplaza TRANSACTION_ID)
curl -X POST "http://localhost:8000/api/ventas/agregar-producto/TRANSACTION_ID" \\
  -H "Content-Type: application/json" \\
  -d '{
    "producto_id": "P12345678",
    "cantidad": 2
  }'

# Aplicar promoción
curl -X POST "http://localhost:8000/api/ventas/aplicar-promocion/TRANSACTION_ID" \\
  -H "Content-Type: application/json" \\
  -d '{
    "codigo_promocion": "DESC10"
  }'

# Finalizar venta
curl -X POST "http://localhost:8000/api/ventas/finalizar/TRANSACTION_ID" \\
  -H "Content-Type: application/json" \\
  -d '{
    "metodo_pago": "tarjeta_credito",
    "monto_recibido": 100.00
  }'

# ============================================================================
# INVENTARIO
# ============================================================================

# Verificar disponibilidad
curl -X GET "http://localhost:8000/api/v1/inventario/disponibilidad/P12345678"

# Transferir stock
curl -X POST "http://localhost:8000/api/v1/inventario/transferir" \\
  -H "Content-Type: application/json" \\
  -d '{
    "producto_id": "P12345678",
    "sucursal_origen": "S001",
    "sucursal_destino": "S002",
    "cantidad": 10,
    "motivo": "Rebalanceo de inventario",
    "autorizado_por": "admin@empresa.com"
  }'

# Productos próximos a vencer
curl -X GET "http://localhost:8000/api/v1/inventario/perecederos/vencimientos?dias=7"

# Ajustar stock
curl -X PUT "http://localhost:8000/api/v1/inventario/ajuste-stock" \\
  -H "Content-Type: application/json" \\
  -d '{
    "producto_id": "P12345678",
    "sucursal_id": "S001",
    "cantidad_ajuste": -5,
    "motivo": "Producto dañado",
    "tipo_ajuste": "perdida",
    "autorizado_por": "supervisor@empresa.com"
  }'

# ============================================================================
# ANALYTICS
# ============================================================================

# Dashboard ventas tiempo real
curl -X GET "http://localhost:8000/api/analytics/ventas/tiempo-real"

# Productos trending
curl -X GET "http://localhost:8000/api/analytics/productos/trending"

# Predicción demanda
curl -X GET "http://localhost:8000/api/analytics/prediccion-demanda/P12345678"

# Recomendaciones cliente
curl -X GET "http://localhost:8000/api/analytics/cliente/C12345678/recomendaciones"
"""
    
    print(curl_examples)

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("🚀 EJEMPLOS DE USO - API SISTEMA DE INVENTARIO")
    print("=" * 60)
    print("Asegúrate de que la API esté corriendo en http://localhost:8000")
    print("Y que tengas datos de ejemplo cargados con: python scripts/seed_data.py")
    
    try:
        # Verificar que la API esté corriendo
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API está corriendo correctamente")
            
            # Ejecutar ejemplos
            ejemplos_ventas()
            ejemplos_inventario() 
            ejemplos_analytics()
            generar_ejemplos_curl()
            
        else:
            print("❌ La API no está respondiendo correctamente")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API. Asegúrate de que esté corriendo.")
        print("Ejecuta: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
