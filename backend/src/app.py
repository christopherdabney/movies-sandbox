from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_caching import Cache
from services.recommendations import RecommendationsService

# Load environment variables from .env file
load_dotenv()

from config import Config
from database import init_db
from routes import membership_bp, movies_bp, watchlist_bp, chat_bp

app = Flask(__name__)

app.config.from_object(Config)

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600
})
RecommendationsService.cache = cache

init_db(app)

# Allow requests from React dev server
#CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
CORS(
    app, 
    origins=Config.CORS_ORIGINS, 
    supports_credentials=True,
    allow_headers=['Content-Type'],
    methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
)

app.register_blueprint(membership_bp)
app.register_blueprint(movies_bp)
app.register_blueprint(watchlist_bp)
app.register_blueprint(chat_bp)

# Import models for Flask-Migrate (safe now - no circular imports)
# Todo - can we movie this to top for imports?
# or perhaps even remove them?
from models import Member, Movie, ChatMessage

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found or invalid parameter format'}), 404

@app.route('/')
def status():
    return "200 OK"

if __name__ == '__main__':
    app.run(debug=True)