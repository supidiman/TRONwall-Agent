import requests
import time
import random

URL = "http://127.0.0.1:5000"

# Normal, saldırı içermeyen masum sayfalar
SAFE_PAGES = [
    "/",
    "/login",             # Parametresiz giriş
    "/search?q=python",   # Normal bir arama
    "/search?q=hello",
    "/images",
    "/cmd"                # Sadece sayfayı görüntüleme (saldırı kodu yok)
]

def simulate_users():
    print("😊 Masum Kullanıcı Trafiği Başlatılıyor...")
    print("-" * 50)
    
    while True:
        page = random.choice(SAFE_PAGES)
        full_url = URL + page
        
        # Farklı tarayıcılar gibi davranalım
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(full_url, headers=headers)
            print(f"✅ İstek: {page} | Durum: {response.status_code}")
        except:
            print("❌ Sunucuya ulaşılamadı!")
            
        # İnsan gibi rastgele bekle (0.5 ile 2 saniye arası)
        time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    simulate_users()