import requests
import time
import random

# Flask WAF Sunucu Adresi
TARGET_URL = "http://127.0.0.1:5000"

# RAG ve AI'ı tetikleyecek profesyonel payloadlar
ATTACK_VECTORS = {
    "XSS": ["<script>alert('TRON_PWNED')</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)"],
    "SQLi": ["' OR '1'='1", "UNION SELECT NULL, username, password FROM users--", "1; DROP TABLE logs"],
    "Traversal": ["../../etc/passwd", "..\\..\\windows\\win.ini", "/etc/shadow"],
    "Command": ["; ls -la", "| whoami", "&& dir"]
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x4) AppleWebKit/537.36",
    "TRON-Scanner/1.0",
    "Evil-Bot/6.6.6"
]

def fire_traffic():
    print("🛡️ TRONwall Advanced Traffic Generator v2.0")
    print("------------------------------------------")
    while True:
        try:
            is_attack = random.random() < 0.30 # %30 Saldırı oranı
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            
            if is_attack:
                v_type = random.choice(list(ATTACK_VECTORS.keys()))
                payload = random.choice(ATTACK_VECTORS[v_type])
                print(f"🔥 [{v_type}] Saldırısı Gönderiliyor: {payload[:30]}...")
                
                # Hem GET hem POST denemesi yaparak middleware'i test et
                if random.choice([True, False]):
                    requests.get(TARGET_URL, params={"search": payload}, headers=headers)
                else:
                    requests.post(TARGET_URL, data={"input": payload}, headers=headers)
            else:
                print("✅ Normal Trafik Gönderiliyor...")
                requests.get(TARGET_URL, headers=headers)
                
        except Exception as e:
            print(f"❌ Sunucu Bağlantı Hatası: {e}")
            
        time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    fire_traffic()
