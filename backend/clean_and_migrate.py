#!/usr/bin/env python3
"""
PostgreSQL tabloları temizle ve veri taşı
"""
import psycopg2
import subprocess

def clean_postgres():
    """PostgreSQL tablolarını temizle"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='document_system',
            user='postgres',
            password='1234'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🧹 PostgreSQL tabloları temizleniyor...")
        
        # Tabloları sil (FK sırası önemli)
        tables = [
            'chat_messages',
            'chat_sessions', 
            'document_contents',
            'documents',
            'users', 
            'companies'
        ]
        
        for table in tables:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"   🗑️ {table} silindi")
        
        cur.close()
        conn.close()
        
        print("✅ Temizlik tamamlandı")
        return True
        
    except Exception as e:
        print(f"❌ Temizlik hatası: {e}")
        return False

if __name__ == "__main__":
    print("🧹 PostgreSQL Temizlik ve Geçiş")
    print("=" * 35)
    
    if clean_postgres():
        print("\n📋 Tabloları yeniden oluşturuluyor...")
        subprocess.run(['python', 'create_tables.py'])
        
        print("\n📦 Verileri taşınıyor...")
        subprocess.run(['python', 'migrate_to_postgres.py'])
    else:
        print("\n❌ Temizlik başarısız!")

