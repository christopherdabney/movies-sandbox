import os
import sqlite3

DATABASE = 'member.db'
DUPLICATE_ERROR = 'Duplicate Member record attempted'

class DuplicateError(Exception):
    """Raised when a duplicate key is detected"""
    pass

def db_path():
    return os.environ.get('DATABASE_PATH', DATABASE)

def connect():
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn

def get_user(id):
    conn = connect()
    record = conn.execute(
        """
        SELECT * FROM member WHERE id = ?
        """, 
        (id,)
    ).fetchone()
    conn.close()
    return record

def login(email):
    conn = connect()
    record = conn.execute(
        """
        SELECT * FROM member WHERE email = ?
        """, 
        (email,)
    ).fetchone()
    conn.close()
    return record

def insert(email, password_hash, first_name, last_name):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO member (email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?)
            """, 
            (email, password_hash, first_name, last_name)
        )
        """ reference
        new_id = cursor.lastrowid
        # Then fetch the complete record
        cursor.execute("SELECT * FROM member WHERE id = ?", (new_id,))
        record = cursor.fetchone()
        """
        conn.commit()
    except sqlite3.IntegrityError:
        raise DuplicateError(DUPLICATE_ERROR)
    finally:
        conn.close()