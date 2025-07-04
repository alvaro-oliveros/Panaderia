#!/usr/bin/env python3
"""
Generate realistic movements for specific users in their assigned locations
Creates movements for alvaro, miguel, and fabiola based on their sede assignments
"""

import requests
import random
import json
from datetime import datetime, timedelta

# API Configuration
API_URL = "http://127.0.0.1:8000"

# User assignments (from API response)
USERS = {
    2: {"name": "alvaro", "sedes": [1, 2]},    # Centro, Norte
    3: {"name": "miguel", "sedes": [3, 4]},    # Sur, Residencial  
    4: {"name": "fabiola", "sedes": [5]}       # Plaza
}

def get_products_by_sede(sede_id):
    """Get all products for a specific sede"""
    try:
        response = requests.get(f"{API_URL}/productos/")
        if response.status_code == 200:
            productos = response.json()
            return [p for p in productos if p["Sede_id"] == sede_id]
        return []
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

def create_user_movement(user_id, producto_id, sede_id, movement_type="venta", days_ago=0):
    """Create a movement for a specific user"""
    
    # Calculate date
    movement_date = datetime.now() - timedelta(days=days_ago)
    
    # Generate realistic quantities and prices based on movement type
    if movement_type == "venta":
        cantidad = random.uniform(1, 8)  # 1-8 items sold
        precio_multiplier = random.uniform(0.95, 1.05)  # Small price variation
    elif movement_type == "reabastecimiento":
        cantidad = random.uniform(20, 100)  # Larger restocking quantities
        precio_multiplier = random.uniform(0.6, 0.8)  # Wholesale prices
    elif movement_type == "ajuste":
        cantidad = random.uniform(1, 10)
        precio_multiplier = 1.0
    else:  # agregado, entrada
        cantidad = random.uniform(5, 30)
        precio_multiplier = random.uniform(0.7, 0.9)
    
    # Get product info to calculate realistic price
    try:
        product_response = requests.get(f"{API_URL}/productos/")
        productos = product_response.json()
        producto = next((p for p in productos if p["idProductos"] == producto_id), None)
        
        if producto:
            base_price = producto["Precio"]
            precio = round(base_price * precio_multiplier, 2)
        else:
            precio = 10.0  # Fallback price
            
    except:
        precio = 10.0  # Fallback price
    
    # Create movement
    movement_data = {
        "producto_id": producto_id,
        "Cantidad": round(cantidad, 2),
        "Precio": precio,
        "tipo": movement_type,
        "Usuario_id": user_id,
        "sede_id": sede_id
    }
    
    try:
        response = requests.post(f"{API_URL}/movimientos/", json=movement_data)
        if response.status_code == 200:
            return True
        else:
            print(f"Error creating movement: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error posting movement: {e}")
        return False

def generate_user_movements():
    """Generate movements for all users over the past 30 days"""
    
    print("🚀 Generando movimientos para usuarios específicos...")
    total_movements = 0
    
    for user_id, user_info in USERS.items():
        user_name = user_info["name"]
        user_sedes = user_info["sedes"]
        
        print(f"\n👤 Procesando usuario: {user_name} (ID: {user_id})")
        print(f"📍 Sedes asignadas: {user_sedes}")
        
        user_movements = 0
        
        # Generate movements for the past 30 days
        for day in range(30):
            # Each user works 5-6 days per week on average
            if random.random() > 0.15:  # 85% chance of working each day
                
                for sede_id in user_sedes:
                    # Get products for this sede
                    productos = get_products_by_sede(sede_id)
                    
                    if not productos:
                        print(f"   ⚠️ No products found for sede {sede_id}")
                        continue
                    
                    # Generate 3-8 movements per sede per day
                    movements_today = random.randint(3, 8)
                    
                    for _ in range(movements_today):
                        # Choose random product
                        producto = random.choice(productos)
                        producto_id = producto["idProductos"]
                        
                        # Choose movement type (weighted towards sales)
                        movement_types = ["venta"] * 7 + ["reabastecimiento"] * 2 + ["ajuste"] * 1
                        movement_type = random.choice(movement_types)
                        
                        # Create movement
                        success = create_user_movement(
                            user_id=user_id,
                            producto_id=producto_id,
                            sede_id=sede_id,
                            movement_type=movement_type,
                            days_ago=day
                        )
                        
                        if success:
                            user_movements += 1
                            total_movements += 1
        
        print(f"   ✅ {user_movements} movimientos creados para {user_name}")
    
    print(f"\n🎉 COMPLETADO: {total_movements} movimientos totales generados")
    return total_movements

def main():
    print("👥 Generador de Movimientos por Usuario")
    print("=" * 50)
    
    # Check API connection
    try:
        response = requests.get(f"{API_URL}/usuarios/")
        if response.status_code != 200:
            print("❌ No se puede conectar a la API")
            return
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    print("✅ Conexión API establecida")
    
    # Confirm before generating
    print("\nEsto generará movimientos para:")
    for user_id, user_info in USERS.items():
        sede_names = []
        for sede_id in user_info["sedes"]:
            # Get sede name
            try:
                sedes_response = requests.get(f"{API_URL}/sedes/")
                sedes = sedes_response.json()
                sede = next((s for s in sedes if s["idSedes"] == sede_id), None)
                if sede:
                    sede_names.append(sede["Nombre"])
                else:
                    sede_names.append(f"Sede {sede_id}")
            except:
                sede_names.append(f"Sede {sede_id}")
        
        print(f"  • {user_info['name']}: {', '.join(sede_names)}")
    
    print("\n🚀 Iniciando generación automática...")
    
    # Generate movements
    movements_created = generate_user_movements()
    
    print(f"\n📊 Resumen:")
    print(f"   • Movimientos creados: {movements_created}")
    print(f"   • Período: Últimos 30 días")
    print(f"   • Usuarios: alvaro, miguel, fabiola")
    print("\n🌐 Revisa los movimientos en:")
    print("   http://localhost:3000/movimientos.html")

if __name__ == "__main__":
    main()