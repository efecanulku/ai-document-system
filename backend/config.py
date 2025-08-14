import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    """Temel konfigürasyon sınıfı"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dosya yükleme ayarları
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # AI ayarları
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    
    # OCR ayarları
    TESSERACT_PATH = os.environ.get('TESSERACT_PATH') or '/usr/bin/tesseract'

class DevelopmentConfig(Config):
    """Geliştirme ortamı konfigürasyonu"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///document_management.db'

class ProductionConfig(Config):
    """Üretim ortamı konfigürasyonu"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/document_management_prod'

class TestingConfig(Config):
    """Test ortamı konfigürasyonu"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Konfigürasyon seçimi
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

