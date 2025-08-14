# Döküman Yönetim Sistemi

AI destekli döküman yönetim sistemi - belgelerden öğrenen yapay zeka chatbotu ile.

## Özellikler

- 🤖 **AI Chatbot**: Belgelerden öğrenen yapay zeka asistanı
- 📄 **Çoklu Dosya Desteği**: PDF, Word, Excel, resim dosyaları
- 🔍 **OCR**: Resimlerden metin çıkarma
- 🏢 **Çok Kiracılı**: Her şirket kendi belgelerini yönetir
- 🔐 **Güvenlik**: Kullanıcı girişi ve yetkilendirme
- 🔎 **Akıllı Arama**: Belgelerde AI destekli arama
- 🌐 **Web Arayüzü**: Modern ve kullanıcı dostu arayüz

## Teknoloji Yığını

### Backend
- **Python** (Flask)
- **PostgreSQL** (Veritabanı)
- **LangChain** (AI Framework)
- **ChromaDB** (Vektör Veritabanı)
- **Tesseract OCR** (Metin çıkarma)

### Frontend
- **HTML5/CSS3/JavaScript**
- **Bootstrap 5**
- **Font Awesome**

### AI/ML
- **OpenAI GPT** (Chatbot)
- **Sentence Transformers** (Embedding)
- **PyPDF2** (PDF okuma)
- **python-docx** (Word dosyaları)

## Kurulum

### Gereksinimler
- Python 3.8+
- PostgreSQL 12+
- Tesseract OCR

### 1. Proje Klonlama
\`\`\`bash
git clone <repo-url>
cd DocumentManagementSystem
\`\`\`

### 2. Python Sanal Ortamı
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\\Scripts\\activate  # Windows
\`\`\`

### 3. Bağımlılıkları Yükleme
\`\`\`bash
cd backend
pip install -r requirements.txt
\`\`\`

### 4. Veritabanı Kurulumu
\`\`\`bash
# PostgreSQL veritabanı oluştur
createdb document_management_dev

# Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle
\`\`\`

### 5. Tesseract OCR Kurulumu

#### Windows:
1. [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) indir ve kur
2. Path'i .env dosyasına ekle: \`TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe\`

#### Linux:
\`\`\`bash
sudo apt-get install tesseract-ocr tesseract-ocr-tur
\`\`\`

#### Mac:
\`\`\`bash
brew install tesseract
\`\`\`

### 6. Uygulamayı Çalıştırma
\`\`\`bash
# Backend
cd backend
python app.py

# Frontend (ayrı terminal)
cd frontend
python -m http.server 8000
# veya
npx serve .
\`\`\`

Uygulama şu adreslerde çalışacak:
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000

## Geliştirme Planı

### 1-3. Günler: Temel Altyapı ✅
- [x] Proje yapısı kurulumu
- [x] Temel Flask uygulaması
- [x] Veritabanı modelleri
- [x] Temel web arayüzü

### 4-6. Günler: Dosya İşleme
- [ ] Dosya yükleme API'si
- [ ] PDF/Word/Excel okuyucuları
- [ ] OCR entegrasyonu
- [ ] Metin çıkarma ve saklama

### 7-9. Günler: AI Chatbot
- [ ] LangChain kurulumu
- [ ] Vektör veritabanı entegrasyonu
- [ ] Belge indeksleme
- [ ] Chatbot API'si

### 10-12. Günler: Gelişmiş Özellikler
- [ ] Akıllı arama sistemi
- [ ] Çok kiracılı yapı
- [ ] Güvenlik iyileştirmeleri
- [ ] Performans optimizasyonu

### 13-15. Günler: Test ve Deployment
- [ ] Unit testler
- [ ] Integration testler
- [ ] UI/UX iyileştirmeleri
- [ ] Production deployment

## API Endpoints

### Kimlik Doğrulama
- \`POST /api/auth/login\` - Giriş yap
- \`POST /api/auth/register\` - Kayıt ol
- \`POST /api/auth/logout\` - Çıkış yap

### Belgeler
- \`GET /api/documents\` - Belge listesi
- \`POST /api/documents/upload\` - Belge yükle
- \`GET /api/documents/{id}\` - Belge detayı
- \`DELETE /api/documents/{id}\` - Belge sil

### Chat
- \`GET /api/chat/sessions\` - Chat oturumları
- \`POST /api/chat/message\` - Mesaj gönder
- \`GET /api/chat/history/{session_id}\` - Chat geçmişi

### Arama
- \`POST /api/search\` - Belgelerde arama
- \`GET /api/search/suggestions\` - Arama önerileri

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (\`git checkout -b feature/amazing-feature\`)
3. Commit yapın (\`git commit -m 'Add amazing feature'\`)
4. Push yapın (\`git push origin feature/amazing-feature\`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altındadır.

## İletişim

Proje ile ilgili sorularınız için issue oluşturabilirsiniz.


