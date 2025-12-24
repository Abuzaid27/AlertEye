# Drowsiness Alert System

## 📌 Objective
A real-time drowsiness detection system using Python, Streamlit, and SQLite3. It monitors user's eye aspect ratio (EAR) through webcam feed and triggers alerts when drowsiness is detected.

---

## 🛠️ Tech Stack
- Frontend: **Streamlit**
- Backend: **OpenCV**, **Dlib**, **Imutils**
- Database: **SQLite3**
- Email Notifications: **smtplib**
- Logging: **Python logging module**

---

## ⚡ Features
- Real-time webcam detection
- Eye Aspect Ratio (EAR) calculation
- Sound + Email alert when drowsy
- Logs all events in SQLite database
- Admin panel to view/download logs (CSV)
- (Optional) User login & graphs

---

## 🔧 Installation

1. Clone the project or copy the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
