from flask import Flask, request
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_adresi = request.remote_addr
    basliklar = dict(request.headers)

    print(f"\n[LOG - {zaman}]")
    print(f"⚡ Gelen İstek IP: {ip_adresi}")
    print(f"📋 Headers: {basliklar}")
    print("-" * 50)

    return "TRONwall Active - WAF Core Online 🛡️"

@app.route('/search')
def search():
    q = request.args.get("q", "")
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_adresi = request.remote_addr

    print(f"\n[SEARCH - {zaman}]")
    print(f"🔍 Arama Sorgusu: {q}")
    print(f"📌 IP: {ip_adresi}")
    print("-" * 50)

    return f"Aranan ifade: {q}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
