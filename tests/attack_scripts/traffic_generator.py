import time
import random
import requests

# WAF sunucusunun adresi
# WAF yazan arkadaşın server.py'yi hangi portta çalıştırıyorsa onu yazın.
WAF_BASE_URL = "http://127.0.0.1:8000"

# Normal istek gidecek path'ler
NORMAL_PATHS = [
    "/",
    "/home",
    "/about",
    "/products",
]

# Zararlı payload'lar (XSS ve basit SQLi denemeleri)
ATTACK_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert('xss')>",
    "' OR 1=1 --",
    "\" OR \"1\"=\"1",
]

def send_normal_request(session: requests.Session):
    """Masum bir GET isteği gönderir."""
    path = random.choice(NORMAL_PATHS)
    url = WAF_BASE_URL + path

    try:
        resp = session.get(url, timeout=3)
        print(f"[NORMAL] {url} -> {resp.status_code}")
    except Exception as e:
        print(f"[NORMAL][HATA] {url} -> {e}")


def send_attack_request(session: requests.Session):
    """Zararlı bir payload içeren isteği gönderir."""
    path = "/search"
    url = WAF_BASE_URL + path

    payload = random.choice(ATTACK_PAYLOADS)
    params = {"q": payload}

    try:
        resp = session.get(url, params=params, timeout=3)
        print(f"[ATTACK] {url}?q={payload} -> {resp.status_code}")
    except Exception as e:
        print(f"[ATTACK][HATA] {url} -> {e}")


def main(total_requests: int = 100, rps: float = 5.0, attack_ratio: float = 0.2):
    """
    total_requests : Toplam kaç istek atılsın
    rps            : Saniyedeki istek sayısı (requests per second)
    attack_ratio   : Saldırı oranı (0.2 -> %20 saldırı, %80 normal)
    """
    delay = 1.0 / rps  # iki istek arasındaki bekleme süresi (saniye)

    session = requests.Session()

    print(f"Başlıyor: toplam={total_requests}, rps={rps}, attack_ratio={attack_ratio}")
    for i in range(1, total_requests + 1):
        is_attack = random.random() < attack_ratio

        if is_attack:
            send_attack_request(session)
        else:
            send_normal_request(session)

        # Çok hızlı gitmemek için uyku
        time.sleep(delay)

    print("Trafik üretimi bitti.")


if __name__ == "__main__":
    # Varsayılan: 100 istek, saniyede 5 istek, %20 saldırı
    main()

