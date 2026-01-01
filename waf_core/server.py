from flask import Flask, request, render_template, abort, jsonify
import json
import os

# --- SENİN MODÜLLERİN (Mevcut yapıyı koruyoruz) ---
try:
    from middleware import request_parser, log_transaction 
    from blocker import is_blocked
except ImportError:
    # Eğer test yaparken modüller yoksa hata vermesin diye (Geliştirme amaçlı)
    def request_parser(req): return {"ip": req.remote_addr, "url": req.url, "method": req.method, "payload": str(req.args)}
    def log_transaction(data, action): print(f"LOG: {action} - {data}")
    def is_blocked(ip): return False

app = Flask(__name__)

# --- YAPILANDIRMA ---
LOG_FILE = "traffic.log"

# Dosya Yolları (waf_core klasörünün bir üstüne çıkıp ai_agent'a gider)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGNATURES_FILE = os.path.join(BASE_DIR, "ai_agent", "attack_signatures.json")
WHITELIST_FILE = os.path.join(BASE_DIR, "ai_agent", "whitelist.json")
BLACKLIST_FILE = os.path.join(BASE_DIR, "ai_agent", "blocked_ips.json")


# --- EKSİK OLAN FONKSİYONLAR (BURALARI EKLEDİM) ---

def load_attack_signatures():
    """
    RAG hafızasındaki (JSON) saldırı imzalarını yükler.
    Her istekte çağrıldığı için veritabanı güncellemelerini anlık görür.
    """
    signatures = []
    # Varsayılanlar (Dosya okunamazsa güvenlik açığı olmasın diye)
    defaults = ["UNION SELECT", "<script>", "alert(", "etc/passwd", "jndi:ldap"]
    signatures.extend(defaults)

    if os.path.exists(SIGNATURES_FILE):
        try:
            with open(SIGNATURES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    # 1. Regex listesini al
                    patterns = item.get("regex_patterns", [])
                    
                    # 2. Veya tekil pattern varsa onu al
                    if item.get("pattern"):
                        patterns.append(item.get("pattern"))
                    
                    # Listeye ekle
                    signatures.extend(patterns)
        except Exception as e:
            print(f"Hata - İmzalar yüklenemedi: {e}")
            
    return signatures

def load_whitelist():
    """Whitelist dosyasını yükler"""
    if os.path.exists(WHITELIST_FILE):
        try:
            with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"allowed_ips": [], "allowed_paths": []}

# --- İÇERİK TARAMA FONKSİYONU ---

def check_payload_for_attack(parsed_data):
    """
    Her istekte JSON dosyasını yeniden okur.
    Böylece Dashboard'dan eklenen kural ANINDA geçerli olur.
    """
    # 1. İmzaları Taze Yükle (ARTIK BU FONKSİYON TANIMLI, HATA VERMEZ)
    current_signatures = load_attack_signatures() 
    
    # Veriyi string'e çevir
    data_str = str(parsed_data).lower()
    
    for sig in current_signatures:
        # Basit string temizliği (Regex karakterlerini temizle)
        clean_sig = sig.replace("\\", "").replace("(?i)", "").lower()
        
        # Çok kısa kelimeleri (örn: "a") yoksay, hatalı pozitif olmasın
        if len(clean_sig) > 3 and clean_sig in data_str:
            print(f"🛡️ TEHDİT YAKALANDI: {sig}")
            return True, sig
            
    return False, None


# --- YARDIMCI FONKSİYONLAR ---
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
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict): blocked = data.get("blocked_ips", [])
                elif isinstance(data, list): blocked = data
        except: pass
    return blocked


# --- GÜVENLİK DUVARI (MIDDLEWARE) ---
@app.before_request
def security_check():
    """
    Her istekten ÖNCE çalışır.
    Sıralama: Whitelist -> IP Ban -> İçerik Tarama (Payload)
    """
    # Statik dosyaları atla
    if request.path.startswith('/static'): return None

    # 1. ADIM: Whitelist Kontrolü (Güvenli ise direkt geçsin)
    whitelist = load_whitelist()
    client_ip = request.remote_addr
    
    if client_ip in whitelist.get("allowed_ips", []) or request.path in whitelist.get("allowed_paths", []):
        # Whitelist ise engelleme yapma
        return None 

    # İsteği Parse Et
    data = request_parser(request)
    
    # 2. ADIM: IP Yasaklı mı? (blocker.py)
    if is_blocked(data['ip']):
        log_transaction(data, "BLOCKED")
        return "🚫 ERİŞİM ENGELLENDİ (IP BAN) - TRONwall AI Security", 403

    # 3. ADIM: Paket İçeriği Temiz mi? (RAG/AI Kontrolü)
    is_attack, signature = check_payload_for_attack(data)
    
    if is_attack:
        print(f"⚔️ PROAKTİF SAVUNMA: {signature} içeren paket engellendi!")
        log_transaction(data, "BLOCKED")
        return f"🚫 ERİŞİM ENGELLENDİ (ZARARLI İÇERİK: {signature}) - TRONwall WAF", 403

    # 4. ADIM: Temiz
    log_transaction(data, "ALLOWED")

# ---------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def home():
    return "TRONwall Active - System Secure 🛡️"

@app.route('/dashboard')
def dashboard():
    logs = get_recent_logs()
    blocked_ips = get_blocked_list()
    return render_template('dashboard.html', logs=logs, blocked_ips=blocked_ips)

# Test Rotaları
@app.route('/login', methods=['GET', 'POST'])
def login(): return "Login Sayfası"

@app.route('/search', methods=['GET'])
def search(): return "Arama Sonuçları..."

@app.route('/images', methods=['GET'])
def images(): return "Resim Görüntüleyici"

@app.route('/cmd', methods=['GET'])
def cmd(): return "Komut Paneli"

@app.route('/download', methods=['GET'])
def download(): return "İndirme Paneli"
    
@app.route('/view', methods=['GET'])
def view(): return "Görüntüleme Paneli"
    
@app.route('/comment', methods=['GET', 'POST'])
def comment(): return "Yorum Paneli"

if __name__ == '__main__':
    if not os.path.exists(LOG_FILE): open(LOG_FILE, 'w').close()
    print("🔥 TRONwall Server (Proaktif Mod) Başlatıldı...")
    app.run(host='0.0.0.0', port=5000, debug=False)