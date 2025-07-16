#!/usr/bin/env python3
"""
Test script to verify business summary data includes sede information for low stock products
"""

import sys
import os
sys.path.append('backend')

from backend.app.database import SessionLocal
from backend.app.routes.ai_analytics import get_business_summary_data
import json

def test_business_summary_data():
    """Test that business summary data includes sede information for low stock products"""
    
    db = SessionLocal()
    try:
        # Get business summary data
        business_data = get_business_summary_data(db, days_back=7)
        
        print("=== BUSINESS SUMMARY DATA TEST ===")
        print(json.dumps(business_data, indent=2, ensure_ascii=False))
        
        print("\n=== LOW STOCK PRODUCTS ANALYSIS ===")
        
        low_stock_products = business_data.get('productos_stock_bajo', [])
        
        if not low_stock_products:
            print("❌ No low stock products found")
            return
        
        print(f"✅ Found {len(low_stock_products)} low stock products")
        
        # Check if sede information is included
        sede_info_found = False
        for product in low_stock_products:
            print(f"\nProduct: {product.get('nombre', 'Unknown')}")
            print(f"  Stock: {product.get('stock_actual', 'Unknown')}")
            print(f"  Sede ID: {product.get('sede_id', 'Missing')}")
            print(f"  Sede Name: {product.get('sede_nombre', 'Missing')}")
            
            if 'sede_id' in product and 'sede_nombre' in product:
                sede_info_found = True
        
        print("\n=== CONCLUSION ===")
        if sede_info_found:
            print("✅ SUCCESS: Business data includes sede information for low stock products!")
            print("   The AI analytics should now be able to provide location details.")
        else:
            print("❌ FAILURE: Business data is missing sede information.")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_business_summary_data()