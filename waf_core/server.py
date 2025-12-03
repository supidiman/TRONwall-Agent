from flask import Flask, request
from middleware import request_parser, log_transaction
from blocker import is_blocked

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    # 1. Veriyi Al
    data = request_parser(request)

    # 2. Yasaklı mı?
    if is_blocked(data['ip']):
        log_transaction(data, "BLOCKED")
        return "🚫 ERİŞİM ENGELLENDİ", 403

    # 3. İzin Ver
    log_transaction(data, "ALLOWED")
    return "TRONwall Active - System Secure 🛡️"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)