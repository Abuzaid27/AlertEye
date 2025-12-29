# main.py
import streamlit as st
import cv2
import os
import time
from datetime import datetime
import threading

from drowsiness import DrowsinessDetector
from db import (
    init_db, add_user, authenticate_user, ensure_default_admin,
    fetch_users, delete_user, DB_NAME, fetch_user_stats,
    get_setting, set_setting
)
from log_handler import log_event
from email_alert import send_email_alert
from telegram_alert import send_telegram_alert
from admin_scheduler import run_scheduler
from admin_dashboard import render_admin_dashboard

# ---------------- INIT ----------------
init_db()
ensure_default_admin()

default_values = {
    "user_id": None,
    "is_admin": False,
    "dark_mode": False,
    "sound_enabled": True,
    "scheduler_started": False
}
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.set_page_config(page_title="Drowsiness Alert System", layout="wide")

# ---------------- STYLES ----------------
st.markdown("""
<style>
.blink {
    animation: blinker 1s linear infinite;
    background-color: #ff4b4b;
    color: white;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    font-size: 18px;
}
@keyframes blinker {
    50% { opacity: 0.3; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.session_state["dark_mode"] = st.sidebar.checkbox(
    "🌙 Dark Mode", st.session_state["dark_mode"]
)
st.session_state["sound_enabled"] = st.sidebar.checkbox(
    "🔊 Sound Alerts", st.session_state["sound_enabled"]
)

# ---------------- AUDIO (BROWSER SAFE) ----------------
def play_browser_alarm(sound_enabled=True):
    if sound_enabled:
        try:
            with open("assets/alert.wav", "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/wav")
        except Exception:
            pass  # never break detection

# ---------------- ALERTS ----------------
def trigger_alerts(status, sound_enabled=True):
    play_browser_alarm(sound_enabled)

    message = (
        f"🚨 Drowsiness detected at "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Status: {status}"
    )

    send_email_alert(message)
    send_telegram_alert(message)

# ---------------- AUTH ----------------
if not st.session_state["user_id"]:
    login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])

    with login_tab:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.session_state["user_id"], st.session_state["is_admin"] = user
                st.success(f"Welcome {username}!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with signup_tab:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if add_user(new_user, new_pass):
                st.success("Account created. Please log in.")
            else:
                st.error("Username already exists.")

# ---------------- MAIN APP ----------------
else:
    menu = ["Detection"]
    if st.session_state["is_admin"]:
        menu.append("Admin Dashboard")

    page = st.sidebar.radio("📌 Navigation", menu)

    if page == "Detection":
        stats = fetch_user_stats(st.session_state["user_id"])
        st.subheader(f"👤 {stats['username']}")
        st.markdown(f"""
- 🕒 Last Login: {stats['last_login']}
- 📊 Total Sessions: {stats['total_logs']}
- ⚠️ Drowsy Events: **{stats['drowsy_logs']}**
        """)

        # Thresholds
        ear_thresh = st.sidebar.slider("EAR Threshold", 0.1, 0.4, 0.25, 0.01)
        mar_thresh = st.sidebar.slider("MAR Threshold", 0.3, 0.7, 0.5, 0.01)
        frame_check = st.sidebar.slider("Frame Check", 10, 40, 20, 1)

        start_btn = st.button("Start Detection")
        stop_btn = st.button("Stop Detection")

        detector = DrowsinessDetector(
            "models/shape_predictor_68_face_landmarks.dat",
            ear_thresh=ear_thresh,
            mar_thresh=mar_thresh,
            frame_check=frame_check
        )

        FRAME_WINDOW = st.image([])
        status_placeholder = st.empty()
        alert_placeholder = st.empty()

        last_log_time = 0
        alert_triggered = False

        if start_btn:
            cap = cv2.VideoCapture(0)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    st.error("Webcam error.")
                    break

                frame = cv2.flip(frame, 1)
                frame, status, ear, mar = detector.analyze_frame(frame)

                FRAME_WINDOW.image(frame, channels="BGR")
                status_placeholder.write(
                    f"EAR: {ear:.2f} | MAR: {mar:.2f} | Status: {status}"
                )

                now = time.time()

                if status == "Drowsy":
                    if now - last_log_time > 10:
                        log_event(ear, status, st.session_state["user_id"])
                        last_log_time = now

                    if not alert_triggered:
                        alert_placeholder.markdown(
                            "<div class='blink'>🚨 Drowsiness Detected!</div>",
                            unsafe_allow_html=True
                        )

                        sound_enabled_value = st.session_state.get("sound_enabled", True)

                        threading.Thread(
                            target=trigger_alerts,
                            args=(status, sound_enabled_value),
                            daemon=True
                        ).start()

                        alert_triggered = True
                else:
                    alert_triggered = False
                    alert_placeholder.empty()

                if stop_btn:
                    break

            cap.release()

    elif page == "Admin Dashboard":
        render_admin_dashboard(st.session_state["dark_mode"])

    if st.sidebar.button("Logout"):
        st.session_state["user_id"] = None
        st.rerun()

# ---------------- SCHEDULER ----------------
if not st.session_state["scheduler_started"]:
    st.session_state["scheduler_started"] = True
    threading.Thread(target=run_scheduler, daemon=True).start()
