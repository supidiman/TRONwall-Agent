import requests
import random
import time

# Hedef WAF sunucusu (waf_core/server.py içindeki Flask app)
TARGET_URL = "http://127.0.0.1:5000/"

# %80 oranında kullanılacak masum istekler
NORMAL_PATHS = [
    "/", 
    "/?page=home",
    "/?page=about",
    "/?page=contact",
]

NORMAL_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
]

# %20 oranında kullanılacak zararlı payload'lar (XSS + benzeri saldırılar)
MALICIOUS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert('XSS')>",
    "<ScRiPt>alert('pwned')</sCrIpT>",
    "\"'><script>alert('xss')</script>",
]

def send_normal_request(session: requests.Session):
    """Masum görünen GET isteği gönder."""
    path = random.choice(NORMAL_PATHS)
    url = TARGET_URL.rstrip("/") + path

    headers = {
        "User-Agent": random.choice(NORMAL_USER_AGENTS)
    }

    try:
        response = session.get(url, headers=headers, timeout=2)
        print(f"[NORMAL] {url} -> {response.status_code}")
    except Exception as e:
        print(f"[NORMAL] İstek hatası: {e}")


def send_malicious_request(session: requests.Session):
    """Zararlı payload içeren POST isteği gönder."""
    payload = random.choice(MALICIOUS_PAYLOADS)
    headers = {
        "User-Agent": "EvilBot/1.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "search": payload
    }

    try:
        response = session.post(TARGET_URL, headers=headers, data=data, timeout=2)
        print(f"[MALICIOUS] Payload gönderildi -> {response.status_code}")
    except Exception as e:
        print(f"[MALICIOUS] İstek hatası: {e}")


def run_traffic_generator(
    total_requests: int = 200,
    min_rps: float = 5.0,
    max_rps: float = 10.0
):
    """
    total_requests: Toplam istek sayısı
    min_rps, max_rps: Saniyede 5–10 istek arası (kabaca)
    """
    session = requests.Session()
    normal_count = 0
    malicious_count = 0

    print(f"[TRONwall Traffic Generator] Başlıyor...")
    print(f"Toplam istek: {total_requests} (≈ %80 normal, %20 zararlı)\n")

    for i in range(1, total_requests + 1):
        # %20 zararlı, %80 normal
        if random.random() < 0.2:
            send_malicious_request(session)
            malicious_count += 1
        else:
            send_normal_request(session)
            normal_count += 1

        # Saniyede 5–10 istek için bekleme (0.1s – 0.2s)
        rps = random.uniform(min_rps, max_rps)   # Kağıt üstünde hız
        sleep_time = 1.0 / rps
        time.sleep(sleep_time)

        # Her 20 istekte bir küçük özet
        if i % 20 == 0:
            print(f"\n--- Durum ---")
            print(f"Toplam istek: {i}")
            print(f"Normal  : {normal_count}")
            print(f"Zararlı : {malicious_count}")
            print("--------------\n")

    print("\n[TRONwall Traffic Generator] Bitti.")
    print(f"Toplam Normal  İstek : {normal_count}")
    print(f"Toplam Zararlı İstek : {malicious_count}")


if __name__ == "__main__":
    # İstersen buradaki değerlerle oynayabilirsin
    run_traffic_generator(
        total_requests=200,
        min_rps=5.0,
        max_rps=10.0
    )

