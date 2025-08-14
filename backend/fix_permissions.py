#!/usr/bin/env python3
"""
PostgreSQL yetkileri düzelt
"""
import psycopg2

def fix_permissions():
    """doc_user'a tüm yetkileri ver"""
    try:
        # postgres admin ile bağlan
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='document_system',
            user='postgres',
            password='1234'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🔧 Yetkileri düzeltiliyor...")
        
        # Schema yetkilerini ver
        cur.execute("GRANT ALL ON SCHEMA public TO doc_user;")
        cur.execute("GRANT ALL PRIVILEGES ON DATABASE document_system TO doc_user;")
        cur.execute("ALTER USER doc_user CREATEDB;")  # Database oluşturma yetkisi
        
        # Mevcut tabloların yetkilerini ver (varsa)
        cur.execute("""
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'GRANT ALL PRIVILEGES ON TABLE ' || quote_ident(r.tablename) || ' TO doc_user';
                END LOOP;
            END
            $$;
        """)
        
        # Sequence'ların yetkilerini ver
        cur.execute("""
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
                    EXECUTE 'GRANT ALL PRIVILEGES ON SEQUENCE ' || quote_ident(r.sequence_name) || ' TO doc_user';
                END LOOP;
            END
            $$;
        """)
        
        print("✅ Tüm yetkiler verildi")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    print("🔧 PostgreSQL Yetki Düzeltme")
    print("=" * 30)
    
    if fix_permissions():
        print("\n🎉 Yetkiler düzeltildi! Şimdi create_tables.py çalıştır")
    else:
        print("\n❌ Yetki düzeltme başarısız!")

