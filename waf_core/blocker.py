import json
import os

# Dosya yolunu belirle (ai_agent klasöründeki dosya)
BLACKLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "ai_agent", "blocked_ips.json")

def is_blocked(ip):
    """
    Hem Liste [] hem de Sözlük {} formatını destekleyen akıllı kontrol.
    """
    if not os.path.exists(BLACKLIST_FILE):
        return False

    try:
        with open(BLACKLIST_FILE, "r") as f:
            data = json.load(f)
            
            # DURUM 1: Eğer dosya bir LİSTE ise (Örn: ["1.1.1.1"])
            if isinstance(data, list):
                return ip in data
                
            # DURUM 2: Eğer dosya bir SÖZLÜK ise (Örn: {"blocked_ips": [...]})
            elif isinstance(data, dict):
                return ip in data.get("blocked_ips", [])
            
            else:
                return False

    except Exception as e:
        # Hata olsa bile sunucuyu çökertme, sadece logla ve geç
        print(f"Blocklist hatası (Göz ardı edildi): {e}")
        return False