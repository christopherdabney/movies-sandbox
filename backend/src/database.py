from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions without app
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database and migrations with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
