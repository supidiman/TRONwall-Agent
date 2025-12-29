import streamlit as st
import psutil
import json
import os
import time
import pandas as pd

# --- PAGE CONFIGURATION AND CUSTOM THEME ---
st.set_page_config(page_title="TRONwall Elite Command", layout="wide")

# Galactic Dark Theme (CSS Injection)
st.markdown("""
    <style>
    /* Main Background: Deep Space Black and Purple Gradient */
    .stApp {
        background: radial-gradient(circle at top right, #1a0b2e, #050505);
        color: #ffffff !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 5, 25, 0.95) !important;
        border-right: 1px solid #4b0082;
    }
    
    /* Metric Card Customization */
    div[data-testid="stMetric"] {
        background: rgba(40, 10, 60, 0.4);
        border: 1px solid #7d2ae8;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 0 15px rgba(125, 42, 232, 0.2);
    }

    /* --- INTEGRATED COLOR SETTINGS --- */
    
    /* SET METRIC VALUE COLOR TO WHITE */
    div[data-testid="stMetricValue"] > div {
        color: #ffffff !important;
    }

    /* SET METRIC LABEL COLOR TO PURPLE */
    div[data-testid="stMetricLabel"] > div {
        color: #bb86fc !important;
    }
    
    /* ----------------------------------------- */
    
    /* General Text Colors */
    h1, h2, h3, p, span, label {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Button Design */
    .stButton>button {
        background-color: #4b0082 !important;
        color: white !important;
        border: 1px solid #7d2ae8 !important;
        border-radius: 10px;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #7d2ae8 !important;
        box-shadow: 0 0 20px #7d2ae8;
    }
    
    /* Progress Bar (Neon Purple) */
    .stProgress > div > div > div > div {
        background-color: #9d50bb !important;
    }
    
    /* Log Area */
    .log-entry {
        background: rgba(20, 0, 30, 0.6);
        border-left: 4px solid #7d2ae8;
        padding: 10px;
        margin-bottom: 5px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA RESET FUNCTION ---
def reset_data():
    try:
        if os.path.exists('traffic.log'):
            with open('traffic.log', 'w') as f: pass
        if os.path.exists('blocked_ips.json'):
            with open('blocked_ips.json', 'w') as f: json.dump([], f)
        st.sidebar.success("System Cleared!")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Reset Error: {e}")

# --- DATA READING FUNCTIONS ---
def get_blocked_ips():
    paths = ['blocked_ips.json', 'ai_agent/blocked_ips.json']
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except: continue
    return []

def get_logs():
    if os.path.exists('traffic.log'):
        try:
            with open('traffic.log', 'r', encoding='utf-8') as f:
                return f.readlines()
        except:
            return ["Data Read Error"]
    return ["Waiting for Signal..."]

# --- HEADER ---
st.title("🛡️ TRONwall: Autonomous Security Command Center")
st.markdown("<p style='color: #bb86fc !important;'>Galactic Defense Line | Active Monitoring</p>", unsafe_allow_html=True)

# --- SIDEBAR: SYSTEM HEALTH ---
st.sidebar.markdown("### 🖥️ System Health")
cpu_usage = psutil.cpu_percent(interval=1)
ram_usage = psutil.virtual_memory().percent 

st.sidebar.metric("CPU Load", f"%{cpu_usage}")
st.sidebar.progress(cpu_usage / 100)

st.sidebar.metric("RAM Status", f"%{ram_usage}")
st.sidebar.progress(ram_usage / 100)

st.sidebar.divider()
if st.sidebar.button("↯ RESET SYSTEM"):
    reset_data()

# --- MAIN PANEL: OPERATIONAL DATA ---
blocked_list = get_blocked_ips()
logs = get_logs()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⊘ Blocked Threats")
    if blocked_list:
        df_blocked = pd.DataFrame(blocked_list, columns=["Blocked IPs"])
        st.table(df_blocked)
    else:
        st.info("No threats detected.")

with col2:
    st.markdown("### ▧ Operational Statistics")
    # Metric values are WHITE, labels are PURPLE
    st.metric("Total Analysis", len(logs))
    st.metric("Neutralized", len(blocked_list))

# --- LIVE TRAFFIC LOGS ---
st.divider()
st.markdown("### ⧖ Live Analysis Stream")
log_container = st.container(height=400)

with log_container:
    for log in reversed(logs):
        log_text = log.strip()
        if "ATTACK" in log_text or "DANGER" in log_text:
            st.markdown(f"<div class='log-entry' style='border-left-color: #ff0000; color: #ff4b4b;'>✖ <b>[DANGER]</b> {log_text}</div>", unsafe_allow_html=True)
        elif "ALLOWED" in log_text:
            st.markdown(f"<div class='log-entry' style='border-left-color: #00ffcc; color: #00ffcc;'>✔ <b>[SECURE]</b> {log_text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='log-entry'>📡 {log_text}</div>", unsafe_allow_html=True)

# Auto Refresh
time.sleep(2)
st.rerun()
