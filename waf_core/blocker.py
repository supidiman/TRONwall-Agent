import json
import os

BLACKLIST_FILE = "waf_core/blacklist.json"

def is_blocked(ip):
    if not os.path.exists(BLACKLIST_FILE):
        return False
    try:
        with open(BLACKLIST_FILE, "r") as f:
            data = json.load(f)
            return ip in data.get("blocked_ips", [])
    except:
        return False