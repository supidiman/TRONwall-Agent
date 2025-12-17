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

# RAG (Hafıza) Modülü
try:
    from rag_memory.retriever import KnowledgeBase
    kb = KnowledgeBase()
except ImportError:
    kb = None

# LEARNER (Öğrenme) Modülü - YENİ EKLENDİ! 🚀
try:
    from rag_memory.learner import AutoLearner
    learner = AutoLearner()
    print("Öğrenme Modülü (Learner) Devrede.")
except ImportError:
    print("Öğrenme modülü yüklenemedi.")
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

def analyze_log(log_entry):
    print(f"\n[TRONwall] Analiz: {log_entry[:50]}...")

    # --- ADIM 1: HAFIZA KONTROLÜ (RAG) ---
    if kb:
        matches = kb.search_knowledge(log_entry)
        if matches:
            print("HAFIZADA BULUNDU! (Gemini Atlandı)")
            best = matches[0]
            return {
                "attack_detected": True,
                "attack_type": best['attack_name'],
                "confidence_score": 1.0,
                "suggested_action": best['rule_template']['action'],
                "explanation": f"RAG veritabanında kayıtlı tehdit. Desen: {best['matched_pattern']}"
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
        # Eğer Gemini "Saldırı Var" dediyse VE Öğrenici aktifse -> KAYDET!
        if result.get("attack_detected") and learner:
            print("YENİ SALDIRI TESPİT EDİLDİ! Hafızaya kaydediliyor...")
            
            # Learner fonksiyonunu çağırıyoruz
            learner.learn_new_attack(
                attack_type=result.get("attack_type"),
                log_pattern=log_entry, # Logun kendisini desen olarak kaydet
                risk_level="HIGH"
            )
            
        return result

    except Exception as e:
        print(f"HATA: {e}")
        return {"attack_detected": False, "error": str(e)}

