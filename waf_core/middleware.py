import json
import datetime

LOG_FILE = "traffic.log"

def request_parser(request):
    parsed_data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "url": request.url,
        "method": request.method,
        "user_agent": request.headers.get('User-Agent', 'Unknown'),
        "payload": request.get_data(as_text=True) if request.method == 'POST' else None
    }
    return parsed_data

def log_transaction(data, action):
    final_log = data.copy()
    final_log["action"] = action
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        json.dump(final_log, f)
        f.write("\n")