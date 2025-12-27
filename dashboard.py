import streamlit as st
import json
import os
import pandas as pd
import psutil

st.sidebar.header("💻 Sistem Sağlığı")
st.sidebar.write(f"CPU Kullanımı: %{psutil.cpu_percent()}")
st.sidebar.write(f"RAM Kullanımı: %{psutil.virtual_memory().percent()}")

st.set_page_config(page_title="TRONwall Dashboard", layout="wide")
st.title("🛡️ TRONwall Komuta Merkezi")

def load_data():
    blocked = []
    if os.path.exists("ai_agent/blocked_ips.json"):
        with open("ai_agent/blocked_ips.json", "r") as f:
            blocked = json.load(f)
    
    logs = []
    if os.path.exists("waf_core/traffic.log"):
        with open("waf_core/traffic.log", "r") as f:
            logs = f.readlines()
    return blocked, logs

blocked, logs = load_data()

c1, c2 = st.columns(2)
c1.metric("Toplam İstek", len(logs))
c2.metric("Engellenen Saldırgan", len(blocked))

st.subheader("📡 Canlı Log Akışı")
st.text("".join(logs[-10:])) # Son 10 logu gösterir

if st.button("Verileri Yenile"):
    st.rerun()
