import requests
import os
from dotenv import load_dotenv

# Replace with your Bot Token and Chat ID
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_alert(message):
    """
    Sends a Telegram message using the Bot API.
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram alert sent successfully!")
        else:
            print(f"❌ Failed to send Telegram alert: {response.text}")
    except Exception as e:
        print(f"❌ Telegram alert failed: {e}")

# Test directly from this file
if __name__ == "__main__":
    send_telegram_alert("🚨 Test Alert: Drowsiness Alert System is working!")
