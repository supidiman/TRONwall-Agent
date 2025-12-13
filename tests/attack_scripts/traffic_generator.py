import requests
import random
import time
import json
from collections import Counter

# --- Terminal renkleri için (TRON teması) ---
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    GOOD_COLOR = Fore.CYAN      # İyi trafik (mavi)
    BAD_COLOR = Fore.RED        # Saldırı (kırmızı)
    WARN_COLOR = Fore.WHITE     # Uyarı / hata (beyaz)
    RESET = Style.RESET_ALL
except ImportError:
    # colorama yoksa renksiz devam et
    GOOD_COLOR = BAD_COLOR = WARN_COLOR = RESET = ""


# Hedef WAF sunucusu (waf_core/server.py içindeki Flask app)
TARGET_URL = "http://127.0.0.1:5000/"

# Farklı IP'lerden geliyormuş gibi yapmak için sahte IP havuzu
FAKE_IPS = [
    "102.54.94.97",
    "11.22.33.44",
    "185.76.9.12",
    "45.81.23.90",
    "72.15.67.222",
    "201.97.11.5",
]

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
        "User-Agent": random.choice(NORMAL_USER_AGENTS),
        # IP spoofing: istekler farklı IP'lerden geliyormuş gibi
        "X-Forwarded-For": random.choice(FAKE_IPS),
    }

    try:
        response = session.get(url, headers=headers, timeout=2)
        print(GOOD_COLOR + f"[NORMAL] {url} -> {response.status_code}" + RESET)
    except Exception as e:
        print(WARN_COLOR + f"[NORMAL] İstek hatası: {e}" + RESET)


def send_malicious_request(session: requests.Session):
    """Zararlı payload içeren POST isteği gönder.
       Kullanılan payload'ı geri döndürür (özet rapor için).
    """
    payload = random.choice(MALICIOUS_PAYLOADS)
    headers = {
        "User-Agent": "EvilBot/1.0",
        "Content-Type": "application/x-www-form-urlencoded",
        # Saldırganın IP'si gibi gözüksün
        "X-Forwarded-For": random.choice(FAKE_IPS),
    }
    data = {
        "search": payload
    }

    try:
        response = session.post(TARGET_URL, headers=headers, data=data, timeout=2)
        print(BAD_COLOR + f"[MALICIOUS] Payload gönderildi -> {response.status_code}" + RESET)
        return payload
    except Exception as e:
        print(WARN_COLOR + f"[MALICIOUS] İstek hatası: {e}" + RESET)
        return None


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
    payload_counter = Counter()  # hangi zararlı payload ne kadar kullanılmış?

    print(f"[TRONwall Traffic Generator] Başlıyor...")
    print(f"Toplam istek: {total_requests} (≈ %80 normal, %20 zararlı)\n")

    for i in range(1, total_requests + 1):
        # %20 zararlı, %80 normal
        if random.random() < 0.2:
            payload_used = send_malicious_request(session)
            malicious_count += 1
            if payload_used:
                payload_counter[payload_used] += 1
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

    # --- JSON ÖZET RAPOR OLUŞTUR ---
    if payload_counter:
        most_used_payload = payload_counter.most_common(1)[0][0]
    else:
        most_used_payload = None

    summary = {
        "total_requests": total_requests,
        "normal": normal_count,
        "malicious": malicious_count,
        "most_used_payload": most_used_payload
    }

    with open("traffic_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)

    print("\n[TRONwall] Özet rapor 'traffic_summary.json' dosyasına kaydedildi.")
    print(summary)


if __name__ == "__main__":
    # İstersen buradaki değerlerle oynayabilirsin
    run_traffic_generator(
        total_requests=200,
        min_rps=5.0,
        max_rps=10.0
    )
