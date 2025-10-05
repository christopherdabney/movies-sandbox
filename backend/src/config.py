import os

class Config:
    """Base configuration"""
    
    # Database
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER', os.getenv('USER'))}:"
        f"{os.getenv('DB_PASSWORD', '')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'pagine_dev')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT/Auth
    SECRET_KEY = os.getenv('SECRET_KEY', 'my-super-secret-jwt-key-for-development-only')
    
    # CORS
    CORS_ORIGINS = ['http://localhost:5173']

    # chat expiry pushes old chats to active=False
    # this does not delete them, but it removes them from Claude AI api conversation context
    CHAT_EXPIRY_MINUTES = int(os.environ.get('CHAT_EXPIRY_MINUTES', 2))