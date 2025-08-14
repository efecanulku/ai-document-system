import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

class DevelopmentConfig(Config):
    DEBUG = True
    # ENV değişkeni varsa onu kullan; yoksa alttaki PG URI
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql+psycopg2://doc_user:1234@localhost:5432/document_system'
    )

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2://user:pass@host:5432/dbname'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
