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
    fetch_user_stats
)
from log_handler import log_event
from email_alert import send_email_alert
from telegram_alert import send_telegram_alert
from admin_scheduler import run_scheduler
from admin_dashboard import render_admin_dashboard


# ---------------- CLOUD DETECTION ----------------
def is_streamlit_cloud():
    return os.environ.get("STREAMLIT_RUNTIME_ENV") == "cloud"


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
for k, v in default_values.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
}
@keyframes blinker {
    50% { opacity: 0.3; }
}
</style>
""", unsafe_allow_html=True)


# ---------------- AUDIO (CLOUD SAFE) ----------------
def play_browser_alarm(enabled=True):
    if not enabled:
        return
    try:
        with open("assets/alert.wav", "rb") as f:
            st.audio(f.read(), format="audio/wav")
    except Exception:
        pass


def trigger_alerts(status, enabled=True):
    play_browser_alarm(enabled)
    msg = f"🚨 Drowsiness detected at {datetime.now()} | Status: {status}"
    send_email_alert(msg)
    send_telegram_alert(msg)


# ---------------- AUTH ----------------
if not st.session_state["user_id"]:
    login, signup = st.tabs(["Login", "Sign Up"])

    with login:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(u, p)
            if user:
                st.session_state["user_id"], st.session_state["is_admin"] = user
                st.rerun()
            else:
                st.error("Invalid credentials")

    with signup:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            if add_user(nu, np):
                st.success("Account created")
            else:
                st.error("Username exists")


# ---------------- MAIN APP ----------------
else:
    menu = ["Detection"]
    if st.session_state["is_admin"]:
        menu.append("Admin Dashboard")

    page = st.sidebar.radio("Navigation", menu)

    if page == "Detection":
        stats = fetch_user_stats(st.session_state["user_id"])
        st.subheader(stats["username"])

        # 🔒 CLOUD GUARD (THIS IS THE KEY FIX)
        if is_streamlit_cloud():
            st.warning(
                "🚫 Webcam-based detection is disabled on Streamlit Cloud.\n\n"
                "✅ Run the app locally for full functionality."
            )
            st.stop()

        ear = st.sidebar.slider("EAR Threshold", 0.1, 0.4, 0.25)
        mar = st.sidebar.slider("MAR Threshold", 0.3, 0.7, 0.5)
        frames = st.sidebar.slider("Frame Check", 10, 40, 20)

        start = st.button("Start Detection")
        stop = st.button("Stop Detection")

        detector = DrowsinessDetector(
            "models/shape_predictor_68_face_landmarks.dat",
            ear_thresh=ear,
            mar_thresh=mar,
            frame_check=frames
        )

        frame_box = st.image([])
        alert_box = st.empty()

        last_log = 0
        alerted = False

        if start:
            cap = cv2.VideoCapture(0)
            while cap.isOpened():
                ok, frame = cap.read()
                if not ok:
                    break

                frame, status, ear_v, mar_v = detector.analyze_frame(frame)
                frame_box.image(frame, channels="BGR")

                now = time.time()
                if status == "Drowsy":
                    if now - last_log > 10:
                        log_event(ear_v, status, st.session_state["user_id"])
                        last_log = now

                    if not alerted:
                        alert_box.markdown(
                            "<div class='blink'>🚨 Drowsiness Detected</div>",
                            unsafe_allow_html=True
                        )
                        threading.Thread(
                            target=trigger_alerts,
                            args=(status, st.session_state["sound_enabled"]),
                            daemon=True
                        ).start()
                        alerted = True
                else:
                    alerted = False
                    alert_box.empty()

                if stop:
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
