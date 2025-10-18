import bcrypt
import jwt
import os
import secrets

from datetime import date, datetime, timedelta
from config import Config
from functools import wraps
from flask import request, jsonify

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

AUTHENTICATION_COOKIE = 'auth_token'
AUTHENTICATION_LIFETIME = 30  # minutes

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def add_token(response, member_id, secure=False):
    token = jwt.encode({
        'member_id': member_id,
        'exp': datetime.utcnow() + timedelta(minutes=AUTHENTICATION_LIFETIME)
    }, Config.SECRET_KEY, algorithm='HS256')
    response.set_cookie(
        AUTHENTICATION_COOKIE,              # Cookie name
        token,                              # JWT token value
        max_age=AUTHENTICATION_LIFETIME*60,
        httponly=True,                      # httponly cookies are safe from javascript
        secure=secure,                      # Only sent over HTTPS (set False for development)
        samesite='Strict',                  # CSRF protection
        path='/',
    )
    return response

def remove_token(response, secure=False):
    response.set_cookie(
        AUTHENTICATION_COOKIE, 
        '',                                 # kill token
        max_age=0,                          # expire immediately
        httponly=True,
        secure=secure,
        samesite='Strict',
        path='/',
    )
    return response


def send_verification_email(member):
    token = secrets.token_urlsafe(32)
    member.verification_token = token
    member.token_expires_at = datetime.utcnow() + timedelta(hours=10)  #TODO: hardcoded expiry
    
    # Construct verification link
    verification_link = f"http://localhost:5173/verify-email/{token}"  # TODO: hardcoded URL
    print(verification_link)

    # After user is created in DB
    message = Mail(
        from_email='noreply@dabneystudios.com',
        to_emails=member.email,
        subject='Welcome! Verify your email address.',
        html_content=f'''                                               # TODO jinja html template
            <h2>Welcome to Movie App!</h2>
            <p>Please verify your email address by clicking the link below:</p>
            <a href="{verification_link}">Verify Email</a>
            <p>This link expires in 24 hours.</p>
        '''
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent: {response.status_code}")  # Email sent: 202
    except Exception as e:
        print(f"Error sending email: {e}")



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get(AUTHENTICATION_COOKIE)
        
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
        token = request.cookies.get(AUTHENTICATION_COOKIE)
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