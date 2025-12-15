import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Ayarları Yükle
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key bulunamadı! .env dosyasını kontrol edin.")

# --- DÜZELTME BURADA ---
# transport='rest' parametresi, bağlantının donmasını engeller.
genai.configure(api_key=api_key, transport="rest")

# 2. PROMPT
TRONWALL_SYSTEM_PROMPT = """
Sen TRONwall adında otonom bir güvenlik analizcisisin. 
Görevin: Sana verilen log girdisini analiz etmek ve siber güvenlik tehditlerini tespit etmektir.

Kurallar:
1. SADECE geçerli bir JSON çıktısı ver.
2. Asla yorum yapma, sohbet etme veya markdown blokları (```json) kullanma.
3. Çıktı formatın tam olarak aşağıdaki şemaya uymalıdır:

{
  "attack_detected": boolean, 
  "attack_type": "string (örn: SQL Injection, XSS, DDoS, None)",
  "confidence_score": number (0.0 ile 1.0 arası),
  "suggested_action": "string (örn: block_ip, log_incident, none)"
}
"""

def analyze_log(log_entry):
    # 3. Model Ayarları
    # Eğer 'gemini-2.5-flash' yine sorun çıkarırsa 'gemini-1.5-flash' yapabilirsin.
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=TRONWALL_SYSTEM_PROMPT,
        generation_config={"response_mime_type": "application/json", "temperature": 0.1}
    )

    print(f"\n[TRONwall] Log Analiz Ediliyor: {log_entry}")
    
    try:
        # 4. Analizi Yap
        response = model.generate_content(log_entry)
        
        # 5. JSON Dönüştürme
        result_json = json.loads(response.text)
        
        print("-" * 40)
        print(json.dumps(result_json, indent=4))
        print("-" * 40)
        
        return result_json

    except json.JSONDecodeError:
        print("HATA: Model JSON döndürmedi.")
        print(response.text)
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    test_log = "User input: ' OR 1=1 --"
    analyze_log(test_log)