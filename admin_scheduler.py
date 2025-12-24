import sqlite3
from datetime import datetime
import time
import threading
import schedule

from db import DB_NAME, get_setting
from email_alert import send_email_alert
from telegram_alert import send_telegram_alert

def send_admin_summary():
    """Send a daily summary to admin"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM logs")
    total_logs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM logs WHERE status='Drowsy'")
    drowsy_events = c.fetchone()[0]

    c.execute("""
        SELECT u.username, COUNT(l.id) as logs
        FROM users u
        LEFT JOIN logs l ON u.id = l.user_id
        GROUP BY u.username
        ORDER BY logs DESC
        LIMIT 3
    """)
    top_users = c.fetchall()
    conn.close()

    top_users_str = "\n".join([f"{user}: {count} logs" for user, count in top_users]) if top_users else "No users"

    message = (
        f"📊 Drowsiness System Daily Report ({datetime.now().date()})\n\n"
        f"📝 Total Logs: {total_logs}\n"
        f"⚠️ Drowsy Events: {drowsy_events}\n\n"
        f"🏆 Top Users:\n{top_users_str}"
    )

    send_email_alert(message)
    send_telegram_alert(message)
    print("✅ Daily summary sent to admin")

def run_scheduler():
    """Run scheduler based on settings"""
    while True:
        enabled = get_setting("scheduler_enabled", "1") == "1"
        time_str = get_setting("scheduler_time", "20:00")

        schedule.clear()

        if enabled:
            schedule.every().day.at(time_str).do(send_admin_summary)

        while True:
            schedule.run_pending()
            time.sleep(60)
