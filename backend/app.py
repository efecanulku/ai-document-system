import os, logging
from flask import Flask, jsonify
from flask_cors import CORS

from config import config
from models.database import db  # db + modeller bu pakette

import logging

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Flask & Config ---
app = Flask(__name__)
CORS(app, origins=['http://localhost:8000','http://127.0.0.1:8000'], supports_credentials=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# DB init
db.init_app(app)

# Klasör oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Blueprints ---
from routes.auth_routes import auth_bp
from routes.document_routes import documents_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(documents_bp, url_prefix='/api/documents')

# --- Basic routes ---
@app.route('/')
def home():
    return jsonify({'message':'Döküman Yönetim Sistemi API','status':'active'})

@app.route('/health')
def health():
    return jsonify({'status':'healthy'})

# --- Create tables and demo data ---
def create_tables():
    with app.app_context():
        db.create_all()
        # demo şirket/kullanıcı yoksa ekle
        from models.database import Company, User
        if not Company.query.first():
            c = Company(name='Demo Şirket', email='demo@company.com')
            db.session.add(c); db.session.commit()
            u = User(username='admin', email='admin@demo.com', company_id=c.id, role='admin')
            u.set_password('123456')
            db.session.add(u); db.session.commit()
            app.logger.info("Demo kullanıcı eklendi: admin@demo.com / 123456")

if __name__ == '__main__':
    create_tables()
    print(f"DB URI => {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(host='0.0.0.0', port=5000, debug=True)
