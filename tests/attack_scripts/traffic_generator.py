import random
import time
import threading
from urllib.parse import urlencode

import requests

# ================== AYARLAR ==================
BASE_URL = "http://localhost:8000"  # WAF geliştiricisinin server.py portuna göre ayarla
RPS = 8  # saniyede istek sayısı (5–10 arası önerilmişti)
DURATION_SECONDS = 60  # toplam test süresi
MALICIOUS_RATIO = 0.2  # %20 zararlı trafik
# ============================================


NORMAL_PATHS = [
    "/", "/home", "/about", "/products", "/contact"
]

MALICIOUS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<script>confirm('XSS')</script>",
    "\"><script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
]

HEADERS_NORMAL = [
    {"User-Agent": "Mozilla/5.0"},
    {"User-Agent": "Chrome/120.0"},
    {"User-Agent": "Safari/17.0"},
]

HEADERS_MALICIOUS = [
    {"User-Agent": "sqlmap/1.0"},
    {"User-Agent": "evil-bot/2.1"},
]


def build_normal_request():
    path = random.choice(NORMAL_PATHS)
    url = BASE_URL + path

    params = {
        "page": random.choice(["1", "2", "3"]),
        "q": random.choice(["tron", "blog", "docs", "products"]),
    }

    headers = random.choice(HEADERS_NORMAL)

    return {
        "method": "GET",
        "url": url,
        "params": params,
        "headers": headers,
    }


def build_malicious_request():
    path = random.choice(NORMAL_PATHS)
    url = BASE_URL + path

    payload = random.choice(MALICIOUS_PAYLOADS)

    # XSS payload query string içinde
    params = {
        "search": payload,
        "debug": "true",
    }

    headers = random.choice(HEADERS_MALICIOUS)

    return {
        "method": "GET",
        "url": url,
        "params": params,
        "headers": headers,
    }


def send_request(session, request_data, index):
    method = request_data["method"]
    url = request_data["url"]
    params = request_data["params"]
    headers = request_data["headers"]

    try:
        if method == "GET":
            resp = session.get(url, params=params, headers=headers, timeout=3)
        else:
            resp = session.post(url, data=params, headers=headers, timeout=3)

        # Kısa log
        query = urlencode(params)
        print(f"[{index}] {method} {url}?{query} -> {resp.status_code}")

    except Exception as e:
        print(f"[HATA] İstek gönderilemedi: {e}")


def traffic_loop():
    """
    Bu fonksiyon, verilen süre boyunca her saniye RPS kadar istek atar.
    %80 normal, %20 zararlı olacak şekilde dağıtır.
    """
    end_time = time.time() + DURATION_SECONDS
    session = requests.Session()

    request_index = 0

    while time.time() < end_time:
        start = time.time()

        threads = []

        for _ in range(RPS):
            request_index += 1

            # Zararlı mı, normal mi?
            if random.random() < MALICIOUS_RATIO:
                req_data = build_malicious_request()
            else:
                req_data = build_normal_request()

            t = threading.Thread(
                target=send_request, args=(session, req_data, request_index)
            )
            t.start()
            threads.append(t)

        # O saniyedeki tüm istekler bitsin
        for t in threads:
            t.join()

        # 1 saniye aralığını korumaya çalış
        elapsed = time.time() - start
        sleep_time = max(0, 1.0 - elapsed)
        time.sleep(sleep_time)

    print("Test tamamlandı.")


if __name__ == "__main__":
    print(f"TRONwall traffic generator başlıyor...")
    print(f"Target: {BASE_URL}, RPS={RPS}, süre={DURATION_SECONDS} sn, kötü oran={MALICIOUS_RATIO*100:.0f}%")
    traffic_loop()
