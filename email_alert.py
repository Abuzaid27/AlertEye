

# email_alert.py
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

# Update these values:
load_dotenv()

SENDER_EMAIL= os.getenv("SENDER_EMAIL")
ADMIN_EMAIL= os.getenv("ADMIN_EMAIL")
PASSWORD=os.getenv("PASSWORD")

# Choose email service: 'gmail', 'outlook', 'yahoo'
EMAIL_SERVICE = "gmail"

def get_smtp_details(service):
    if service == "gmail":
        return ("smtp.gmail.com", 465, True)
    elif service == "outlook":
        return ("smtp.office365.com", 587, False)
    elif service == "yahoo":
        return ("smtp.mail.yahoo.com", 465, True)
    else:
        raise ValueError("Unsupported email service")

def send_email_alert(status):
    try:
        smtp_server, port, use_ssl = get_smtp_details(EMAIL_SERVICE)
        msg = MIMEText(f"⚠️ Alert! Drowsiness detected. Status: {status}")
        msg['Subject'] = "Drowsiness Alert"
        msg['From'] = SENDER_EMAIL
        msg['To'] = ADMIN_EMAIL

        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, port)
        else:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()

        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email alert sent successfully!")
        return True

    except Exception as e:
        print(f"⚠️ Email sending failed: {e}")
        return False
