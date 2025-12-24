import sqlite3
from datetime import datetime

DB_NAME = "drowsiness_logs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn.close()

def fetch_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, is_admin FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, is_admin FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, is_admin=0):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, is_admin))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_user(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def ensure_default_admin():
    if not authenticate_user("admin", "admin123"):
        add_user("admin", "admin123", is_admin=1)

def log_detection(user_id, ear, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, user_id, ear, status) VALUES (?, ?, ?, ?)",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, ear, status))
    conn.commit()
    conn.close()

def fetch_user_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    username = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM logs WHERE user_id=?", (user_id,))
    total_logs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM logs WHERE user_id=? AND status='Drowsy'", (user_id,))
    drowsy_logs = c.fetchone()[0]

    c.execute("SELECT MAX(timestamp) FROM logs WHERE user_id=?", (user_id,))
    last_login = c.fetchone()[0]

    conn.close()

    return {
        "username": username,
        "total_logs": total_logs,
        "drowsy_logs": drowsy_logs,
        "last_login": last_login
    }

def get_setting(key, default=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else default

def set_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
