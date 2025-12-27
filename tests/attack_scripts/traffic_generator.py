import requests
import time
import random

URL = "http://127.0.0.1:5000"
ATTACKS = ["<script>alert(1)</script>", "' OR 1=1 --", "../../etc/passwd"]
NORMALS = ["Anasayfa", "Hakkimizda", "Urunler", "Iletisim"]

def start_bot():
    print("🚀 TRONwall Saldırı Botu Aktif...")
    while True:
        # %20 Saldırı, %80 Normal trafik ayarı
        if random.random() < 0.20:
            payload = random.choice(ATTACKS)
            label = "🔥 SALDIRI"
        else:
            payload = random.choice(NORMALS)
            label = "✅ NORMAL "
        
        try:
            requests.get(URL, params={"data": payload})
            print(f"{label}: {payload[:15]}...")
        except:
            print("❌ Sunucuya erişilemiyor!")
        
        time.sleep(random.uniform(0.1, 0.2)) # Saniyede ~5-10 istek

if __name__ == "__main__":
    start_bot()
