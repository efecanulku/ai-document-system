@echo off
echo PostgreSQL Kurulum Kontrolu
echo ===============================

echo 1. PostgreSQL servisini kontrol et...
sc query postgresql*

echo.
echo 2. PostgreSQL versiyonu...
"C:\Program Files\PostgreSQL\15\bin\psql.exe" --version 2>nul
if errorlevel 1 (
    echo PostgreSQL bulunamadi. Kurulum yap:
    echo https://www.postgresql.org/download/windows/
    pause
    exit
)

echo.
echo 3. Test baglantisi...
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d postgres -c "SELECT version();" 2>nul
if errorlevel 1 (
    echo Baglanti basarisiz. Sifre: 123456 olarak ayarla
)

echo.
echo 4. Veritabani ve kullanici olustur...
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d postgres -c "CREATE USER doc_user WITH PASSWORD '123456';" 2>nul
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d postgres -c "CREATE DATABASE document_system OWNER doc_user;" 2>nul
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE document_system TO doc_user;" 2>nul

echo.
echo PostgreSQL hazir! Simdi Python scriptini calistir:
echo python migrate_to_postgres.py
pause

