import streamlit as st
import random
import pandas as pd
import time

st.set_page_config(page_title="Smart Healthcare System", layout="wide")

st.title("🏥 Cloud–IoT Smart Healthcare Monitoring & Analysis System")

# -------------------------
# Sidebar Controls
# -------------------------
st.sidebar.header("Controls")

patient = st.sidebar.selectbox("Select Patient", ["Patient A", "Patient B", "Patient C"])
role = st.sidebar.selectbox("Login as", ["Doctor", "Patient"])

st.divider()

# -------------------------
# Initialize storage (cloud simulation)
# -------------------------
if "patients_data" not in st.session_state:
    st.session_state.patients_data = {
        "Patient A": [],
        "Patient B": [],
        "Patient C": []
    }

if "alerts" not in st.session_state:
    st.session_state.alerts = []

# -------------------------
# Simulated IoT Data
# -------------------------
def generate_data():
    return {
        "heart_rate": random.randint(60, 120),
        "oxygen": random.randint(88, 100),
        "temperature": round(random.uniform(36.0, 39.5), 1)
    }

data = generate_data()

# Store data
st.session_state.patients_data[patient].append(data)

df = pd.DataFrame(st.session_state.patients_data[patient])

# -------------------------
# Health Score Calculation
# -------------------------
score = 100

if data["heart_rate"] > 100:
    score -= 20
    st.session_state.alerts.append(f"{patient}: High Heart Rate")

if data["oxygen"] < 92:
    score -= 30
    st.session_state.alerts.append(f"{patient}: Low Oxygen")

if data["temperature"] > 38:
    score -= 20
    st.session_state.alerts.append(f"{patient}: High Temperature")

# Status Classification
if score > 80:
    status = "Healthy ✅"
elif score > 50:
    status = "Moderate Risk ⚠️"
else:
    status = "Critical 🚨"

# -------------------------
# Dashboard
# -------------------------
st.subheader(f"📊 Live Monitoring - {patient}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("❤️ Heart Rate", data["heart_rate"])
col2.metric("🫁 Oxygen Level", data["oxygen"])
col3.metric("🌡️ Temperature", data["temperature"])
col4.metric("💯 Health Score", score)

st.subheader("🧠 Patient Status")
st.info(status)

# -------------------------
# Alerts
# -------------------------
st.subheader("🚨 Current Alerts")

if data["heart_rate"] > 100:
    st.error("High Heart Rate!")

if data["oxygen"] < 92:
    st.error("Low Oxygen Level!")

if data["temperature"] > 38:
    st.error("High Temperature!")

if score > 80:
    st.success("All vitals normal")

# -------------------------
# Graphs
# -------------------------
st.subheader("📈 Patient Trends")

st.line_chart(df["heart_rate"])
st.line_chart(df["oxygen"])
st.line_chart(df["temperature"])

# -------------------------
# Analytics
# -------------------------
st.subheader("📊 Data Analysis")

st.write("Average Heart Rate:", round(df["heart_rate"].mean(), 2))
st.write("Max Temperature:", df["temperature"].max())
st.write("Min Oxygen Level:", df["oxygen"].min())

# -------------------------
# Alert History
# -------------------------
st.subheader("📜 Alert History")

for alert in st.session_state.alerts[-5:]:
    st.warning(alert)

# -------------------------
# Doctor View (All Patients)
# -------------------------
if role == "Doctor":
    st.subheader("👨‍⚕️ Doctor Dashboard (All Patients)")

    for p, pdata in st.session_state.patients_data.items():
        if pdata:
            latest = pdata[-1]
            st.write(f"{p} → HR: {latest['heart_rate']}, O2: {latest['oxygen']}, Temp: {latest['temperature']}")

# -------------------------
# Download Report
# -------------------------
st.subheader("📄 Generate Report")

st.download_button(
    label="Download Patient Report",
    data=df.to_csv(index=False),
    file_name=f"{patient}_report.csv",
    mime="text/csv"
)

# -------------------------
# Cloud Simulation Info
# -------------------------
st.success("☁️ Data stored & synced with cloud (simulated)")
st.info("🔄 Real-time monitoring enabled")

# -------------------------
# Auto Refresh
# -------------------------
time.sleep(2)
st.rerun()