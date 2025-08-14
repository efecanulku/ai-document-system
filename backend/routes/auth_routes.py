from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from functools import wraps
import jwt

# Models import
from models.database import db, Company, User

# Blueprint oluştur
auth_bp = Blueprint('auth', __name__)

def generate_token(user_id, company_id):
    """JWT token oluştur"""
    payload = {
        'user_id': user_id,
        'company_id': company_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, 'dev-secret', algorithm='HS256')

def verify_token(token):
    """JWT token doğrula"""
    try:
        return jwt.decode(token, 'dev-secret', algorithms=['HS256'])
    except:
        return None

def token_required(f):
    """Token decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Token gerekli'}), 401
        
        token = token[7:]  # "Bearer " kısmını çıkar
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Geçersiz token'}), 401
        
        request.user_id = payload['user_id']
        request.company_id = payload['company_id']
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı girişi"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email ve şifre gerekli'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Geçersiz email veya şifre'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Hesap aktif değil'}), 401
        
        token = generate_token(user.id, user.company_id)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Giriş başarılı',
            'token': token,
            'user': user.to_dict(),
            'company': user.company.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': 'Giriş yapılırken hata oluştu'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Kayıt"""
    try:
        data = request.get_json()
        required = ['companyName', 'companyEmail', 'username', 'userEmail', 'password']
        
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} gerekli'}), 400
        
        if Company.query.filter_by(email=data['companyEmail']).first():
            return jsonify({'error': 'Bu şirket emaili zaten kayıtlı'}), 400
        
        company = Company(name=data['companyName'], email=data['companyEmail'])
        db.session.add(company)
        db.session.flush()
        
        user = User(
            username=data['username'],
            email=data['userEmail'],
            company_id=company.id,
            role='admin'
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Kayıt başarılı',
            'company': company.to_dict(),
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Kayıt olurken hata oluştu'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Çıkış"""
    return jsonify({'message': 'Çıkış başarılı'})

@auth_bp.route('/me')
@token_required
def me():
    """Kullanıcı bilgisi"""
    user = User.query.get(request.user_id)
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
    return jsonify({
        'user': user.to_dict(),
        'company': user.company.to_dict()
    })
