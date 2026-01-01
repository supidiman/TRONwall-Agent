import requests
import time
import random

URL = "http://127.0.0.1:5000"

# --- SABİT SALDIRGAN IP'Sİ (TEST İÇİN) ---
ATTACKER_IP = "66.66.66.66"

ATTACK_VECTORS = {
    "SQL_INJECTION": ["/products?id=-1 UNION SELECT 1,version()", "/login?user=admin' OR '1'='1"],
    "XSS_ATTACK": ["/search?q=<script>alert('HACK')</script>", "/comment?msg=<img src=x onerror=alert(1)>"],
    "RCE_ATTACK": ["/cmd?run=cat /etc/passwd", "/cmd?run=ping 127.0.0.1"],
    "LFI_ATTACK": ["/download?file=../../etc/shadow", "/view?page=../../boot.ini"]
}

def run_simulation():
    print(f"💀 TEHDİT SİMÜLATÖRÜ AKTİF (IP: {ATTACKER_IP})...")
    print("-" * 60)

    # Headerlar SABİT IP ile ayarlanıyor
    headers = {
        "X-Forwarded-For": ATTACKER_IP,
        "User-Agent": "Mozilla/5.0 (EvilBot/2.0)"
    }

    while True:
        category = random.choice(list(ATTACK_VECTORS.keys()))
        payload = random.choice(ATTACK_VECTORS[category])
        target_url = URL + payload

        try:
            # İsteği gönder
            response = requests.get(target_url, headers=headers)
            
            # --- SONUÇ ANALİZİ ---
            if response.status_code == 403:
                # EĞER 403 ALIYORSAK SİSTEM ÇALIŞIYOR DEMEKTİR
                print(f"🛡️ [ENGEL - 403] Saldırı Püskürtüldü! -> {payload[:30]}...")
            
            elif response.status_code == 200:
                print(f"⚠️ [GEÇTİ - 200] Sistem İzin Verdi! -> {payload[:30]}...")
                
            elif response.status_code == 404:
                # 404 alması WAF'ın çalışmadığı anlamına gelmez, sayfa yoktur.
                # Ama payload zararlıysa WAF yine de 403 vermeliydi.
                print(f"⚠️ [GEÇTİ - 404] Sayfa Yok (WAF Yakalamadı) -> {payload[:30]}...")

        except Exception as e:
            print(f"❌ Bağlantı Hatası: {e}")

        time.sleep(1.5) # Çok hızlı yapma, AI'ın banlamasına 1 saniye ver

if __name__ == "__main__":
    run_simulation()