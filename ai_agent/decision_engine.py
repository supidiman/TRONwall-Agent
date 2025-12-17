import time
import os
import json
from analyzer import analyze_log

# Ayarlar
LOG_FILE = "traffic.log"
BLACKLIST_FILE = "blocked_ips.json"

def block_ip(ip_address):
    """
    Saldırgan IP adresini blocked_ips.json dosyasına ekler.
    """
    blocked_list = []

    # 1. Mevcut listeyi oku
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r") as f:
                blocked_list = json.load(f)
        except (json.JSONDecodeError, ValueError):
            blocked_list = []

    # 2. IP zaten listede yoksa ekle (Tekrarı önler)
    if ip_address not in blocked_list:
        blocked_list.append(ip_address)
        
        # 3. Güncel listeyi dosyaya yaz
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(blocked_list, f, indent=4)
        print(f"🚫 [İNFAZ] {ip_address} kara listeye alındı.")
    else:
        print(f"ℹ️ {ip_address} zaten kara listede.")

def start_watching():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("")

    print(f"--- TRONwall Karar Mekanizması & İnfaz Memuru Başlatıldı ---")
    
    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            log_entry = line.strip()
            if log_entry:
                # IP adresini ayıkla (Satırın başındaki ilk blok)
                attacker_ip = log_entry.split(" ")[0].split("-")[0].strip()
                
                result = analyze_log(log_entry)

                if result:
                    # DÜZELTME: "block_ip" ifadesi suggested_action içinde geçiyor mu?
                    action = result.get("suggested_action", "")
                    is_attack = result.get("attack_detected", False)

                    if is_attack and "block_ip" in action:
                        print(f"⚠️ KRİTİK: {result.get('attack_type')} tespit edildi!")
                        block_ip(attacker_ip)
                    else:
                        print(f"✅ Analiz tamamlandı: {result.get('attack_type', 'Temiz')}")

if __name__ == "__main__":
    try:
        start_watching()
    except KeyboardInterrupt:
        print("\nSistem kapatılıyor...")