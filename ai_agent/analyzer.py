import os
import json
import google.generativeai as genai
import time
import sys
from dotenv import load_dotenv

# --- 1. AYARLAR & IMPORTLAR ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# .env dosyasını güvenli yükle
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key bulunamadı! .env dosyasını kontrol edin.")

genai.configure(api_key=api_key, transport="rest")




# Whitelist Modülü
try:
    from rag_memory.whitelist_manager import WhitelistManager
    whitelist = WhitelistManager()
    print("Whitelist Modülü Devrede.")
except ImportError:
    whitelist = None
    print("Whitelist yüklenemedi.")


# RAG (Hafıza) Modülü
try:
    from rag_memory.retriever import KnowledgeBase
    kb = KnowledgeBase()
except ImportError:
    kb = None

# LEARNER (Öğrenme) Modülü
try:
    from rag_memory.learner import AutoLearner
    learner = AutoLearner()
    print("Öğrenme Modülü (Learner) Devrede.")
except ImportError:
    print(" Öğrenme modülü yüklenemedi.")
    learner = None

TRONWALL_SYSTEM_PROMPT = """
Sen TRONwall adında otonom bir güvenlik analizcisisin. 
Görevin: Log girdisini analiz et ve tehditleri tespit et.

Kurallar:
1. SADECE JSON çıktısı ver.
2. Çıktı formatı:
{
  "attack_detected": boolean, 
  "attack_type": "string (örn: SQL Injection, XSS, DDoS, None)",
  "confidence_score": number (0.0 - 1.0),
  "suggested_action": "string",
  "explanation": "string"
}
"""

def analyze_log(log_entry, retry_count=0):
    """
    Logu analiz eder. Hata alırsa yönetir.
    """
    print(f"\n[TRONwall] Analiz: {log_entry[:50]}...")


    # --- ADIM 0: BEYAZ LİSTE KONTROLÜ (Whitelist) ---
    # Eğer güvenliyse, ne AI'ya ne de Hafızaya sorma. Direkt geçir.
    if whitelist:
        is_safe, reason = whitelist.is_whitelisted(log_entry)
        if is_safe:
            print(f" WHITELIST: Güvenli olarak işaretlendi. ({reason})")
            return {
                "attack_detected": False,
                "attack_type": "None",
                "confidence_score": 1.0,
                "suggested_action": "allow",
                "explanation": f"Yönetici tarafından beyaz listeye alınmış: {reason}"
            }

    # --- ADIM 1: HAFIZA KONTROLÜ (RAG) ---
    if kb:
        matches = kb.search_knowledge(log_entry)
        if matches:
            print(" HAFIZADA BULUNDU! (Gemini Atlandı)")
            best = matches[0]
            
            # --- GÜVENLİ VERİ OKUMA (KeyError Çözümü) ---
            # Veritabanında bazı alanlar eksik olsa bile kod çökmesin diye .get() kullanıyoruz.
            
            # Action verisini güvenli al, yoksa 'block_ip' yap
            rule_template = best.get('rule_template', {})
            action = rule_template.get('action', 'block_ip')
            
            # Saldırı adını güvenli al
            attack_name = best.get('attack_name', best.get('name', 'Known Attack'))
            
            return {
                "attack_detected": True,
                "attack_type": attack_name,
                "confidence_score": 1.0,
                "suggested_action": action,
                "explanation": f"RAG veritabanında kayıtlı tehdit. Desen: {best.get('matched_pattern', 'N/A')}"
            }

    # --- ADIM 2: YAPAY ZEKA ANALİZİ (AI) ---
    print("Bilinmiyor. Gemini'ye soruluyor...")
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash', 
        system_instruction=TRONWALL_SYSTEM_PROMPT,
        generation_config={"response_mime_type": "application/json", "temperature": 0.1}
    )

    try:
        response = model.generate_content(log_entry)
        result = json.loads(response.text)
        
        # --- ADIM 3: OTOMATİK ÖĞRENME (SELF-LEARNING) ---
        if result.get("attack_detected") and learner:
            print(" YENİ SALDIRI TESPİT EDİLDİ! Hafızaya kaydediliyor...")
            
            learner.learn_new_attack(
                attack_type=result.get("attack_type"),
                log_pattern=log_entry,
                risk_level="HIGH"
            )
            
        return result

    except Exception as e:
        # KOTA HATASI YÖNETİMİ (Rate Limit Fix)
        if "429" in str(e) or "Quota" in str(e):
            if retry_count < 3:
                wait_time = 20
                print(f" API Kotası (429)! {wait_time} saniye bekleniyor... (Deneme {retry_count+1})")
                time.sleep(wait_time)
                return analyze_log(log_entry, retry_count + 1)
        
        print(f"HATA: {e}")
        return {"attack_detected": False, "error": str(e)}

if __name__ == "__main__":
    # Test amaçlı
    test_log = "SELECT * FROM users WHERE admin = '1' OR '1'='1'"
    analyze_log(test_log)