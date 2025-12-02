from flask import Flask, request
import datetime

app = Flask(_name_)

@app.route('/')
def home():
    # Zamanı ve IP'yi al
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_adresi = request.remote_addr
    basliklar = dict(request.headers)

    # Terminale süslü log bas
    print(f"\n[LOG - {zaman}]")
    print(f"⚡ Gelen İstek IP: {ip_adresi}")
    print(f"📋 Headers: {basliklar}")
    print("-" * 50)

    return "TRONwall Active - WAF Core Online 🛡️"

if _name_ == '_main_':
    # Sunucuyu başlat
    app.run(host='0.0.0.0', port=5000)
