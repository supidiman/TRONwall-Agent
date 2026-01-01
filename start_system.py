
import subprocess
import os
import sys

def launch():
    print(" TRONwall Sistemi Başlatılıyor...")
    # WAF ve AI modüllerini arka planda başlatır
    subprocess.Popen([sys.executable, "waf_core/server.py"])
    subprocess.Popen([sys.executable, "ai_agent/decision_engine.py"])
    print("Sistemler Aktif. Analiz terminalden izlenebilir.")

if __name__ == "__main__":
    launch()
