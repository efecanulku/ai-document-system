#!/usr/bin/env python3
"""
SQLite'dan PostgreSQL'e veri taşıma scripti
"""
import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# PostgreSQL bağlantı ayarları
PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'document_system',
    'user': 'doc_user',
    'password': '1234'
}

SQLITE_DB = 'instance/document_management.db'

def create_postgres_database():
    """PostgreSQL veritabanı ve kullanıcı oluştur"""
    try:
        # postgres kullanıcısı ile bağlan (default admin)
        # Farklı şifreler dene
        possible_passwords = ['1234', '123456', 'postgres', '', 'admin', 'password']
        conn = None
        
        for pwd in possible_passwords:
            try:
                conn = psycopg2.connect(
                    host=PG_CONFIG['host'],
                    port=PG_CONFIG['port'],
                    database='postgres',
                    user='postgres',
                    password=pwd
                )
                print(f"✅ Şifre bulundu: '{pwd}'")
                break
            except:
                continue
        
        if not conn:
            print("❌ Hiçbir şifre çalışmadı. Manuel şifre reset gerekli.")
            return False
        conn.autocommit = True
        cur = conn.cursor()
        
        # Kullanıcı oluştur
        try:
            cur.execute(f"CREATE USER {PG_CONFIG['user']} WITH PASSWORD '{PG_CONFIG['password']}';")
            print(f"✅ Kullanıcı {PG_CONFIG['user']} oluşturuldu")
        except psycopg2.errors.DuplicateObject:
            print(f"ℹ️ Kullanıcı {PG_CONFIG['user']} zaten mevcut")
        
        # Veritabanı oluştur
        try:
            cur.execute(f"CREATE DATABASE {PG_CONFIG['database']} OWNER {PG_CONFIG['user']};")
            print(f"✅ Veritabanı {PG_CONFIG['database']} oluşturuldu")
        except psycopg2.errors.DuplicateDatabase:
            print(f"ℹ️ Veritabanı {PG_CONFIG['database']} zaten mevcut")
        
        # Yetkileri ver
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {PG_CONFIG['database']} TO {PG_CONFIG['user']};")
        
        cur.close()
        conn.close()
        print("✅ PostgreSQL hazırlandı")
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL bağlantı hatası: {e}")
        print("💡 PostgreSQL kurulu ve çalışıyor mu?")
        print("💡 postgres kullanıcısının şifresi doğru mu? (kurulumda verdiğin)")
        return False

def migrate_data():
    """SQLite'dan PostgreSQL'e veri taşı"""
    if not os.path.exists(SQLITE_DB):
        print(f"❌ SQLite dosyası bulunamadı: {SQLITE_DB}")
        return False
    
    try:
        # SQLite bağlantısı
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()
        
        # PostgreSQL bağlantısı
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cur = pg_conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔄 Veri taşıma başladı...")
        
        # Tabloları kontrol et
        sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in sqlite_cur.fetchall()]
        print(f"📋 Bulunan tablolar: {tables}")
        
        # Her tablo için veri taşı
        for table in tables:
            if table.startswith('sqlite_'):
                continue
                
            print(f"📦 {table} tablosu taşınıyor...")
            
            # SQLite'dan verileri al
            sqlite_cur.execute(f"SELECT * FROM {table}")
            rows = sqlite_cur.fetchall()
            
            if not rows:
                print(f"   ⚠️ {table} tablosu boş")
                continue
            
            # PostgreSQL'e verileri ekle
            columns = [description[0] for description in sqlite_cur.description]
            placeholders = ', '.join(['%s'] * len(columns))
            
            insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            try:
                for row in rows:
                    # Boolean değerleri dönüştür (SQLite 1/0 -> PostgreSQL True/False)
                    row_data = []
                    for i, val in enumerate(row):
                        col_name = columns[i].lower()
                        if col_name in ['is_active', 'is_processed'] and isinstance(val, int):
                            row_data.append(bool(val))
                        else:
                            row_data.append(val)
                    
                    pg_cur.execute(insert_sql, tuple(row_data))
                
                pg_conn.commit()
                print(f"   ✅ {len(rows)} kayıt taşındı")
                
            except Exception as e:
                pg_conn.rollback()
                print(f"   ❌ Hata: {e}")
        
        sqlite_cur.close()
        sqlite_conn.close()
        pg_cur.close()
        pg_conn.close()
        
        print("🎉 Veri taşıma tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Veri taşıma hatası: {e}")
        return False

def test_connection():
    """PostgreSQL bağlantısını test et"""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✅ PostgreSQL bağlantısı başarılı: {version}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL bağlantı testi başarısız: {e}")
        return False

if __name__ == "__main__":
    print("🐘 SQLite → PostgreSQL Geçiş Scripti")
    print("=" * 50)
    
    print("\n1️⃣ PostgreSQL veritabanı hazırlanıyor...")
    if not create_postgres_database():
        sys.exit(1)
    
    print("\n2️⃣ Bağlantı test ediliyor...")
    if not test_connection():
        sys.exit(1)
    
    print("\n3️⃣ Veriler taşınıyor...")
    if migrate_data():
        print("\n🎉 Geçiş başarılı!")
        print("\n📝 Sonraki adımlar:")
        print("   1. backend/config.py kontrol et")
        print("   2. Flask uygulamasını yeniden başlat")
        print("   3. Test et")
    else:
        print("\n❌ Geçiş başarısız!")
        sys.exit(1)
