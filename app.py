import streamlit as st
import random
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartHealth IoT Monitor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DYNAMIC THEME & GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
def apply_theme(sim_mode):
    if sim_mode == "Critical":
        accent_color = "#ff3344"
        base_bg = "#1a060a"
        glow_color = "red"
        live_badge_bg = "#2a0a10"
        live_badge_border = "#ff334488"
        live_dot_anim = "blink-crit 1s ease-in-out infinite"
    elif sim_mode == "Recovery":
        accent_color = "#00ff88"
        base_bg = "#061a0e"
        glow_color = "green"
        live_badge_bg = "#0a1e10"
        live_badge_border = "#00ff8860"
        live_dot_anim = "blink 1.1s ease-in-out infinite"
    else: # Normal
        accent_color = "#00d4ff"
        base_bg = "#060d1a"
        glow_color = "cyan"
        live_badge_bg = "#0a1e10" # Using green for normal as per original
        live_badge_border = "#00ff8860"
        live_dot_anim = "blink 1.1s ease-in-out infinite"

    st.markdown(
        f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

    :root {{
        --accent: {accent_color};
        --glow: {glow_color};
        --base-bg: {base_bg};
        --live-badge-bg: {live_badge_bg};
        --live-badge-border: {live_badge_border};
        --live-dot-anim: {live_dot_anim};
    }}

    /* ── Base ── */
    html, body, .stApp {{ background-color: var(--base-bg) !important; color: #c8d8e8; font-family: 'Rajdhani', sans-serif; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding: 0.8rem 1.8rem !important; max-width: 100%; }}
    div[data-testid="stVerticalBlock"] {{ gap: 0.8rem; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #080f1e 0%, #060d1a 100%) !important;
        border-right: 1px solid #122038;
    }}
    [data-testid="stSidebar"] * {{ color: #7aaacf !important; }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label {{ font-size: 0.75rem; letter-spacing: 1px; text-transform: uppercase; }}
    .switch-user-btn {{
        background: linear-gradient(135deg, #ffaa0022, #ffaa0011) !important;
        border: 1px solid #ffaa0066 !important;
        color: #ffaa00 !important;
    }}
    .switch-user-btn:hover {{ background: #ffaa0033 !important; box-shadow: 0 0 18px #ffaa0044; }}

    /* ── Inputs ── */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
        background: #0d1f35 !important;
        border: 1px solid #1a3a5c !important;
        color: #c8d8e8 !important;
        border-radius: 6px !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #00d4ff22, #00d4ff11) !important;
        border: 1px solid #00d4ff66 !important;
        color: #00d4ff !important;
        font-family: 'Share Tech Mono', monospace !important;
        letter-spacing: 2px !important;
        border-radius: 6px !important;
        transition: all 0.25s;
    }}
    .stButton > button:hover {{ background: #00d4ff33 !important; box-shadow: 0 0 18px #00d4ff44; }}
    .stDownloadButton > button {{
        background: linear-gradient(135deg, #00ff8822, #00ff8811) !important;
        border: 1px solid #00ff8866 !important;
        color: #00ff88 !important;
        font-family: 'Share Tech Mono', monospace !important;
        border-radius: 6px !important;
    }}

    /* ── Section header ── */
    .sec-head {{
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.82rem;
        color: #00d4ffcc;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin: 0.6rem 0 0.35rem;
        padding-left: 0.6rem;
        border-left: 2px solid #00d4ff66;
    }}

    /* ── Live badge ── */
    .live-wrap {{ display: flex; align-items: center; gap: 8px; }}
    .live-badge {{
        display: inline-flex; align-items: center; gap: 5px;
        background: var(--live-badge-bg); border: 1px solid var(--live-badge-border);
        border-radius: 20px; padding: 2px 10px;
        font-size: 0.68rem; color: var(--accent);
        font-family: 'Share Tech Mono', monospace;
    }}
    .live-dot {{
        width: 7px; height: 7px; background: var(--accent);
        border-radius: 50%; display: inline-block;
        animation: var(--live-dot-anim);
    }}
    @keyframes blink {{
        0%,100% {{ opacity: 1; box-shadow: 0 0 6px var(--glow); }}
        50%      {{ opacity: 0.2; box-shadow: none; }}
    }}
    @keyframes blink-crit {{
        0%,100% {{ opacity: 1; transform: scale(1.1); box-shadow: 0 0 8px var(--glow); }}
        50%      {{ opacity: 0.2; transform: scale(1); box-shadow: none; }}
    }}

    /* ── Vital card ── */
    .vcard {{
        background: linear-gradient(145deg, #0d1e32 0%, #091628 100%);
        border: 1px solid #152d4a;
        border-top: 2px solid var(--accent);
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
        text-align: center;
        min-height: 108px;
        display: flex; flex-direction: column; justify-content: center;
        box-shadow: 0 0 20px -5px var(--glow, transparent);
    }}
    .vcard .vlbl  {{ font-size: 0.85rem; color: #ffffff; letter-spacing: 2px; text-transform: uppercase; font-family: 'Share Tech Mono', monospace; }}
    .vcard .vval  {{ font-size: 2.6rem; font-weight: 700; color: var(--accent); font-family: 'Share Tech Mono', monospace;
                    text-shadow: 0 0 14px var(--accent); line-height: 1.15; }}
    .vcard .vunit {{ font-size: 0.62rem; color: #4a7a9e; margin-top: 2px; }}

    /* ── Status strip ── */
    .status-strip {{
        background: #091628; border: 1px solid #152d4a; border-radius: 8px;
        padding: 0.5rem 1rem; display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
        font-family: 'Share Tech Mono', monospace; font-size: 0.75rem;
    }}

    /* ── Alert boxes ── */
    .al-crit {{ background:#140508; border:1px solid #ff334466; border-left:3px solid #ff3344;
               border-radius:6px; padding:0.35rem 0.9rem; color:#ff6677;
               font-family:'Share Tech Mono',monospace; font-size:0.88rem; margin:3px 0; }}
    .al-warn {{ background:#14100a; border:1px solid #ffaa0066; border-left:3px solid #ffaa00;
               border-radius:6px; padding:0.35rem 0.9rem; color:#ffcc44;
               font-family:'Share Tech Mono',monospace; font-size:0.88rem; margin:3px 0; }}
    .al-ok   {{ background:#04120a; border:1px solid #00ff8860; border-left:3px solid #00ff88;
               border-radius:6px; padding:0.35rem 0.9rem; color:#00ff88;
               font-family:'Share Tech Mono',monospace; font-size:0.88rem; }}

    /* ── Info card (profile / AI) ── */
    .info-card {{
        background: #0d1e32; border: 1px solid #152d4a; border-radius: 10px; padding: 0.9rem 1rem;
        height:100%;
    }}
    .info-card .ic-title {{ color: #00d4ff; font-weight: 700; font-size: 1rem; margin-bottom: 0.4rem; }}
    .info-card .ic-row   {{ color: #7aaacf; font-size: 0.82rem; line-height: 1.8; }}

    /* ── Mini stat ── */
    .mini-stat {{
        background: #0d1e32; border: 1px solid #152d4a; border-radius: 8px;
        padding: 0.5rem; text-align: center;
    }}
    .mini-stat .ms-val {{ color: var(--accent); font-size: 1.6rem; font-weight: 700; font-family: 'Share Tech Mono', monospace; }}
    .mini-stat .ms-lbl {{ color: #a0c4e0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; }}
    .mini-stat .ms-unit {{ color:#4a7a9e; font-size: 0.75rem; }}

    /* ── AI card ── */
    .ai-card {{
        background: #0d1e32; border: 1px solid #152d4a; border-radius: 10px; padding: 0.75rem 1rem;
        border-top: 2px solid var(--accent);
    }}
    .ai-card .ai-lbl   {{ font-size: 0.78rem; color: #a0c4e0; letter-spacing: 2px; text-transform: uppercase; font-family: 'Share Tech Mono', monospace; }}
    .ai-card .ai-trend {{ font-size: 1.15rem; color: var(--accent); margin: 0.2rem 0; font-weight: 600; }}
    .ai-card .ai-anom  {{ font-size: 0.75rem; font-family: 'Share Tech Mono', monospace; }}

    /* ── Chart Card Wrapper ── */
    .chart-card {{
        background: #0d1e32;
        border: 1px solid #152d4a;
        border-radius: 10px;
        padding: 1.2rem;
    }}

    /* ── Enc badge ── */
    .enc-badge {{
        background: #041410; border: 1px solid #00ff8840; border-radius: 5px;
        padding: 0.25rem 0.7rem; font-family: 'Share Tech Mono', monospace;
        font-size: 0.68rem; color: #00ff88; display: inline-block; margin: 2px 0;
    }}

    /* ── Doc patient row ── */
    .doc-row {{
        background: #0d1e32; border: 1px solid #152d4a; border-radius: 8px;
        padding: 0.55rem 0.9rem; margin-bottom: 0.3rem;
        font-family: 'Share Tech Mono', monospace;
    }}
    .doc-row .dr-name {{ color: #00d4ff; font-weight: 700; font-size: 1rem; }}
    .doc-row .dr-vals {{ color: #a0c4e0; font-size: 0.85rem; }}

    /* ── Login ── */
    .login-bg {{
        min-height: 100vh; display: flex; align-items: center; justify-content: center;
    }}
    .login-panel {{
        background: #0d1e32; border: 1px solid #152d4a; border-radius: 16px;
        padding: 2.5rem 2rem; max-width: 420px; width: 100%; text-align: center;
    }}
    .login-logo {{
        font-family: 'Share Tech Mono', monospace; font-size: 2rem;
        color: #00d4ff; text-shadow: 0 0 25px #00d4ff88; letter-spacing: 3px;
    }}
    .login-sub {{ color: #4a7a9e; font-size: 0.72rem; letter-spacing: 4px; margin: 0.3rem 0 1.5rem; }}

    /* ── Divider ── */
    .divider-glow {{
        border-top: 1px solid var(--accent);
        opacity: 0.4;
        box-shadow: 0 0 10px var(--glow);
        margin: 0.8rem 0;
    }}

    /* ── Score ring (text) ── */
    .score-ring {{
        width: 80px; height: 80px; border-radius: 50%;
        border: 3px solid var(--sc, #00ff88); display: flex; flex-direction: column;
        align-items: center; justify-content: center; margin: auto;
        box-shadow: 0 0 18px var(--sc, #00ff8866);
    }}
    .score-ring .sr-val {{ font-family: 'Share Tech Mono', monospace; font-size: 1.3rem; font-weight: 700; color: var(--sc, #00ff88); line-height: 1; }}
    .score-ring .sr-lbl {{ font-size: 0.5rem; color: #4a7a9e; letter-spacing: 2px; }}
    </style>
    """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# CREDENTIALS & PROFILES
# ─────────────────────────────────────────────────────────────────────────────
CREDENTIALS = {
    "doctor":    {"password": "doc123",  "role": "Doctor",  "patient": None},
    "patient_a": {"password": "pat123",  "role": "Patient", "patient": "Patient A"},
    "patient_b": {"password": "pat456",  "role": "Patient", "patient": "Patient B"},
    "patient_c": {"password": "pat789",  "role": "Patient", "patient": "Patient C"},
}

PROFILES = {
    "Patient A": {"name": "Arjun Mehta",  "age": 45, "blood": "B+", "condition": "Hypertension",      "doctor": "Dr. Sharma",  "ward": "Cardiology 3B"},
    "Patient B": {"name": "Priya Nair",   "age": 32, "blood": "O+", "condition": "Type-2 Diabetes",   "doctor": "Dr. Sharma",  "ward": "Endocrine 2A"},
    "Patient C": {"name": "Ravi Kumar",   "age": 67, "blood": "A-", "condition": "Cardiac Monitoring", "doctor": "Dr. Patel",   "ward": "ICU 1C"},
}

BASE_VITALS = {
    "Patient A": {"hr": 82.0,  "o2": 96.0, "temp": 37.2, "sbp": 140.0, "dbp": 90.0,  "glc": 105.0, "rr": 17.0},
    "Patient B": {"hr": 76.0,  "o2": 97.0, "temp": 36.8, "sbp": 118.0, "dbp": 76.0,  "glc": 145.0, "rr": 16.0},
    "Patient C": {"hr": 95.0,  "o2": 92.0, "temp": 37.5, "sbp": 155.0, "dbp": 98.0,  "glc": 98.0,  "rr": 20.0},
}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "logged_in": False,
        "role": None,
        "username": None,
        "assigned_patient": None,
        "patients_data": {"Patient A": [], "Patient B": [], "Patient C": []},
        "global_alerts": [],
        "vitals_base": {k: dict(v) for k, v in BASE_VITALS.items()},
        "show_arch": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─────────────────────────────────────────────────────────────────────────────
# DATA GENERATION  – realistic Gaussian random walk
# ─────────────────────────────────────────────────────────────────────────────
def generate_data(patient, sim_mode="Normal"):
    b = st.session_state.vitals_base[patient]

    if sim_mode == "Critical":
        b["hr"]   = b["hr"]   * 0.85 + 118  * 0.15
        b["o2"]   = b["o2"]   * 0.85 +  88  * 0.15
        b["temp"] = b["temp"] * 0.85 +  39.4 * 0.15
        b["sbp"]  = b["sbp"]  * 0.85 + 170  * 0.15
        b["glc"]  = b["glc"]  * 0.85 + 210  * 0.15
    elif sim_mode == "Recovery":
        b["hr"]   = b["hr"]   * 0.85 +  72  * 0.15
        b["o2"]   = b["o2"]   * 0.85 +  98  * 0.15
        b["temp"] = b["temp"] * 0.85 +  36.9 * 0.15
        b["sbp"]  = b["sbp"]  * 0.85 + 120  * 0.15
        b["glc"]  = b["glc"]  * 0.85 +  95  * 0.15
    else:
        b["hr"]   = max(50,  min(140,  b["hr"]   + np.random.normal(0, 1.5)))
        b["o2"]   = max(85,  min(100,  b["o2"]   + np.random.normal(0, 0.4)))
        b["temp"] = max(35.5,min(40.0, b["temp"] + np.random.normal(0, 0.04)))
        b["sbp"]  = max(90,  min(185,  b["sbp"]  + np.random.normal(0, 1.5)))
        b["dbp"]  = max(60,  min(120,  b["dbp"]  + np.random.normal(0, 1.0)))
        b["glc"]  = max(60,  min(260,  b["glc"]  + np.random.normal(0, 1.8)))
        b["rr"]   = max(10,  min(30,   b["rr"]   + np.random.normal(0, 0.35)))

    return {
        "heart_rate":       round(b["hr"]),
        "oxygen":           round(b["o2"], 1),
        "temperature":      round(b["temp"], 1),
        "systolic_bp":      round(b["sbp"]),
        "diastolic_bp":     round(b["dbp"]),
        "glucose":          round(b["glc"]),
        "respiratory_rate": round(b["rr"], 1),
        "timestamp":        datetime.now().strftime("%H:%M:%S"),
    }

# ─────────────────────────────────────────────────────────────────────────────
# HEALTH SCORE
# ─────────────────────────────────────────────────────────────────────────────
def health_score(d):
    sc = 100
    alerts = []

    if   d["heart_rate"] > 100: sc -= 20; alerts.append(("crit", f"⚡ Tachycardia  {d['heart_rate']} bpm"))
    elif d["heart_rate"] < 60:  sc -= 15; alerts.append(("warn", f"⚡ Bradycardia  {d['heart_rate']} bpm"))

    if   d["oxygen"] < 90:  sc -= 30; alerts.append(("crit", f"💨 Hypoxia  SpO₂ {d['oxygen']}%"))
    elif d["oxygen"] < 95:  sc -= 12; alerts.append(("warn", f"💨 Low SpO₂  {d['oxygen']}%"))

    if   d["temperature"] > 38.5: sc -= 20; alerts.append(("crit", f"🌡 Fever  {d['temperature']}°C"))
    elif d["temperature"] > 37.5: sc -= 8;  alerts.append(("warn", f"🌡 Elevated Temp  {d['temperature']}°C"))

    if   d["systolic_bp"] > 160: sc -= 20; alerts.append(("crit", f"🩸 Hypertensive Crisis  {d['systolic_bp']}/{d['diastolic_bp']} mmHg"))
    elif d["systolic_bp"] > 140: sc -= 10; alerts.append(("warn", f"🩸 High BP  {d['systolic_bp']}/{d['diastolic_bp']} mmHg"))

    if   d["glucose"] < 70:  sc -= 20; alerts.append(("crit", f"🍬 Hypoglycaemia  {d['glucose']} mg/dL"))
    elif d["glucose"] > 180: sc -= 15; alerts.append(("warn", f"🍬 High Glucose  {d['glucose']} mg/dL"))

    if d["respiratory_rate"] > 25 or d["respiratory_rate"] < 12:
        sc -= 10; alerts.append(("warn", f"💨 Abnormal RR  {d['respiratory_rate']}/min"))

    sc = max(0, sc)

    if   sc > 80: colour = "#00ff88"; label = "STABLE ✅"
    elif sc > 60: colour = "#ffcc00"; label = "MODERATE RISK ⚠️"
    elif sc > 40: colour = "#ff6600"; label = "HIGH RISK 🟠"
    else:         colour = "#ff3344"; label = "CRITICAL 🔴"

    return sc, colour, label, alerts

# ─────────────────────────────────────────────────────────────────────────────
# AI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def ai_trend(df, col):
    if len(df) < 5:
        return "→ Collecting data…", False
    vals = df[col].values[-20:]
    X = np.arange(len(vals)).reshape(-1, 1)
    m = LinearRegression().fit(X, vals)
    coef = m.coef_[0]
    trend = "↗️ Rising" if coef > 0.4 else ("↘️ Falling" if coef < -0.4 else "→ Stable")

    # Anomaly (z‑score on last point)
    mu, sigma = vals[:-1].mean(), vals[:-1].std()
    anomaly = bool(sigma > 0 and abs((vals[-1] - mu) / sigma) > 2.5)
    return trend, anomaly

# ─────────────────────────────────────────────────────────────────────────────
# ECG WAVEFORM GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def ecg_wave(hr=75, pts=320):
    t = np.linspace(0, 4.5, pts)
    sig = np.zeros(pts)
    period = 60 / hr
    for i, ti in enumerate(t):
        ph = (ti % period) / period
        if 0.08 < ph < 0.18:
            sig[i] = 0.22 * np.sin(np.pi * (ph - 0.08) / 0.1)
        elif 0.27 < ph < 0.33:
            p = (ph - 0.27) / 0.06
            if   p < 0.25: sig[i] = -0.25 * p / 0.25
            elif p < 0.45: sig[i] = -0.25 + 1.8  * (p - 0.25) / 0.2
            elif p < 0.65: sig[i] =  1.55 - 1.8  * (p - 0.45) / 0.2
            else:          sig[i] = -0.25 + 0.25 * (p - 0.65) / 0.35
        elif 0.42 < ph < 0.6:
            sig[i] = 0.32 * np.sin(np.pi * (ph - 0.42) / 0.18)
        sig[i] += np.random.normal(0, 0.018)
    return t, sig

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART LAYOUT TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────
def chart_layout(title="", h=260):
    return dict(
        title=dict(text=title, font=dict(color="#a0c4e0", size=14, family="Share Tech Mono"), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", # Transparent plot bg
        font=dict(color="#a0c4e0", family="Rajdhani"),
        margin=dict(l=36, r=12, t=40, b=28),
        xaxis=dict(gridcolor="#0d2240", zerolinecolor="#0d2240", color="#3a6080", showticklabels=True),
        yaxis=dict(gridcolor="#0d2240", zerolinecolor="#0d2240", color="#3a6080"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a0c4e0", size=10),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=h,
        hovermode="x unified",
    )

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_login():
    apply_theme("Normal") # Always use normal theme for login
    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align:center; margin-bottom: 1.5rem;">
                <div style="font-family:'Share Tech Mono',monospace; font-size:2.1rem; color:#00d4ff;
                            text-shadow: 0 0 28px #00d4ff88; letter-spacing:3px;">
                    🏥 SMARTHEALTH
                </div>
                <div style="color:#4a7a9e; font-size:0.7rem; letter-spacing:5px; margin-top:4px;">
                    CLOUD · IoT · MONITORING
                </div>
            </div>
            <div style="background:#0d1e32; border:1px solid #152d4a; border-radius:14px; padding:2rem 1.8rem;">
                <div style="font-family:'Share Tech Mono',monospace; color:#00d4ff; font-size:0.8rem;
                            letter-spacing:2px; margin-bottom:1rem;">🔐 SECURE PORTAL</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uname = st.text_input("Username", placeholder="e.g., doctor, patient_a")
        pwd   = st.text_input("Password", type="password", placeholder="e.g., doc123, pat123")

        if st.button("LOGIN  →", use_container_width=True):
            cred = CREDENTIALS.get(uname)
            if cred and cred["password"] == pwd:
                st.session_state.logged_in       = True
                st.session_state.role            = cred["role"]
                st.session_state.username        = uname
                st.session_state.assigned_patient = cred["patient"]
                st.rerun()
            else:
                st.error("Invalid username or password")


# ─────────────────────────────────────────────────────────────────────────────
# ARCHITECTURE DIAGRAM
# ─────────────────────────────────────────────────────────────────────────────
def show_architecture():
    total_pts = sum(len(v) for v in st.session_state.patients_data.values())
    latency   = random.randint(11, 38)
    st.markdown(
        f"""
    <div style="background: #0d1e32; border: 1px solid #152d4a; border-radius: 10px; padding: 0.9rem 1rem; font-family: 'Share Tech Mono', monospace;">
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 4px;">
            <div style="text-align: center;">
                <div style="font-size: 1.6rem;">🩺</div>
                <div style="font-size: 0.7rem; letter-spacing: 1px; color:#00d4ff;">IoT SENSORS</div>
                <div style="color: #3a6080; font-size: 0.6rem; margin-top: 2px;">HR · SpO₂ · Temp<br>BP · Glucose · ECG</div>
            </div>
            <div style="color: #1a3a5c; font-size: 1.2rem; align-self: center;">━━▶️</div>
            <div style="text-align: center;">
                <div style="font-size: 1.6rem;">🔌</div>
                <div style="font-size: 0.7rem; letter-spacing: 1px; color:#f472b6;">EDGE NODE</div>
                <div style="color: #3a6080; font-size: 0.6rem; margin-top: 2px;">Local processing<br>Pre-filtering alerts</div>
            </div>
            <div style="color: #1a3a5c; font-size: 1.2rem; align-self: center;">━━▶️</div>
            <div style="text-align: center;">
                <div style="font-size: 1.6rem;">🔒</div>
                <div style="font-size: 0.7rem; letter-spacing: 1px; color:#ffaa00;">ENCRYPTION</div>
                <div style="color: #3a6080; font-size: 0.6rem; margin-top: 2px;">AES-256<br>TLS 1.3 in transit</div>
            </div>
            <div style="color: #1a3a5c; font-size: 1.2rem; align-self: center;">━━▶️</div>
            <div style="text-align: center;">
                <div style="font-size: 1.6rem;">☁️</div>
                <div style="font-size: 0.7rem; letter-spacing: 1px; color:#00ff88;">CLOUD SERVER</div>
                <div style="color: #3a6080; font-size: 0.6rem; margin-top: 2px;">AWS / Azure IoT Hub<br>Scalable storage</div>
            </div>
            <div style="color: #1a3a5c; font-size: 1.2rem; align-self: center;">━━▶️</div>
            <div style="text-align: center;">
                <div style="font-size: 1.6rem;">🤖</div>
                <div style="font-size: 0.7rem; letter-spacing: 1px; color:#c084fc;">AI ENGINE</div>
                <div style="color: #3a6080; font-size: 0.6rem; margin-top: 2px;">Linear Regression<br>Anomaly Detection</div>
            </div>
            <div style="color: #1a3a5c; font-size: 1.2rem; align-self: center;">━━▶️</div>
            <div style="text-align: center;">
                <div style="font-size: 1.6rem;">🖥️</div>
                <div style="font-size: 0.7rem; letter-spacing: 1px; color:#34d399;">DASHBOARD</div>
                <div style="color: #3a6080; font-size: 0.6rem; margin-top: 2px;">Real-time UI<br>Role-based access</div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 0.6rem; color: #2a5070; font-size: 0.65rem;">
            📡 Latency: {latency}ms &nbsp;|&nbsp; 🔄 Uptime: 99.98% &nbsp;|&nbsp;
            📦 Total Data Points: {total_pts} &nbsp;|&nbsp; 👥 Patients: 3 Active
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard():
    role = st.session_state.role

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            """<div style="font-family:'Share Tech Mono',monospace; color:#00d4ff; font-size:1rem;
                           text-align:center; padding:0.4rem 0; text-shadow:0 0 12px #00d4ff66;">
               ⚕ SmartHealth IoT</div>""",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)

        # Simplified sidebar as per user request
        st.session_state.sim_mode = st.selectbox("🚨 SIMULATION MODE", ["Normal", "Critical", "Recovery"])
        
        st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)
        
        arch_btn_text = "✕ HIDE ARCHITECTURE" if st.session_state.show_arch else "☁️ VIEW ARCHITECTURE"
        if st.button(arch_btn_text, use_container_width=True):
            st.session_state.show_arch = not st.session_state.show_arch
            st.rerun()

        if st.button("🔄 SWITCH USER", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.rerun()

    # Must be called after sidebar controls to get current sim_mode
    apply_theme(st.session_state.sim_mode)

    # Determine which patient to show
    if role == "Doctor":
        patient_list = ["Patient A", "Patient B", "Patient C"]
        patient = st.sidebar.selectbox("Select Patient", patient_list)
    else:
        patient = st.session_state.assigned_patient

    # ── GENERATE DATA ─────────────────────────────────────────────────────────
    data = generate_data(patient, st.session_state.sim_mode)
    st.session_state.patients_data[patient].append(data)
    
    # Keep only the last 100 records to prevent memory leak and lag
    if len(st.session_state.patients_data[patient]) > 100:
        st.session_state.patients_data[patient] = st.session_state.patients_data[patient][-100:]
        
    df   = pd.DataFrame(st.session_state.patients_data[patient])
    sc, sc_col, sc_label, cur_alerts = health_score(data)

    # Persist alerts
    for _, amsg in cur_alerts:
        entry = f"[{data['timestamp']}] {patient}: {amsg}"
        if len(st.session_state.global_alerts) == 0 or st.session_state.global_alerts[-1] != entry:
            st.session_state.global_alerts.append(entry)
            
    # Cap global alerts history as well
    if len(st.session_state.global_alerts) > 50:
        st.session_state.global_alerts = st.session_state.global_alerts[-50:]

    # ── HEADER ROW ───────────────────────────────────────────────────────────
    hcol1, hcol2, hcol3 = st.columns([3, 1, 1.3])
    with hcol1:
        st.markdown(
            """<div style="font-family:'Share Tech Mono',monospace; font-size:1.45rem; color:#00d4ff;
                           text-shadow:0 0 18px #00d4ff66; letter-spacing:2px; border-bottom:1px solid #122038;
                           padding-bottom:0.25rem;">
               🏥 SMARTHEALTH  CLOUD‑IoT  MONITOR</div>""",
            unsafe_allow_html=True,
        )
    with hcol2:
        st.markdown(
            f"""<div class="live-wrap" style="margin-top:0.35rem;">
                    <span class="live-badge"><span class="live-dot"></span>&nbsp;LIVE</span>
                    <span style="color:#3a6080; font-family:'Share Tech Mono',monospace; font-size:0.68rem;">
                        {data['timestamp']}
                    </span>
                </div>""",
            unsafe_allow_html=True,
        )
    with hcol3:
        st.markdown(
            f"""<div style="text-align:right; margin-top:0.3rem;">
                    <div style="color:{sc_col}; font-family:'Share Tech Mono',monospace; font-size:0.85rem;
                                text-shadow:0 0 10px {sc_col}88;">{sc_label}</div>
                    <div style="color:#3a6080; font-size:0.7rem;">Health Score:
                        <span style="color:{sc_col}; font-weight:700;">{sc} / 100</span>
                    </div>
                </div>""",
            unsafe_allow_html=True,
        )
    
    # --- PATIENT PROFILE AT TOP ---
    st.markdown("<div class='sec-head'>👤 PATIENT PROFILE</div>", unsafe_allow_html=True)
    prof = PROFILES[patient]
    st.markdown(
        f"""<div class="info-card">
                <div class="ic-title">{prof['name']}</div>
                <div class="ic-row">
                    🎂 &nbsp;Age: <b>{prof['age']}</b> yrs &nbsp;|&nbsp; 🩸 Blood: <b>{prof['blood']}</b><br>
                    🏥 Condition: <b>{prof['condition']}</b><br>
                    👨‍⚕️ Doctor: <b>{prof['doctor']}</b><br>
                    🛏 Ward: <b>{prof['ward']}</b>
                </div>
            </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)


    # ── VITAL CARDS (MERGED WITH AI) ──────────────────────────────────────
    st.markdown("<div class='sec-head'>📡 REAL-TIME IoT SENSOR FEED</div>", unsafe_allow_html=True)

    cards_data = [
        ("heart_rate",       "❤️ HEART RATE",     data["heart_rate"],                          "bpm",    "#ff4d6d"),
        ("oxygen",           "🫁 SpO₂ OXYGEN",    data["oxygen"],                              "%",      "#00d4ff"),
        ("temperature",      "🌡 TEMPERATURE",     data["temperature"],                         "°C",     "#ff9a3c"),
        ("systolic_bp",      "🩸 BLOOD PRESSURE",  f"{data['systolic_bp']}/{data['diastolic_bp']}", "mmHg", "#c084fc"),
    ]

    cols = st.columns(4)
    for col, (fld, lbl, val, unit, ac) in zip(cols, cards_data):
        with col:
            trend, anomaly = ai_trend(df, fld) if len(df) >= 5 else ("→ Collecting…", False)
            anom_col = "#ff3344" if anomaly else "#00ff88"
            anom_txt = "⚠ ANOMALY" if anomaly else "✅ Normal"
            st.markdown(
                f"""<div class="vcard" style="--ac:{ac};">
                        <div class="vlbl">{lbl}</div>
                        <div class="vval">{val}</div>
                        <div class="vunit">{unit}</div>
                        <div class="ai-card" style="margin-top: 8px; border-top: 1px solid #152d4a; padding-top: 8px;">
                            <div class="ai-trend" style="font-size: 0.9rem;">{trend}</div>
                            <div class="ai-anom" style="color:{anom_col}; font-size: 0.7rem;">{anom_txt}</div>
                        </div>
                    </div>""",
                unsafe_allow_html=True,
            )

    # ── ECG + ALERTS ─────────────────────────────────────────────────────────
    ecg_col, al_col = st.columns([2.2, 1])

    with ecg_col:
        st.markdown("<div class='sec-head'>📈 ECG WAVEFORM — LIVE</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        t, sig = ecg_wave(hr=data["heart_rate"])
        fig_ecg = go.Figure()
        fig_ecg.add_trace(go.Scatter(
            x=t, y=sig, mode="lines",
            line=dict(color="#00ff88", width=1.5),
            fill="tozeroy", fillcolor="rgba(0,255,136,0.04)",
            name="ECG",
        ))
        layout = chart_layout("ELECTROCARDIOGRAM", h=260)
        layout["xaxis"]["showticklabels"] = False
        layout["showlegend"] = False
        fig_ecg.update_layout(**layout)
        st.plotly_chart(fig_ecg, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with al_col:
        st.markdown("<div class='sec-head'>🚨 ACTIVE ALERTS</div>", unsafe_allow_html=True)
        if cur_alerts:
            for atype, amsg in cur_alerts:
                css = "al-crit" if atype == "crit" else "al-warn"
                st.markdown(f"<div class='{css}'>{amsg}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='al-ok'>✅ All vitals within normal range</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)

    # ── TREND CHARTS (2x2 GRID) ──────────────────────────────────────────
    if len(df) > 1:
        st.markdown("<div class='sec-head'>📊 VITAL TREND GRAPHS</div>", unsafe_allow_html=True)

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(y=df["heart_rate"], name="Heart Rate", line=dict(color="#ff4d6d", width=2)))
            fig1.add_trace(go.Scatter(y=df["oxygen"], name="SpO₂", line=dict(color="#00d4ff", width=2)))
            fig1.update_layout(**chart_layout("CARDIO & PULMONARY", h=300))
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with row1_col2:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            h_scores = [health_score(row.to_dict())[0] for _, row in df.iterrows()]
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(y=h_scores, name="Health Score", line=dict(color="#00ff88", width=2), fill="tozeroy", fillcolor="rgba(0,255,136,0.05)"))
            fig2.add_trace(go.Scatter(y=df["systolic_bp"], name="Systolic BP", line=dict(color="#c084fc", width=1.8)))
            fig2.update_layout(**chart_layout("SCORE & BP", h=300))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(y=df["glucose"], name="Glucose", line=dict(color="#34d399", width=2), fill="tozeroy", fillcolor="rgba(52,211,153,0.05)"))
            fig3.update_layout(**chart_layout("BLOOD GLUCOSE", h=300))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with row2_col2:
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(y=df["temperature"], name="Temp (°C)", line=dict(color="#ff9a3c", width=2), fill="tozeroy", fillcolor="rgba(255,154,60,0.05)"))
            fig4.update_layout(**chart_layout("BODY TEMPERATURE", h=300))
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)

    # ── DOCTOR VIEW / ALERT HISTORY ────────────────────────────────────────
    d_col, a_col = st.columns([1.5, 1])
    with d_col:
        if role == "Doctor":
            st.markdown("<div class='sec-head'>👨‍⚕️ DOCTOR DASHBOARD — ALL PATIENTS</div>", unsafe_allow_html=True)
            for p, pdata in st.session_state.patients_data.items():
                if pdata:
                    lat = pdata[-1]
                    ps, pc, _, _ = health_score(lat)
                    st.markdown(
                        f"""<div class="doc-row">
                                <span class="dr-name">{PROFILES[p]['name']}</span>
                                <span style="color:#3a6080; font-size:0.68rem; margin-left:6px;">({p})</span>
                                <span class="dr-vals" style="float:right;">
                                    HR {lat['heart_rate']} | SpO₂ {lat['oxygen']}% | Score <span style="color:{pc}; font-weight:700;">{ps}</span>
                                </span>
                            </div>""",
                        unsafe_allow_html=True,
                    )
    with a_col:
        if st.session_state.global_alerts:
            st.markdown("<div class='sec-head'>📜 ALERT HISTORY (last 4)</div>", unsafe_allow_html=True)
            for a in st.session_state.global_alerts[-4:][::-1]:
                st.markdown(f"<div class='al-warn'>{a}</div>", unsafe_allow_html=True)


    # ── CLOUD ARCHITECTURE (TOGGLE) ──────────────────────────────────────────
    if st.session_state.show_arch:
        st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-head'>☁️ CLOUD-IoT SYSTEM ARCHITECTURE</div>", unsafe_allow_html=True)
        show_architecture()


    # ── AUTO REFRESH ──────────────────────────────────────────────────────────
    time.sleep(2) # Fixed refresh time
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
main_container = st.empty()
if not st.session_state.logged_in:
    with main_container.container():
        show_login()
else:
    with main_container.container():
        show_dashboard()
