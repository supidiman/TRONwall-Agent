import sys
import os

# --- Import Ayarları ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ai_agent.analyzer import analyze_log
except ImportError:
    from ai_agents.analyzer import analyze_log

print("==================================================")
print("🛡️ TRONWALL BEYAZ LİSTE (WHITELIST) TESTİ")
print("==================================================\n")

# SENARYO: Çok tehlikeli bir SQL Injection saldırısı
saldiri_kodu = "SELECT * FROM users WHERE password = '' OR '1'='1'"

# --- DURUM 1: YABANCI BİRİ (Engellenmeli) ---
print("--- TEST 1: Yabancı IP (10.20.30.40) Saldırıyor ---")
log_yabanci = f"IP: 10.20.30.40 - User: hacker - Msg: {saldiri_kodu}"
sonuc1 = analyze_log(log_yabanci)

if sonuc1.get("attack_detected"):
    print("✅ BAŞARILI: Sistem yabancıyı yakaladı!\n")
else:
    print("❌ HATA: Sistem yabancıyı kaçırdı!\n")


# --- DURUM 2: PATRON (99.99.99.99) (İzin Verilmeli) ---
print("--- TEST 2: Güvenli IP (99.99.99.99) Aynı Şeyi Yapıyor ---")
# Not: Logun içinde "99.99.99.99" geçmesi yeterli, kodumuz string araması yapıyor.
log_patron = f"IP: 99.99.99.99 - User: admin - Msg: {saldiri_kodu}" 
sonuc2 = analyze_log(log_patron)

# Burada 'attack_detected' FALSE olmalı çünkü whitelist devreye girdi.
if not sonuc2.get("attack_detected") and sonuc2.get("suggested_action") == "allow":
    print("✅ BAŞARILI: Sistem patronu tanıdı ve izin verdi! (Whitelist Çalışıyor)")
    print(f"   Açıklama: {sonuc2.get('explanation')}")
else:
    print("❌ HATA: Sistem patronu da engelledi! Whitelist çalışmıyor.")

print("\n==================================================")