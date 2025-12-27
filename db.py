import sqlite3
from datetime import datetime
import contextlib

DB_NAME = "drowsiness_logs.db"

@contextlib.contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10) # Added timeout for concurrency
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()

        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                is_admin INTEGER DEFAULT 0
            )
        ''')

        # Create logs table
        c.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_id INTEGER,
                ear REAL,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Create settings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        conn.commit()

def fetch_users():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, is_admin FROM users")
        return c.fetchall()

def authenticate_user(username, password):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, is_admin FROM users WHERE username=? AND password=?", (username, password))
        return c.fetchone()

def add_user(username, password, is_admin=0):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, is_admin))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def delete_user(username):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()

def ensure_default_admin():
    if not authenticate_user("admin", "admin123"):
        add_user("admin", "admin123", is_admin=1)

def log_detection(user_id, ear, status):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO logs (timestamp, user_id, ear, status) VALUES (?, ?, ?, ?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, ear, status))
        conn.commit()

def fetch_user_stats(user_id):
    with get_db_connection() as conn:
        c = conn.cursor()

        c.execute("SELECT username FROM users WHERE id=?", (user_id,))
        res = c.fetchone()
        if not res:
            return None # Handle case where user doesn't exist?
        username = res[0]

        c.execute("SELECT COUNT(*) FROM logs WHERE user_id=?", (user_id,))
        total_logs = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM logs WHERE user_id=? AND status='Drowsy'", (user_id,))
        drowsy_logs = c.fetchone()[0]

        c.execute("SELECT MAX(timestamp) FROM logs WHERE user_id=?", (user_id,))
        last_login = c.fetchone()[0]

    return {
        "username": username,
        "total_logs": total_logs,
        "drowsy_logs": drowsy_logs,
        "last_login": last_login
    }

def get_setting(key, default=None):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = c.fetchone()
        return result[0] if result else default

def set_setting(key, value):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
