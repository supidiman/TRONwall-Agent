import os
import json

# --- AYARLAR ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'rag_memory', 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Dosya Yolları
SIGNATURES_FILE = os.path.join(DATA_DIR, 'attack_signatures.json')
WHITELIST_FILE = os.path.join(DATA_DIR, 'whitelist.json')

# Varsayılan Veriler
DEFAULT_SIGNATURES = [
    {
        "id": "A001",
        "name": "SQL Injection (Basic)",
        "pattern": "(OR|AND)\\s+['\"]?1['\"]?\\s*=\\s*['\"]?1",
        "description": "Temel SQL Enjeksiyon denemesi.",
        "risk_level": "HIGH",
        "rule_template": {"action": "block_ip"}
    }
]

DEFAULT_WHITELIST = {
    "allowed_ips": ["127.0.0.1"],
    "allowed_paths": ["/dashboard", "/login"],
    "trusted_users": ["admin"]
}

def create_directory(path):
    """Klasör yoksa oluşturur."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Klasör oluşturuldu: {path}")
    else:
        print(f"Klasör zaten var: {path}")

def create_json_file(path, default_data):
    """JSON dosyası yoksa varsayılan verilerle oluşturur."""
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        print(f"Dosya oluşturuldu: {path}")
    else:
        print(f"Dosya zaten var: {path}")

def main():
    print("==========================================")
    print("TRONwall-Agent Kurulum Sihirbazı")
    print("==========================================\n")

    # 1. Klasörleri Oluştur
    create_directory(DATA_DIR)
    create_directory(LOGS_DIR)

    # 2. JSON Dosyalarını Oluştur
    create_json_file(SIGNATURES_FILE, DEFAULT_SIGNATURES)
    create_json_file(WHITELIST_FILE, DEFAULT_WHITELIST)

    print("\n==========================================")
    print("Kurulum Tamamlandı! Sistem kullanıma hazır.")
    print("==========================================")

if __name__ == "__main__":
    main()