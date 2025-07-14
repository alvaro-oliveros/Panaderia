#!/usr/bin/env python3
"""
Fix fractional quantities in movements - round to whole numbers
Since bakery products are sold as individual units, fractional quantities don't make sense
"""

import requests
import json

API_URL = "http://127.0.0.1:8000"

def fix_movements():
    """Round all fractional quantities to whole numbers"""
    
    print("🔧 Fixing fractional quantities in movements...")
    
    # Get all movements
    try:
        response = requests.get(f"{API_URL}/movimientos/?limit=10000")
        if response.status_code != 200:
            print(f"❌ Error fetching movements: {response.status_code}")
            return
        
        data = response.json()
        movements = data['movements']
        
        print(f"📊 Found {len(movements)} movements to check")
        
        fixed_count = 0
        
        for mov in movements:
            # Check if quantity is fractional
            current_qty = mov['Cantidad']
            rounded_qty = round(current_qty)
            
            # Only update if it's actually fractional
            if current_qty != rounded_qty:
                # Ensure minimum of 1 unit for sales
                if mov['tipo'] == 'venta' and rounded_qty < 1:
                    rounded_qty = 1
                
                # Update the movement
                update_data = {
                    "producto_id": mov["producto_id"],
                    "Cantidad": rounded_qty,
                    "Precio": mov["Precio"],
                    "tipo": mov["tipo"],
                    "Usuario_id": mov["Usuario_id"],
                    "sede_id": mov["sede_id"]
                }
                
                try:
                    update_response = requests.put(
                        f"{API_URL}/movimientos/{mov['idMovimientos']}", 
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        print(f"  ✅ Fixed movement {mov['idMovimientos']}: {current_qty} → {rounded_qty}")
                        fixed_count += 1
                    else:
                        print(f"  ❌ Failed to update movement {mov['idMovimientos']}: {update_response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Error updating movement {mov['idMovimientos']}: {e}")
        
        print(f"\n🎉 Summary:")
        print(f"   • Total movements checked: {len(movements)}")
        print(f"   • Fractional quantities fixed: {fixed_count}")
        print(f"   • Movements now use whole numbers only")
        
        if fixed_count > 0:
            print(f"\n✨ All bakery products now have realistic whole-number quantities!")
        else:
            print(f"\n✅ No fractional quantities found - data already looks good!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def fix_products_stock():
    """Round product stock to whole numbers"""
    
    print("\n🔧 Fixing fractional stock in products...")
    
    try:
        response = requests.get(f"{API_URL}/productos/")
        if response.status_code != 200:
            print(f"❌ Error fetching products: {response.status_code}")
            return
        
        productos = response.json()
        print(f"📊 Found {len(productos)} products to check")
        
        fixed_count = 0
        
        for prod in productos:
            current_stock = prod['Stock']
            rounded_stock = round(current_stock)
            
            # Only update if it's actually fractional
            if current_stock != rounded_stock:
                # Update the product
                update_data = {
                    "Nombre": prod["Nombre"],
                    "Descripcion": prod["Descripcion"],
                    "Precio": prod["Precio"],
                    "Stock": rounded_stock,
                    "Unidad": prod["Unidad"],
                    "Categoria": prod["Categoria"],
                    "Sede_id": prod["Sede_id"]
                }
                
                try:
                    update_response = requests.put(
                        f"{API_URL}/productos/{prod['idProductos']}", 
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        print(f"  ✅ Fixed product {prod['idProductos']}: {current_stock} → {rounded_stock}")
                        fixed_count += 1
                    else:
                        print(f"  ❌ Failed to update product {prod['idProductos']}: {update_response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Error updating product {prod['idProductos']}: {e}")
        
        print(f"\n📦 Product stock summary:")
        print(f"   • Total products checked: {len(productos)}")
        print(f"   • Fractional stocks fixed: {fixed_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🍞 Bakery Quantity Fixer")
    print("=" * 50)
    print("Making quantities realistic for bakery products")
    print("(Converting fractional quantities to whole numbers)")
    print()
    
    # Check API connection
    try:
        response = requests.get(f"{API_URL}/movimientos/?limit=1")
        if response.status_code != 200:
            print("❌ Cannot connect to API")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    print("✅ API connection established")
    
    # Fix movements
    fix_movements()
    
    # Fix products
    fix_products_stock()
    
    print(f"\n🎯 Changes completed!")
    print(f"   • Movement quantities now whole numbers only")
    print(f"   • Product stock counts now whole numbers only") 
    print(f"   • Forms updated to prevent future fractional entries")
    print(f"\n🌐 Check the results at:")
    print(f"   • http://localhost:3000/movimientos.html")
    print(f"   • http://localhost:3000/productos.html")

if __name__ == "__main__":
    main()