from flask import Flask, request, render_template
import json
import os
from middleware import request_parser, log_transaction
from blocker import is_blocked

app = Flask(__name__)

# Dosya Yolları
LOG_FILE = "traffic.log"
# AI'ın oluşturduğu yasaklı listesini bul (3. Hafta mantığıyla aynı)
BLACKLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "ai_agent", "blocked_ips.json")

def get_recent_logs():
    """Traffic.log dosyasından son 10 satırı okur"""
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Son 10 satırı al ve ters çevir (En yeni en üstte olsun)
                for line in reversed(lines[-10:]):
                    try:
                        logs.append(json.loads(line))
                    except:
                        continue
        except Exception as e:
            print(f"Log okuma hatası: {e}")
    return logs

def get_blocked_list():
    """AI'ın oluşturduğu blocked_ips.json dosyasından banlı IP'leri okur"""
    blocked = []
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r") as f:
                data = json.load(f)
                # Hem liste hem sözlük formatını destekle (3. Hafta fix)
                if isinstance(data, dict):
                    blocked = data.get("blocked_ips", [])
                elif isinstance(data, list):
                    blocked = data
        except:
            pass
    return blocked

@app.route('/', methods=['GET', 'POST'])
def home():
    data = request_parser(request)
    
    if is_blocked(data['ip']):
        log_transaction(data, "BLOCKED")
        return "🚫 ERİŞİM ENGELLENDİ", 403

    log_transaction(data, "ALLOWED")
    return "TRONwall Active - System Secure 🛡️"

# --- YENİ EKLENEN KISIM: DASHBOARD ROTASI ---
@app.route('/dashboard')
def dashboard():
    logs = get_recent_logs()
    blocked_ips = get_blocked_list()
    # Verileri HTML'e gönder
    return render_template('dashboard.html', logs=logs, blocked_ips=blocked_ips)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)