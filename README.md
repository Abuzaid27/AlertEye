# Drowsiness Alert System

## 📌 Objective
A real-time drowsiness detection system using Python, Streamlit, and SQLite3. It monitors user's eye aspect ratio (EAR) and mouth aspect ratio (MAR) through webcam feed and triggers alerts when drowsiness is detected. Includes user authentication, admin dashboard, and automated scheduling features.

---

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Backend:** OpenCV, Dlib, Imutils, NumPy, SciPy
- **Database:** SQLite3
- **Notifications:** Email (smtplib), Telegram Bot API
- **Audio:** SimpleAudio
- **Logging:** Python logging module
- **Visualization:** Plotly, Pandas

---

## ⚡ Features
- **Real-time Detection:** Webcam-based eye and mouth monitoring using facial landmarks
- **Aspect Ratio Calculation:** EAR (Eye Aspect Ratio) and MAR (Mouth Aspect Ratio) for drowsiness detection
- **Multi-modal Alerts:** Sound, Email, and Telegram notifications when drowsy
- **Event Logging:** All detection events stored in SQLite database with timestamps
- **User Authentication:** Login/Signup system with session management
- **Admin Dashboard:** View user statistics, download logs as CSV, manage users
- **Automated Scheduler:** Background task for periodic log cleanup and maintenance
- **Configurable Thresholds:** Adjustable EAR, MAR, and frame check parameters
- **Dark Mode:** UI theme toggle
- **Sound Control:** Enable/disable audio alerts

---

## 📋 Prerequisites
- Python 3.8+
- Webcam
- Dlib shape predictor model file (`shape_predictor_68_face_landmarks.dat` in `models/` folder)
- Environment variables for email and Telegram bot configuration

---

## 🔧 Installation

1. **Clone or Download the Project:**
   ```bash
   git clone <repository-url>
   cd Drowsiness_Alert_System_Final
   ```

2. **Create Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Variables:**
   - Copy `.env` file and update with your credentials:
     - `BOT_TOKEN`: Your Telegram Bot Token
     - `CHAT_ID`: Your Telegram Chat ID
     - `SENDER_EMAIL`: Your email address
     - `ADMIN_EMAIL`: Admin email for notifications
     - `PASSWORD`: Email app password

5. **Download Dlib Model:**
   - Ensure `models/shape_predictor_68_face_landmarks.dat` exists
   - Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   - Extract to `models/` folder

---

## 🚀 Usage

1. **Run the Application:**
   ```bash
   streamlit run main.py
   ```

2. **Access the App:**
   - Open browser at `http://localhost:8501`

3. **User Registration/Login:**
   - New users: Sign up with username and password
   - Existing users: Login with credentials

4. **Detection Mode:**
   - Adjust thresholds in sidebar (EAR: 0.1-0.4, MAR: 0.3-0.7, Frame Check: 10-40)
   - Click "Start Detection" to begin webcam monitoring
   - System will log events and trigger alerts when drowsy

5. **Admin Dashboard (Admin Users Only):**
   - View user statistics and logs
   - Download logs as CSV
   - Manage user accounts

---

## ⚙️ Configuration
- **EAR Threshold:** Lower values increase sensitivity to eye closure (default: 0.25)
- **MAR Threshold:** Lower values increase sensitivity to yawning (default: 0.5)
- **Frame Check:** Number of consecutive frames to confirm drowsiness (default: 20)
- **Alert Cooldown:** 10 seconds between log entries for same event

---

## 📁 Project Structure
```
Drowsiness_Alert_System_Final/
├── main.py                 # Main Streamlit application
├── drowsiness.py           # Drowsiness detection logic
├── db.py                   # Database operations
├── log_handler.py          # Logging utilities
├── email_alert.py          # Email notification system
├── telegram_alert.py       # Telegram bot notifications
├── admin_dashboard.py      # Admin panel components
├── admin_scheduler.py      # Background scheduler tasks
├── scheduler.py            # Additional scheduling
├── create_admin.py         # Admin user creation script
├── clear_normal_logs.py    # Log cleanup utilities
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── models/                 # Dlib model files
├── sounds/                 # Alert sound files
├── assets/                 # Static assets
└── README.md               # This file
```

---

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## ⚠️ Disclaimer
This system is for educational and safety purposes. Ensure proper testing before real-world deployment. Not a substitute for professional drowsiness monitoring systems.
