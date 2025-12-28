import os
import json
import collections
from dotenv import load_dotenv
import google.generativeai as genai

# --- AYARLAR ---
LOG_FILE = "traffic.log"
REPORT_FILE = "daily_executive_summary.txt"

# --- ENV & GEMINI ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY bulunamadı!")

genai.configure(api_key=api_key)

# --- LOG ANALİZİ ---
def analyze_daily_logs():
    attack_types = []
    countries = []

    if not os.path.exists(LOG_FILE):
        print("Log dosyası bulunamadı.")
        return None

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.lower()

            # Basit heuristikler (AI özetleyecek zaten)
            if "sql" in line:
                attack_types.append("SQL Injection")
            elif "xss" in line or "script" in line:
                attack_types.append("XSS")
            elif "ddos" in line or "flood" in line:
                attack_types.append("DDoS")

            if "ru" in line or "russia" in line:
                countries.append("Russia")
            elif "cn" in line or "china" in line:
                countries.append("China")
            elif "tr" in line:
                countries.append("Turkey")

    return attack_types, countries

# --- EXECUTIVE SUMMARY (GEMINI) ---
def generate_executive_summary(attack_types, countries):
    attack_counter = collections.Counter(attack_types)
    country_counter = collections.Counter(countries)

    total_attacks = sum(attack_counter.values())
    most_common_attack = attack_counter.most_common(1)
    most_common_country = country_counter.most_common(1)

    prompt = f"""
You are a cybersecurity executive assistant.

Create a 3-sentence executive summary for a daily security report.

Data:
- Total blocked attacks: {total_attacks}
- Most common attack type: {most_common_attack[0][0] if most_common_attack else 'Unknown'}
- Most common source country: {most_common_country[0][0] if most_common_country else 'Unknown'}

Rules:
- Write in professional business language
- Maximum 3 sentences
- Do NOT include technical details
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    return response.text.strip()

# --- MAIN ---
if __name__ == "__main__":
    result = analyze_daily_logs()

    if not result:
        exit()

    attack_types, countries = result
    summary = generate_executive_summary(attack_types, countries)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(summary)

    print("📊 Günlük Executive Summary oluşturuldu:")
    print("-" * 40)
    print(summary)
    print("-" * 40)
