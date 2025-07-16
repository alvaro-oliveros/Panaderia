#!/usr/bin/env python3
"""Simple test for voice chat context"""

from app.database import SessionLocal
from app.routes.voice_chat import build_database_context

db = SessionLocal()
try:
    context = build_database_context(db, user_id=1)
    print("VOICE CHAT CONTEXT:")
    print("=" * 50)
    print(context)
    print("=" * 50)
    
    if "unidades en " in context:
        print("✅ SUCCESS: Context includes sede information!")
    else:
        print("❌ FAILED: No sede information found")
        
finally:
    db.close()