import bcrypt
import jwt

from config import Config
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def add_token(response, member_id, secure=False):
    token = jwt.encode({
        'member_id': member_id,
        'exp': datetime.utcnow() + timedelta(minutes=5)
    }, Config.SECRET_KEY, algorithm='HS256')
    response.set_cookie(
        'auth_token',           # Cookie name
        token,                  # JWT token value
        max_age=5*60,           # 5 minutes in seconds
        httponly=True,          # JavaScript can't access it
        secure=secure,            # Only sent over HTTPS (set False for development)
        samesite='Strict',       # CSRF protection
        path='/',
    )
    return response

def remove_token(response, secure=False):
    response.set_cookie(
        'auth_token', 
        '',                    # Empty value
        max_age=0,            # Expire immediately
        httponly=True,
        secure=secure,         # Match your login settings
        samesite='Strict',
        path='/',
    )
    return response

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
            
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            member_id = data['member_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(member_id, *args, **kwargs)
    return decorated

def token_optional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('auth_token')
        member_id = None
        
        if token:
            try:
                data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
                member_id = data['member_id']
            except:
                # Token invalid or expired - just continue with None
                pass
        
        return f(member_id=member_id, *args, **kwargs)
    
    return decorated