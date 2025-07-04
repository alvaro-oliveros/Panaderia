#!/usr/bin/env python3
"""
Business Data Generator for Panadería Management System
Generates realistic bakery business data for AI analytics and visualization

Usage:
    python3 generate_business_data.py

This creates:
- Multiple bakery locations (sedes) with different characteristics
- 50+ realistic bakery products with proper pricing
- 6 months of historical sales and movement data
- Realistic patterns: weekends, holidays, seasonal trends
"""

import requests
import random
import json
from datetime import datetime, timedelta
import time

# API Configuration
API_URL = "http://127.0.0.1:8000"

# Realistic bakery product data
BAKERY_PRODUCTS = {
    "Panadería": [
        {"nombre": "Pan Francés", "precio": 1.50, "categoria": "Pan", "unidad": "unidad"},
        {"nombre": "Pan Integral", "precio": 2.00, "categoria": "Pan", "unidad": "unidad"},
        {"nombre": "Baguette", "precio": 3.50, "categoria": "Pan", "unidad": "unidad"},
        {"nombre": "Pan de Centeno", "precio": 2.80, "categoria": "Pan", "unidad": "unidad"},
        {"nombre": "Pan Dulce", "precio": 4.00, "categoria": "Pan", "unidad": "unidad"},
        {"nombre": "Rosca de Reyes", "precio": 25.00, "categoria": "Pan", "unidad": "unidad"},
        {"nombre": "Pan de Muerto", "precio": 15.00, "categoria": "Pan", "unidad": "unidad"},
    ],
    "Pastelería": [
        {"nombre": "Croissant Simple", "precio": 4.50, "categoria": "Pastelería", "unidad": "unidad"},
        {"nombre": "Croissant de Chocolate", "precio": 5.50, "categoria": "Pastelería", "unidad": "unidad"},
        {"nombre": "Donut Glaseada", "precio": 3.00, "categoria": "Pastelería", "unidad": "unidad"},
        {"nombre": "Éclair de Chocolate", "precio": 6.00, "categoria": "Pastelería", "unidad": "unidad"},
        {"nombre": "Muffin de Arándanos", "precio": 4.00, "categoria": "Pastelería", "unidad": "unidad"},
        {"nombre": "Palmera", "precio": 3.50, "categoria": "Pastelería", "unidad": "unidad"},
        {"nombre": "Cupcake Vainilla", "precio": 5.00, "categoria": "Pastelería", "unidad": "unidad"},
        {"nombre": "Tartaleta de Frutas", "precio": 7.50, "categoria": "Pastelería", "unidad": "unidad"},
    ],
    "Tortas": [
        {"nombre": "Torta de Chocolate", "precio": 180.00, "categoria": "Tortas", "unidad": "unidad"},
        {"nombre": "Torta de Vainilla", "precio": 150.00, "categoria": "Tortas", "unidad": "unidad"},
        {"nombre": "Torta de Fresa", "precio": 200.00, "categoria": "Tortas", "unidad": "unidad"},
        {"nombre": "Torta Red Velvet", "precio": 220.00, "categoria": "Tortas", "unidad": "unidad"},
        {"nombre": "Cheesecake", "precio": 250.00, "categoria": "Tortas", "unidad": "unidad"},
        {"nombre": "Torta Tres Leches", "precio": 190.00, "categoria": "Tortas", "unidad": "unidad"},
    ],
    "Ingredientes": [
        {"nombre": "Harina Trigo", "precio": 25.00, "categoria": "Ingredientes", "unidad": "kg"},
        {"nombre": "Azúcar", "precio": 18.00, "categoria": "Ingredientes", "unidad": "kg"},
        {"nombre": "Mantequilla", "precio": 45.00, "categoria": "Ingredientes", "unidad": "kg"},
        {"nombre": "Huevos", "precio": 35.00, "categoria": "Ingredientes", "unidad": "docena"},
        {"nombre": "Leche", "precio": 22.00, "categoria": "Ingredientes", "unidad": "litro"},
        {"nombre": "Chocolate", "precio": 85.00, "categoria": "Ingredientes", "unidad": "kg"},
        {"nombre": "Levadura", "precio": 12.00, "categoria": "Ingredientes", "unidad": "paquete"},
        {"nombre": "Sal", "precio": 8.00, "categoria": "Ingredientes", "unidad": "kg"},
        {"nombre": "Vainilla", "precio": 120.00, "categoria": "Ingredientes", "unidad": "botella"},
    ],
    "Bebidas": [
        {"nombre": "Café Americano", "precio": 8.00, "categoria": "Bebidas", "unidad": "taza"},
        {"nombre": "Café con Leche", "precio": 12.00, "categoria": "Bebidas", "unidad": "taza"},
        {"nombre": "Cappuccino", "precio": 15.00, "categoria": "Bebidas", "unidad": "taza"},
        {"nombre": "Chocolate Caliente", "precio": 18.00, "categoria": "Bebidas", "unidad": "taza"},
        {"nombre": "Té de Manzanilla", "precio": 6.00, "categoria": "Bebidas", "unidad": "taza"},
        {"nombre": "Jugo de Naranja", "precio": 10.00, "categoria": "Bebidas", "unidad": "vaso"},
        {"nombre": "Agua", "precio": 5.00, "categoria": "Bebidas", "unidad": "botella"},
    ]
}

