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

    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r") as f:
                blocked_list = json.load(f)
        except (json.JSONDecodeError, ValueError):
            blocked_list = []

    if ip_address not in blocked_list:
        blocked_list.append(ip_address)
        
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(blocked_list, f, indent=4)
        print(f"🚫 [İNFAZ] {ip_address} kara listeye alındı.")
    else:
        print(f"ℹ️ {ip_address} zaten kara listede.")

def pre_filter(log_entry):
    """
    AKILLI FİLTRELEME (SMART FILTERING)
    Basit string kontrolleri ile bariz temiz olan istekleri eler.
    True dönerse -> AI analiz etmeli (Şüpheli veya Hata kodu)
    False dönerse -> AI analize gerek yok (Temiz)
    """
    # 1. Şüpheli Karakter Kontrolü (SQLi, XSS belirtileri)
    suspicious_chars = ["<", ">", "'", "--", "script", "union", "select"]
    
    for char in suspicious_chars:
        if char in log_entry.lower(): # Küçük harfe çevirip bakmak daha güvenli
            return True # Şüpheli karakter var, AI görsün!

    # 2. HTTP Status Kontrolü
    # Eğer log içinde " 200 " (Başarılı) varsa ve yukarıdaki şüpheli karakterler yoksa temizdir.
    # Not: Log formatına göre status kodunun yeri değişebilir ama genelde boşluklar arasındadır.
    if " 200 " in log_entry:
        return False # Temiz 200 isteği, AI'a gerek yok.

    # 3. Diğer Durumlar (404, 500, 403 vb.)
    # Hata kodları bazen Fuzzing veya Brute Force belirtisi olabilir.
    return True

def start_watching():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("")

    print(f"--- TRONwall Karar Mekanizması & İnfaz Memuru Başlatıldı ---")
    print(f"⚡ Smart Filtering (Akıllı Filtreleme) Aktif.")
    
    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            log_entry = line.strip()
            if log_entry:
                attacker_ip = log_entry.split(" ")[0].split("-")[0].strip()
                
                # --- AKILLI FİLTRELEME DEVREDE ---
                if not pre_filter(log_entry):
                    # Eğer temizse döngünün başına dön (AI'ı çağırma)
                    print(f"⏩ [ATLANDI] Temiz İstek: {attacker_ip}") # Debug için açılabilir
                    continue
                # ---------------------------------

                print(f"b[AI Analiz Ediyor...] {attacker_ip}") # Filtreyi geçenleri görelim
                result = analyze_log(log_entry)

                if result:
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