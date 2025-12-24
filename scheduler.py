import scheduler
import time
from db import DB_NAME
import sqlite3
from email_alert import send_email_alert
from telegram_alert import send_telegram_alert
from datetime import datetime

def send_admin_summary():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Summary stats
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

    top_users_str = "\n".join([f"{user}: {count} logs" for user, count in top_users])

    message = (
        f"📊 **Drowsiness System Daily Report ({datetime.now().date()})**\n\n"
        f"📝 Total Logs: {total_logs}\n"
        f"⚠️ Drowsy Events: {drowsy_events}\n\n"
        f"🏆 Top Users:\n{top_users_str if top_users else 'No users found'}"
    )

    # Send to admin
    send_email_alert(message)
    send_telegram_alert(message)

    print("✅ Summary sent to admin")

# Schedule job (runs every day at 20:00)
scheduler.every().day.at("20:00").do(send_admin_summary)

def run_scheduler():
    while True:
        scheduler.run_pending()
        time.sleep(60)