# Bakery locations with different characteristics
SEDES_DATA = [
    {
        "nombre": "Panadería Centro",
        "direccion": "Av. Principal 123, Centro",
        "caracteristicas": "alta_demanda",  # High sales, premium products
        "multiplicador_ventas": 1.4
    },
    {
        "nombre": "Panadería Norte",
        "direccion": "Calle Norte 456, Zona Norte",
        "caracteristicas": "familia",  # Family-oriented, more bread/basic items
        "multiplicador_ventas": 1.0
    },
    {
        "nombre": "Panadería Sur",
        "direccion": "Av. Sur 789, Zona Sur",
        "caracteristicas": "economica",  # Budget-friendly, lower prices
        "multiplicador_ventas": 0.7
    },
    {
        "nombre": "Panadería Residencial",
        "direccion": "Calle Residencial 321, Las Flores",
        "caracteristicas": "residencial",  # Residential area, steady but moderate
        "multiplicador_ventas": 0.9
    },
    {
        "nombre": "Panadería Plaza",
        "direccion": "Plaza Comercial, Local 15",
        "caracteristicas": "comercial",  # Mall location, high weekend traffic
        "multiplicador_ventas": 1.2
    }
]

def check_api_connection():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_URL}/sedes/", timeout=5)
        if response.status_code == 200:
            print("✅ API conectada correctamente")
            return True
        else:
            print(f"❌ API respondió con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar a la API: {e}")
        print("🔧 Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
        return False

def create_sedes():
    """Create bakery locations"""
    print("\n🏢 Creando sedes...")
    created_sedes = []
    
    for sede_data in SEDES_DATA:
        try:
            response = requests.post(f"{API_URL}/sedes/", json={
                "Nombre": sede_data["nombre"],
                "Direccion": sede_data["direccion"],
                "Usuario_id": 1  # Admin user
            })
            
            if response.status_code == 200:
                sede = response.json()
                sede["caracteristicas"] = sede_data["caracteristicas"]
                sede["multiplicador_ventas"] = sede_data["multiplicador_ventas"]
                created_sedes.append(sede)
                print(f"✅ Sede creada: {sede_data['nombre']}")
            else:
                print(f"❌ Error creando sede {sede_data['nombre']}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión creando sede {sede_data['nombre']}: {e}")
    
    return created_sedes

def create_products(sedes):
    """Create products for each sede"""
    print("\n🥖 Creando productos...")
    created_products = []
    
    for sede in sedes:
        print(f"  📍 Sede: {sede['Nombre']}")
        sede_products = []
        
        # Each sede gets all products but with different stock levels
        for categoria, productos in BAKERY_PRODUCTS.items():
            for producto_data in productos:
                # Adjust pricing based on sede characteristics
                precio_base = producto_data["precio"]
                if sede["caracteristicas"] == "alta_demanda":
                    precio = precio_base * 1.1  # Premium pricing
                elif sede["caracteristicas"] == "economica":
                    precio = precio_base * 0.9  # Budget pricing
                else:
                    precio = precio_base
                
                # Set realistic stock levels
                if categoria == "Ingredientes":
                    stock = random.randint(50, 200)  # Higher stock for ingredients
                elif categoria == "Tortas":
                    stock = random.randint(2, 8)    # Lower stock for cakes
                else:
                    stock = random.randint(10, 50)  # Medium stock for others
                
                try:
                    response = requests.post(f"{API_URL}/productos/", json={
                        "Nombre": producto_data["nombre"],
                        "Descripcion": f"{producto_data['categoria']} - {sede['Nombre']}",
                        "Precio": round(precio, 2),
                        "Stock": stock,
                        "Unidad": producto_data["unidad"],
                        "Categoria": producto_data["categoria"],
                        "Sede_id": sede["idSedes"]
                    })
                    
                    if response.status_code == 200:
                        producto = response.json()
                        producto["categoria_original"] = categoria
                        producto["sede_info"] = sede
                        sede_products.append(producto)
                        created_products.append(producto)
                    else:
                        print(f"    ❌ Error creando producto {producto_data['nombre']}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"    ❌ Error de conexión: {e}")
        
        print(f"    ✅ {len(sede_products)} productos creados para {sede['Nombre']}")
    
    print(f"✅ Total: {len(created_products)} productos creados")
    return created_products

def generate_historical_movements(products, days_back=180):
    """Generate realistic historical sales and movement data"""
    print(f"\n📊 Generando {days_back} días de movimientos históricos...")
    
    movements_created = 0
    start_date = datetime.now() - timedelta(days=days_back)
    
    for day_offset in range(days_back):
        current_date = start_date + timedelta(days=day_offset)
        
        # Determine day characteristics
        is_weekend = current_date.weekday() >= 5
        is_holiday = is_special_date(current_date)
        
        # Weekend and holiday multipliers
        if is_holiday:
            day_multiplier = 1.8  # Holidays are busier
        elif is_weekend:
            day_multiplier = 1.3  # Weekends are busier
        else:
            day_multiplier = 1.0
        
        # Get unique sedes
        sedes_procesadas = {}
        for p in products:
            sede_id = p["sede_info"]["idSedes"]
            if sede_id not in sedes_procesadas:
                sedes_procesadas[sede_id] = p["sede_info"]
        
        # Generate movements for each sede
        for sede in sedes_procesadas.values():
            sede_products = [p for p in products if p["sede_info"]["idSedes"] == sede["idSedes"]]
            
            # Number of transactions for this day/sede
            base_transactions = random.randint(15, 35)
            transactions = int(base_transactions * day_multiplier * sede["multiplicador_ventas"])
            
            for _ in range(transactions):
                # Choose random product (weighted by category popularity)
                product = choose_weighted_product(sede_products, current_date, is_weekend)
                
                if product:
                    # Generate realistic transaction
                    movement_type, cantidad, precio = generate_realistic_transaction(
                        product, current_date, is_weekend, is_holiday
                    )
                    
                    # Create movement
                    try:
                        response = requests.post(f"{API_URL}/movimientos/", json={
                            "producto_id": product["idProductos"],
                            "Cantidad": cantidad,
                            "Precio": precio,
                            "tipo": movement_type,
                            "Usuario_id": 1,  # Admin user
                            "sede_id": sede["idSedes"]
                        })
                        
                        if response.status_code == 200:
                            movements_created += 1
                        
                    except requests.exceptions.RequestException:
                        pass  # Silent fail to keep generation moving
        
        # Progress indicator
        if day_offset % 30 == 0:
            print(f"  📅 Procesados {day_offset} días... ({movements_created} movimientos)")
    
    print(f"✅ {movements_created} movimientos históricos creados")
    return movements_created

def is_special_date(date):
    """Check if date is a special holiday/event"""
    special_dates = [
        (12, 25),  # Christmas
        (12, 24),  # Christmas Eve
        (1, 1),    # New Year
        (2, 14),   # Valentine's Day
        (5, 10),   # Mother's Day (approximate)
        (11, 2),   # Day of the Dead
    ]
    
    return (date.month, date.day) in special_dates

def choose_weighted_product(products, date, is_weekend):
    """Choose a product with realistic probability weights"""
    if not products:
        return None
    
    # Seasonal adjustments
    month = date.month
    weights = {}
    
    for product in products:
        base_weight = 1.0
        categoria = product.get("categoria_original", product["Categoria"])
        
        # Category popularity adjustments
        if categoria == "Panadería":
            base_weight = 3.0  # Bread is most popular
        elif categoria == "Bebidas":
            base_weight = 2.5  # Drinks are popular
            if month in [12, 1, 2] and "Chocolate Caliente" in product["Nombre"]:
                base_weight = 4.0  # Hot chocolate in winter
        elif categoria == "Pastelería":
            base_weight = 2.0
            if is_weekend:
                base_weight = 2.5  # More pastries on weekends
        elif categoria == "Tortas":
            base_weight = 0.3  # Cakes are occasional
            if is_weekend:
                base_weight = 0.8
        elif categoria == "Ingredientes":
            base_weight = 0.1  # Ingredients are rarely sold directly
        
        # Seasonal adjustments
        if "Pan de Muerto" in product["Nombre"] and month == 11:
            base_weight = 5.0
        elif "Rosca de Reyes" in product["Nombre"] and month == 1:
            base_weight = 4.0
        elif "Chocolate Caliente" in product["Nombre"] and month in [12, 1, 2]:
            base_weight = 3.0
        
        weights[product["idProductos"]] = base_weight
    
    # Choose weighted random product
    total_weight = sum(weights.values())
    if total_weight == 0:
        return random.choice(products)
    
    random_val = random.uniform(0, total_weight)
    current_weight = 0
    
    for product in products:
        current_weight += weights[product["idProductos"]]
        if random_val <= current_weight:
            return product
    
    return products[0]  # Fallback

def generate_realistic_transaction(product, date, is_weekend, is_holiday):
    """Generate realistic transaction details"""
    categoria = product.get("categoria_original", product["Categoria"])
    precio_base = product["Precio"]
    
    # Determine transaction type (mostly sales)
    rand = random.random()
    if rand < 0.85:  # 85% sales
        movement_type = "venta"
    elif rand < 0.95:  # 10% restocking
        movement_type = "reabastecimiento"
    else:  # 5% adjustments
        movement_type = "ajuste"
    
    if movement_type == "venta":
        # Realistic sales quantities
        if categoria == "Tortas":
            cantidad = 1  # Usually sell 1 cake
        elif categoria == "Ingredientes":
            cantidad = random.uniform(0.5, 5.0)  # Ingredients by weight
        elif categoria == "Bebidas":
            cantidad = random.randint(1, 3)  # 1-3 drinks
        else:
            cantidad = random.randint(1, 6)  # 1-6 items
        
        # Pricing with small variations
        precio = precio_base * random.uniform(0.98, 1.02)
        
    elif movement_type == "reabastecimiento":
        # Restocking quantities
        if categoria == "Ingredientes":
            cantidad = random.randint(10, 50)
        else:
            cantidad = random.randint(20, 100)
        
        # Wholesale prices (lower than retail)
        precio = precio_base * random.uniform(0.6, 0.8)
        
    else:  # ajuste
        cantidad = random.randint(1, 5)
        precio = precio_base
    
    return movement_type, round(cantidad, 2), round(precio, 2)

def main():
    """Main data generation function"""
    print("🍞 Generador de Datos de Negocio - Sistema de Panadería")
    print("=" * 60)
    
    # Check API connection
    if not check_api_connection():
        return
    
    print("\n⚠️  IMPORTANTE: Este script generará una gran cantidad de datos.")
    print("Asegúrate de tener una copia de seguridad de tu base de datos actual.")
    print("🚀 Iniciando generación automática de datos...")
    
    start_time = time.time()
    
    try:
        # Step 1: Create sedes
        sedes = create_sedes()
        if not sedes:
            print("❌ No se pudieron crear las sedes. Abortando.")
            return
        
        # Step 2: Create products
        products = create_products(sedes)
        if not products:
            print("❌ No se pudieron crear productos. Abortando.")
            return
        
        # Step 3: Generate historical movements
        movements_count = generate_historical_movements(products, days_back=180)
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 GENERACIÓN DE DATOS COMPLETADA")
        print("=" * 60)
        print(f"📍 Sedes creadas: {len(sedes)}")
        print(f"🥖 Productos creados: {len(products)}")
        print(f"📊 Movimientos generados: {movements_count}")
        print(f"⏱️  Tiempo total: {duration:.1f} segundos")
        print("\n🌐 Revisa los datos en:")
        print("   • http://localhost:3000/index.html")
        print("   • http://localhost:3000/productos.html")
        print("   • http://localhost:3000/movimientos.html")
        print("\n🤖 ¡Listos para integrar IA con datos realistas!")
        
    except KeyboardInterrupt:
        print("\n🛑 Generación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la generación: {e}")

if __name__ == "__main__":
    main()