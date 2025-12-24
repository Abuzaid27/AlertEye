# log_handler.py

import sqlite3
from datetime import datetime
from db import DB_NAME

def log_event(ear, status, user_id):
    # Only log if it's Drowsy
    if status != "Drowsy":
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO logs (timestamp, ear, status, user_id) VALUES (?, ?, ?, ?)",
        (datetime.now(), ear, status, user_id)
    )
    conn.commit()
    conn.close()
