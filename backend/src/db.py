import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import IntegrityError

DUPLICATE_ERROR = 'Duplicate Member record attempted'

class DuplicateError(Exception):
    """Raised when a duplicate key is detected"""
    pass

def connect():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'pagine_dev'),
        user=os.getenv('DB_USER', os.getenv('USER')),  # Uses your system username
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor  # Returns dict-like rows (like sqlite3.Row)
    )
    return conn

def get_user(id):
    conn = connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM member WHERE id = %s
            """, 
            (id,)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def login(email):
    conn = connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM member WHERE email = %s
            """, 
            (email,)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def insert(email, password_hash, first_name, last_name):
    conn = connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO member (email, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """, 
            (email, password_hash, first_name, last_name)
        )
        record_id = cursor.fetchone()['id']
        conn.commit()
        return record_id
    except IntegrityError:
        raise DuplicateError(DUPLICATE_ERROR)
    finally:
        conn.close()

# Initialize database (create tables)
def init_db():
    """Initialize database with required tables"""
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