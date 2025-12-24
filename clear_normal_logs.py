import sqlite3

conn = sqlite3.connect("drowsiness_logs.db")  # Use your DB name
cursor = conn.cursor()
cursor.execute("DELETE FROM logs WHERE status='Normal'")
conn.commit()
conn.close()
print("All 'Normal' logs removed.")
