#!/usr/bin/env python3
"""
Import test
"""
try:
    print("1. Flask import...")
    from flask import Blueprint
    print("✅ Flask OK")
    
    print("2. Models import...")
    from models.database import db, User, Company
    print("✅ Models OK")
    
    print("3. Auth routes import...")
    import routes.auth_routes
    print("✅ Auth routes module OK")
    
    print("4. Auth_bp import...")
    from routes.auth_routes import auth_bp
    print("✅ Auth_bp OK")
    
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
