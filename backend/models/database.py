from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Company(db.Model):
    """Şirket modeli"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # İlişkiler
    users = db.relationship('User', backref='company', lazy=True)
    documents = db.relationship('Document', backref='company', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class User(db.Model):
    """Kullanıcı modeli"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Benzersizlik kısıtı - aynı şirkette aynı email/username olamaz
    __table_args__ = (
        db.UniqueConstraint('email', 'company_id', name='unique_email_per_company'),
        db.UniqueConstraint('username', 'company_id', name='unique_username_per_company'),
    )
    
    def set_password(self, password):
        """Şifreyi hashle ve kaydet"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifreyi kontrol et"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'company_id': self.company_id,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

class Document(db.Model):
    """Döküman modeli"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processed = db.Column(db.Boolean, default=False)
    
    # İlişkiler
    uploader = db.relationship('User', backref='uploaded_documents')
    content = db.relationship('DocumentContent', backref='document', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'company_id': self.company_id,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_processed': self.is_processed
        }

class DocumentContent(db.Model):
    """Döküman içerik modeli"""
    __tablename__ = 'document_contents'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), default='text')  # text, ocr
    page_number = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'content': self.content,
            'content_type': self.content_type,
            'page_number': self.page_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatSession(db.Model):
    """Chat oturum modeli"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(200), default='Yeni Sohbet')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    user = db.relationship('User', backref='chat_sessions')
    messages = db.relationship('ChatMessage', backref='session', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ChatMessage(db.Model):
    """Chat mesaj modeli"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    message_type = db.Column(db.String(20), default='user')  # user, assistant
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message': self.message,
            'response': self.response,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


