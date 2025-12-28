import sys
import os

# İçe aktarma yollarını ayarla
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_agent.analyzer import analyze_log
except ImportError:
    from ai_agents.analyzer import analyze_log

print("--- RAPOR İÇİN ENTEGRASYON KANIT TESTİ ---")
print("Senaryo: Veritabanında bilinen bir SQL Injection saldırısı gönderiliyor.")
print("Beklenti: Gemini API kullanılmadan, 'HAFIZADA BULUNDU' çıktısı alınması.\n")

# Klasik bir SQL Injection (Regex bunu kesin yakalar)
bilinen_saldiri = "SELECT * FROM users WHERE admin = '1' OR '1'='1'"

analyze_log(bilinen_saldiri)