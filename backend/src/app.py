from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config import Config
from database import init_db
from routes import membership_bp, movies_bp, watchlist_bp

app = Flask(__name__)
app.config.from_object(Config)

init_db(app)

# Allow requests from React dev server
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

app.register_blueprint(membership_bp)
app.register_blueprint(movies_bp)
app.register_blueprint(watchlist_bp)

# Import models for Flask-Migrate (safe now - no circular imports)
from models import Member, Movie

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found or invalid parameter format'}), 404

@app.route('/')
def status():
    return "200 OK"

if __name__ == '__main__':
    app.run(debug=True)