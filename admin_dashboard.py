import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from db import DB_NAME, add_user, delete_user, fetch_users, set_setting, get_setting

# ------------------ DB Utility ------------------
def fetch_logs():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM logs", conn)
    conn.close()
    return df

# ------------------ Admin Dashboard ------------------
def render_admin_dashboard(dark_mode=False):
    st.header("👑 Admin Dashboard")

    tabs = st.tabs(["📂 User Management", "📊 Analytics", "📅 Report Config"])

    # ------------------ User Management ------------------
    with tabs[0]:
        st.subheader("User Management")

        # Create user
        st.markdown("**Create New User**")
        new_username = st.text_input("Username", key="new_user_name")
        new_password = st.text_input("Password", type="password", key="new_user_pass")
        new_role = st.selectbox("Role", ["User", "Admin"], key="new_user_role")
        if st.button("Add User"):
            role_val = True if new_role == "Admin" else False
            if add_user(new_username, new_password, is_admin=role_val):
                st.success(f"User '{new_username}' created as {new_role}.")
            else:
                st.error("Username already exists.")

        st.markdown("---")

        # User list + delete
        st.subheader("Existing Users")
        users = fetch_users()
        if users:
            df_users = pd.DataFrame(users, columns=["ID", "Username", "Role"])
            st.dataframe(df_users)

            del_user_id = st.number_input("User ID to delete", min_value=1, step=1)
            if st.button("Delete User"):
                delete_user(del_user_id)
                st.success(f"User ID {del_user_id} deleted.")
        else:
            st.info("No users found.")

    # ------------------ Analytics ------------------
    with tabs[1]:
        st.subheader("Detection Analytics")
        df = fetch_logs()

        if df.empty:
            st.info("No logs available yet.")
        else:
            # Filter Drowsy only
            df_drowsy = df[df["status"] == "Drowsy"]

            if df_drowsy.empty:
                st.info("No Drowsy events logged.")
            else:
                # Date filter
                min_date = pd.to_datetime(df_drowsy["timestamp"]).min().date()
                max_date = pd.to_datetime(df_drowsy["timestamp"]).max().date()
                date_range = st.date_input("Select Date Range:", [min_date, max_date])

                start_date, end_date = date_range if len(date_range) == 2 else (min_date, max_date)
                mask = (pd.to_datetime(df_drowsy["timestamp"]).dt.date >= start_date) & \
                       (pd.to_datetime(df_drowsy["timestamp"]).dt.date <= end_date)
                filtered_df = df_drowsy[mask]

                # Drowsy events per user
                user_counts = filtered_df.groupby("user_id")["status"].count().reset_index()
                user_counts.columns = ["User ID", "Drowsy Events"]
                bar_chart = px.bar(
                    user_counts, x="User ID", y="Drowsy Events",
                    title="Drowsy Events per User",
                    template="plotly_dark" if dark_mode else "plotly_white"
                )
                st.plotly_chart(bar_chart, use_container_width=True)

                # Over time
                filtered_df["date"] = pd.to_datetime(filtered_df["timestamp"]).dt.date
                daily = filtered_df.groupby("date")["status"].count().reset_index()
                daily.columns = ["Date", "Drowsy Count"]
                line_chart = px.line(
                    daily, x="Date", y="Drowsy Count",
                    title="Drowsy Events Over Time", markers=True,
                    template="plotly_dark" if dark_mode else "plotly_white"
                )
                st.plotly_chart(line_chart, use_container_width=True)

                # System health stats
                st.subheader("System Health")
                total_users = len(fetch_users())
                total_events = len(df)
                total_drowsy = len(df_drowsy)
                st.markdown(f"""
                - 👥 **Total Users:** {total_users}  
                - 📦 **Total Logs:** {total_events}  
                - 🚨 **Drowsy Events:** {total_drowsy}
                """)

                # Show filtered logs
                st.subheader("Log Records")
                st.dataframe(filtered_df)

                # Export to CSV
                csv = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Logs as CSV",
                    data=csv,
                    file_name="drowsy_logs.csv",
                    mime="text/csv"
                )

    # ------------------ Report Config ------------------
    with tabs[2]:
        st.subheader("Daily Report Configuration")

        # Load existing config
        report_time = get_setting("report_time") or "09:00"
        report_email = get_setting("report_email") or ""
        report_telegram = get_setting("report_telegram") or ""

        time_input = st.time_input("Daily Summary Time", pd.to_datetime(report_time).time())
        email_input = st.text_input("Report Email Recipient", value=report_email)
        telegram_input = st.text_input("Report Telegram ID", value=report_telegram)

        if st.button("Save Report Settings"):
            set_setting("report_time", time_input.strftime("%H:%M"))
            set_setting("report_email", email_input)
            set_setting("report_telegram", telegram_input)
            st.success("Report settings saved successfully.")
