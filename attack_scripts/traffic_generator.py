import requests
import time
import random

# WAF Sunucusunun adresi (1. üyenin yazdığı server.py burada çalışır)
URL = "http://127.0.0.1:5000"

# Saldırı örnekleri (AI'yı test etmek için)
PAYLOADS = [
    "<script>alert('XSS')</script>",   # XSS Saldırısı
    "' OR 1=1 --",                      # SQL Injection
    "../../etc/passwd",                 # Dosya Erişimi
    "normal_istek"                      # Masum trafik
]

def test_baslat():
    print("🚀 TRONwall Saldırı Botu Başlatıldı...")
    while True:
        # %20 ihtimalle saldırı, %80 normal trafik gönder
        p = random.choice(PAYLOADS)
        try:
            res = requests.get(URL, params={"data": p})
            print(f"Gönderildi: {p[:15]}... | Sonuç: {res.status_code}")
        except:
            print("❌ HATA: Sunucu kapalı! Lütfen once server.py'ı calistirin.")
        
        time.sleep(2) # 2 saniyede bir istek atar

if __name__ == "__main__":
    test_baslat()
