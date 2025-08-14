#!/usr/bin/env python3
"""
PostgreSQL kullanıcı şifresini düzelt
"""
import psycopg2

def fix_user_password():
    """doc_user şifresini 1234 yap"""
    try:
        # postgres admin ile bağlan
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='postgres',
            password='1234'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🔧 doc_user şifresini düzeltiliyor...")
        
        # Kullanıcı şifresini değiştir
        cur.execute("ALTER USER doc_user WITH PASSWORD '1234';")
        print("✅ doc_user şifresi '1234' olarak ayarlandı")
        
        # Veritabanı yetkilerini kontrol et
        cur.execute("GRANT ALL PRIVILEGES ON DATABASE document_system TO doc_user;")
        print("✅ Yetkiler verildi")
        
        cur.close()
        conn.close()
        
        # Test bağlantısı
        test_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='document_system',
            user='doc_user',
            password='1234'
        )
        test_conn.close()
        print("✅ Test bağlantısı başarılı!")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    print("🔧 PostgreSQL Kullanıcı Düzeltme")
    print("=" * 35)
    
    if fix_user_password():
        print("\n🎉 Hazır! Şimdi migrate_to_postgres.py çalıştır")
    else:
        print("\n❌ Düzeltme başarısız!")

