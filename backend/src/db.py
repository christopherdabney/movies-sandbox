import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import IntegrityError

def connect():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'movies_dev'),
        user=os.getenv('DB_USER', os.getenv('USER')),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor  # Returns dict-like rows (like sqlite3.Row)
    )
    return conn

def init_db():
    """Initialize database"""
    conn = connect()
    try:
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        cursor.execute(schema)
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()