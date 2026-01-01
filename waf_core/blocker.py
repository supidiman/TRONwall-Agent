import json
import os

# --- 1. KISIM: GARANTİ DOSYA YOLU ---
# __file__ = bu dosyanın yeri (waf_core/blocker.py)
# dirname = waf_core
# dirname(dirname) = Proje Ana Dizini (TRONwall-Agent)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLACKLIST_FILE = os.path.join(BASE_DIR, "ai_agent", "blocked_ips.json")

def is_blocked(ip):
    """
    Gelen IP'nin yasaklı olup olmadığını kontrol eder.
    Her çağrıda dosyayı yeniden okur (Cache sorunu olmaz).
    Hem Liste [] hem Sözlük {} formatını destekler.
    """
    # Dosya henüz oluşmadıysa yasak yok demektir
    if not os.path.exists(BLACKLIST_FILE):
        return False

    try:
        with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # --- 2. KISIM: SENİN YAZDIĞIN AKILLI KONTROL ---
            
            # DURUM 1: Eğer dosya bir LİSTE ise (Örn: ["1.1.1.1"])
            if isinstance(data, list):
                return ip in data
                
            # DURUM 2: Eğer dosya bir SÖZLÜK ise (Örn: {"blocked_ips": [...]})
            elif isinstance(data, dict):
                blocked_list = data.get("blocked_ips", [])
                return ip in blocked_list
            
            # Tanımsız format
            else:
                return False

    except Exception as e:
        # Dosya bozuksa veya okunamazsa sistemi durdurma, izin ver geçsin
        print(f"Blocklist okuma hatası: {e}")
        return False