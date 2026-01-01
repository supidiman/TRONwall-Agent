from flask import Flask, request, render_template, abort
import json
import os
# Kendi modüllerini koruyoruz
from middleware import request_parser, log_transaction 
from blocker import is_blocked

app = Flask(__name__)

# --- YAPILANDIRMA ---
LOG_FILE = "traffic.log"
# Yolu senin yapına uygun şekilde ayarladım
BLACKLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "ai_agent", "blocked_ips.json")

# --- 1. YENİ ÖZELLİK: PROAKTİF İMZA LİSTESİ ---
# Bu kelimeler geçerse, IP temiz olsa bile WAF anında engeller.
CRITICAL_SIGNATURES = [
    "UNION SELECT", "OR '1'='1", "WAITFOR DELAY",  # SQLi
    "<script>", "alert(", "onerror=", "javascript:", # XSS
    "../", "etc/passwd", "boot.ini", "cat /",       # LFI/RCE
    "ping ", "whoami", "system(", "wget ", "curl "  # Komut Enjeksiyonu
]

# --- 2. YENİ ÖZELLİK: İÇERİK TARAMA FONKSİYONU ---
def check_payload_for_attack(parsed_data):
    """
    request_parser'dan gelen veriyi string'e çevirip
    içinde zararlı imza var mı diye bakar.
    """
    # Veriyi komple stringe çevirip küçük harf yapalım (büyük/küçük harf kaçmasın)
    data_str = str(parsed_data).lower()
    
    for sig in CRITICAL_SIGNATURES:
        if sig.lower() in data_str:
            print(f"🛡️ TEHDİT YAKALANDI: {sig}") # Konsolda görelim
            return True, sig # Yakalandı ve Hangi imza
            
    return False, None

# --- MEVCUT YARDIMCI FONKSİYONLARIN (Log Okuma vs) ---
def get_recent_logs():
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines[-10:]):
                    try:
                        logs.append(json.loads(line))
                    except: continue
        except Exception as e:
            print(f"Log okuma hatası: {e}")
    return logs

def get_blocked_list():
    blocked = []
    path = BLACKLIST_FILE
    # Yol hatası almamak için kontrol
    if not os.path.exists(path):
        # Eğer server.py bir alt klasördeyse (waf_core gibi) bir üstü dene
        path = "ai_agent/blocked_ips.json"
        
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, dict): blocked = data.get("blocked_ips", [])
                elif isinstance(data, list): blocked = data
        except: pass
    return blocked

# --- 3. GÜNCELLENMİŞ GÜVENLİK DUVARI (MIDDLEWARE) ---
@app.before_request
def security_check():
    """
    Her istekten ÖNCE çalışır.
    Hem IP hem de İÇERİK kontrolü yapar.
    """
    if request.path.startswith('/static'):
        return None

    # 1. İsteği Parse Et (Senin middleware modülün)
    data = request_parser(request)
    
    # 2. KONTROL: IP Yasaklı mı? (Senin blocker modülün)
    if is_blocked(data['ip']):
        # Loga 'BLOCKED' olarak işle
        log_transaction(data, "BLOCKED")
        return "🚫 ERİŞİM ENGELLENDİ (IP BAN) - TRONwall AI Security", 403

    # 3. KONTROL (YENİ): Paket İçeriği Temiz mi?
    is_attack, signature = check_payload_for_attack(data)
    
    if is_attack:
        # IP temiz olsa bile içerik kirli! ANINDA ENGELLE.
        # Loga saldırı detayını ekleyelim (Middleware destekliyorsa)
        # Desteklemiyorsa direkt BLOCKED olarak göndeririz.
        print(f"⚔️ PROAKTİF SAVUNMA: {signature} içeren paket engellendi!")
        
        # Log dosyasına saldırı olarak işle
        log_transaction(data, "BLOCKED")
        
        return f"🚫 ERİŞİM ENGELLENDİ (ZARARLI İÇERİK: {signature}) - TRONwall WAF", 403

    # 4. TEMİZ: Yasaklı değil ve içerik temizse izin ver
    log_transaction(data, "ALLOWED")

# ---------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def home():
    return "TRONwall Active - System Secure 🛡️"

@app.route('/dashboard')
def dashboard():
    # Flask dashboard'un (Eğer Streamlit kullanıyorsan burası opsiyoneldir)
    logs = get_recent_logs()
    blocked_ips = get_blocked_list()
    return render_template('dashboard.html', logs=logs, blocked_ips=blocked_ips)

# Test Rotaları
@app.route('/login', methods=['GET', 'POST'])
def login():
    return "Login Sayfası"

@app.route('/search', methods=['GET'])
def search():
    return "Arama Sonuçları..."

@app.route('/images', methods=['GET'])
def images():
    return "Resim Görüntüleyici"

@app.route('/cmd', methods=['GET'])
def cmd():
    return "Komut Paneli"

@app.route('/download', methods=['GET'])
def download():
    return "İndirme Paneli"
    
@app.route('/view', methods=['GET'])
def view():
    return "Görüntüleme Paneli"
    
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    return "Yorum Paneli"

if __name__ == '__main__':
    # Log dosyasını başlat
    if not os.path.exists(LOG_FILE): open(LOG_FILE, 'w').close()
    print("🔥 TRONwall Server (Proaktif Mod) Başlatıldı...")
    app.run(host='0.0.0.0', port=5000, debug=False)