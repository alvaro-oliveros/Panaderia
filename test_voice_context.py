#!/usr/bin/env python3
"""
Test script to verify voice chat context includes sede information
"""

import sys
import os
sys.path.append('backend')

from backend.app.database import SessionLocal
from backend.app.routes.voice_chat import build_database_context

def test_voice_context():
    """Test that voice chat context includes sede information for low stock products"""
    
    db = SessionLocal()
    try:
        # Build context for admin user (user_id=1)
        context = build_database_context(db, user_id=1)
        
        print("=== VOICE CHAT CONTEXT ===")
        print(context)
        print("\n=== ANALYSIS ===")
        
        # Check if context includes sede information
        if "unidades en " in context:
            print("✅ PASS: Context includes sede information ('unidades en')")
            
            # Extract low stock products section
            lines = context.split('\n')
            for line in lines:
                if "PRODUCTOS CON STOCK BAJO" in line:
                    continue
                if "unidades en " in line:
                    print(f"   📦 {line.strip()}")
        else:
            print("❌ FAIL: Context does not include sede information")
            
        print("\n=== CONCLUSION ===")
        if "unidades en " in context:
            print("✅ The voice chat context correctly includes sede information!")
            print("   When users ask about low stock, they will see location details.")
        else:
            print("❌ The voice chat context is missing sede information.")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_voice_context()