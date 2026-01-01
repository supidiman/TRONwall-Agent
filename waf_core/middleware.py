import json
import datetime

LOG_FILE = "traffic.log"

def request_parser(request):
    """
    Gelen isteği analiz eder ve loglanacak veriyi hazırlar.
    Hem Test Scripti için IP maskelemeyi çözer hem de URL parametrelerini yakalar.
    """
    
    # 1. ADIM: Doğru IP Tespiti (Test Scripti için Kritik)
    # Eğer istekte 'X-Forwarded-For' başlığı varsa (yani saldırgan IP taklidi yapıyorsa)
    # onu gerçek IP olarak kabul et. Yoksa normal bağlantı IP'sini al.
    if request.headers.get('X-Forwarded-For'):
        # Örnek Header: "66.100.20.10, 127.0.0.1" -> İlkini alıyoruz
        client_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        client_ip = request.remote_addr

    # 2. ADIM: Payload Yakalama (Hem GET hem POST için)
    payload_data = None
    
    # Eğer URL parametresi varsa (Örn: /login?user=admin)
    if request.args:
        payload_data = str(request.args.to_dict())
    
    # Eğer Form veya Body verisi varsa (POST isteği)
    elif request.method == 'POST':
        if request.form:
            payload_data = str(request.form.to_dict())
        else:
            payload_data = request.get_data(as_text=True)

    # 3. ADIM: Veriyi Paketle
    parsed_data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": client_ip,  # Artık simülasyon IP'sini görecek
        "url": request.url,
        "method": request.method,
        "user_agent": request.headers.get('User-Agent', 'Unknown'),
        "payload": payload_data  # Artık URL'deki saldırıları da içeriyor
    }
    
    return parsed_data

def log_transaction(data, action):
    """
    Veriyi log dosyasına yazar.
    Hata durumunda sistemi çökertmemesi için try-except bloğu eklendi.
    """
    final_log = data.copy()
    final_log["action"] = action
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            json.dump(final_log, f)
            f.write("\n")
    except Exception as e:
        print(f"Log Yazma Hatası: {e}")