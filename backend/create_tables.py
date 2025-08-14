#!/usr/bin/env python3
"""
PostgreSQL'de tabloları oluştur
"""
import os
from flask import Flask
from config import config
from models.database import db, Company, User

# Flask app oluştur
app = Flask(__name__)

# Config yükle
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# DB başlat
db.init_app(app)

def create_tables():
    """Tabloları oluştur"""
    with app.app_context():
        print("🏗️ PostgreSQL tabloları oluşturuluyor...")
        print(f"📍 DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Tabloları oluştur
        db.create_all()
        print("✅ Tablolar oluşturuldu!")
        
        # Demo veri eklenmişse kontrol et
        if not Company.query.first():
            # Demo şirket
            c = Company(name='Demo Şirket', email='demo@company.com')
            db.session.add(c)
            db.session.commit()
            
            # Demo kullanıcı
            u = User(username='admin', email='admin@demo.com', company_id=c.id, role='admin')
            u.set_password('123456')
            db.session.add(u)
            db.session.commit()
            
            print("✅ Demo veriler eklendi!")
            print("📝 Giriş: admin@demo.com / 123456")
        else:
            print("ℹ️ Demo veriler zaten mevcut")

if __name__ == "__main__":
    create_tables()

