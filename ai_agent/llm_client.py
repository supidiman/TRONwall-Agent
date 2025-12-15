import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. .env dosyasındaki gizli değişkenleri yükle
load_dotenv()

# 2. API Anahtarını yapılandır
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("HATA: API anahtarı bulunamadı. .env dosyasını kontrol et.")
else:
    try:
        genai.configure(api_key=api_key)

        # 3. Model Seçimi (Listendeki güncel modeli kullanıyoruz)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 4. Prompt gönder
        print("Siber güvenlik uzmanına bağlanılıyor...")
        response = model.generate_content("Sen bir siber güvenlik uzmanısın. Kısa ve etkileyici bir şekilde merhaba de.")
        
        # 5. Cevabı yazdır
        print("-" * 30)
        print(response.text)
        print("-" * 30)
        
    except Exception as e:
        print(f"Bir hata oluştu: {e}")