# TRONwall-Agent

**TRONwall-Agent**, yapay zeka destekli otonom bir Web Application Firewall (WAF) sistemidir. Sistem, gerçek zamanlı trafik analizi yaparak siber saldırıları tespit eder, engeller ve otomatik öğrenme yeteneği sayesinde sürekli kendini geliştirir.

## Genel Bakış

TRONwall-Agent, modern web uygulamalarını siber saldırılara karşı korumak için tasarlanmış entegre bir güvenlik çözümüdür. Sistem, üç katmanlı analiz yaklaşımı kullanarak hem performans hem de güvenlik arasında optimal denge sağlar:

1. **Whitelist Kontrolü**: Güvenli IP ve path'ler için anında geçiş
2. **RAG Hafıza**: Bilinen saldırı desenlerini hızlıca tespit etme
3. **AI Analizi**: Google Gemini AI ile bilinmeyen tehditleri analiz etme

Sistem, tespit ettiği yeni saldırıları otomatik olarak öğrenir ve gelecekte benzer saldırıları daha hızlı tespit edebilir hale gelir.

## Özellikler

### Temel Özellikler

- **Gerçek Zamanlı Analiz**: Gelen HTTP istekleri anlık olarak analiz edilir
- **Otomatik Tehdit Tespiti**: SQL Injection, XSS, Path Traversal, Command Injection ve daha fazlası
- **IP Engelleme**: Saldırgan IP'ler otomatik olarak kara listeye alınır
- **Otomatik Öğrenme**: Yeni saldırı türleri sistem tarafından öğrenilir ve hafızaya kaydedilir
- **Canlı Dashboard**: Streamlit tabanlı görsel izleme ve yönetim paneli
- **Akıllı Filtreleme**: Gereksiz AI çağrılarını önleyen ön filtreleme mekanizması

### Güvenlik Özellikleri

- Çok katmanlı güvenlik yaklaşımı
- Regex tabanlı pattern matching
- AI destekli tehdit analizi
- Otomatik saldırı imzası oluşturma
- Whitelist/Blacklist yönetimi
- Detaylı log kayıtları

### Performans Özellikleri

- Akıllı ön filtreleme ile %80-90 daha az AI çağrısı
- RAG hafıza ile bilinen saldırılar için 0ms yanıt süresi
- Lazy loading ile optimize edilmiş kaynak kullanımı
- Regex pattern caching

## Sistem Gereksinimleri

### Yazılım Gereksinimleri

- **Python**: 3.8 veya üzeri
- **İşletim Sistemi**: Windows, Linux, macOS
- **Disk Alanı**: En az 100 MB (log dosyaları hariç)
- **RAM**: En az 512 MB (önerilen: 1 GB+)
- **Ağ**: İnternet bağlantısı (Gemini API erişimi için)

### Python Paketleri

Tüm bağımlılıklar `requirements.txt` dosyasında listelenmiştir:

```
flask
google-generativeai
python-dotenv
requests
psutil
pandas
streamlit
locust
```

## Kurulum

### Adım 1: Repository'yi Klonlayın

```bash
git clone https://github.com/kullanici/tronwall-agent.git
cd tronwall-agent
```

### Adım 2: Python Sanal Ortamı Oluşturun (Önerilir)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### Adım 4: Veritabanını ve Dosya Sistemini Başlatın

```bash
python init_db.py
```

Bu komut şunları oluşturur:
- Gerekli klasör yapısı
- Varsayılan veri dosyaları (attack_signatures.json, whitelist.json, blocked_ips.json)
- Log dosyaları
- Konfigürasyon şablonları

### Adım 5: Ortam Değişkenlerini Yapılandırın

`.env` dosyası oluşturun (veya `.env.example` dosyasını `.env` olarak kopyalayın):

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

`.env` dosyasını düzenleyin ve Google Gemini API anahtarınızı ekleyin:

```
GEMINI_API_KEY=your_api_key_here
```

**API Anahtarı Nasıl Alınır:**
1. https://makersuite.google.com/app/apikey adresine gidin
2. Google hesabınızla giriş yapın
3. "Create API Key" butonuna tıklayın
4. Oluşturulan anahtarı `.env` dosyasına ekleyin

## Yapılandırma

### Temel Yapılandırma

`.env` dosyasında aşağıdaki ayarları yapabilirsiniz:

```
# Zorunlu
GEMINI_API_KEY=your_api_key_here

# Opsiyonel Flask Ayarları
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# Opsiyonel Log Ayarları
LOG_LEVEL=INFO
LOG_FILE=traffic.log
MAX_LOG_SIZE=10485760

# Opsiyonel Güvenlik Ayarları
MAX_REQUESTS_PER_MINUTE=100
BLOCK_DURATION_HOURS=24
AUTO_LEARNING_ENABLED=True
```

### Saldırı İmzaları Yapılandırması

`rag_memory/data/attack_signatures.json` dosyasını düzenleyerek saldırı imzalarını özelleştirebilirsiniz. Her imza şu yapıdadır:

```json
{
    "id": "A001",
    "name": "SQL Injection",
    "description": "Açıklama",
    "risk_level": "CRITICAL",
    "regex_patterns": [
        "(?i)(\\bunion\\s+select\\b)"
    ],
    "rule_template": {
        "action": "block_ip",
        "reason": "SQL Injection detected"
    }
}
```

### Whitelist Yapılandırması

`rag_memory/data/whitelist.json` dosyasını düzenleyerek güvenli IP'leri ve path'leri yönetebilirsiniz:

```json
{
    "allowed_ips": ["127.0.0.1", "192.168.1.1"],
    "allowed_paths": ["/dashboard", "/login"],
    "trusted_users": ["admin"]
}
```

## Kullanım

### Sistemi Başlatma

#### Yöntem 1: Otomatik Başlatma (Önerilen)

```bash
python start_system.py
```

Bu komut şunları başlatır:
- WAF sunucusu (Port 5000)
- AI karar motoru
- Log izleme sistemi

#### Yöntem 2: Manuel Başlatma

**Terminal 1 - WAF Sunucusu:**
```bash
cd waf_core
python server.py
```

**Terminal 2 - AI Karar Motoru:**
```bash
cd ai_agent
python decision_engine.py
```

### Dashboard'u Başlatma

Yeni bir terminal açın ve şu komutu çalıştırın:

```bash
streamlit run dashboard.py
```

Dashboard varsayılan olarak `http://localhost:8501` adresinde açılır.

### Sistem Erişimi

- **WAF Endpoint**: http://localhost:5000
- **Dashboard**: http://localhost:8501
- **Flask Dashboard**: http://localhost:5000/dashboard

### Test Etme

Sistem testleri için `tests` modülünde çeşitli test araçları bulunmaktadır:

#### Saldırı Simülasyonu

**Karışık Trafik (Normal + Saldırı):**
```bash
cd tests/attack_scripts
python traffic_generator.py
```
Bu script, %20 saldırı, %80 normal trafik içeren karışık bir trafik simülasyonu oluşturur.

**Zorunlu Saldırı Simülasyonu:**
```bash
cd tests/attack_scripts
python force_attack.py
```
Belirli bir IP adresinden çeşitli saldırı türleri gönderir ve sistemin tepkisini test eder.

#### Normal Trafik Simülasyonu

Sadece normal, saldırı içermeyen trafik göndermek için:

```bash
python tests/normal_traffic.py
```

#### Yük Testi (Stress Test)

Locust kullanarak yük testi yapmak için:

```bash
cd tests/stress_tests
locust -f locustfile.py --host=http://localhost:5000
```

Tarayıcıda `http://localhost:8089` adresini açarak test arayüzüne erişebilirsiniz.

## Mimari Yapı

### Dizin Yapısı

```
TRONwall-Agent/
├── ai_agent/                 # AI analiz modülleri
│   ├── analyzer.py          # Ana analiz motoru
│   ├── decision_engine.py   # Karar mekanizması
│   ├── llm_client.py        # Gemini AI istemcisi
│   ├── daily_report.py      # Günlük rapor üretici
│   └── blocked_ips.json     # Engellenen IP listesi
├── waf_core/                # WAF çekirdek modülleri
│   ├── server.py            # Flask web sunucusu
│   ├── middleware.py        # İstek işleme katmanı
│   ├── blocker.py           # IP engelleme motoru
│   └── templates/           # HTML şablonları
│       └── dashboard.html
├── rag_memory/              # RAG (Hafıza) sistemi
│   ├── retriever.py         # Bilgi tabanı erişimi
│   ├── learner.py           # Otomatik öğrenme
│   ├── whitelist_manager.py # Whitelist yönetimi
│   └── data/                # Veri dosyaları
│       ├── attack_signatures.json
│       └── whitelist.json
├── tests/                   # Test modülleri
│   ├── attack_scripts/      # Saldırı simülasyonları
│   │   ├── traffic_generator.py  # Karışık trafik üretici
│   │   └── force_attack.py       # Zorunlu saldırı simülatörü
│   ├── normal_traffic.py    # Normal trafik simülatörü
│   └── stress_tests/        # Yük testleri
│       └── locustfile.py    # Locust yük testi konfigürasyonu
├── logs/                    # Log dosyaları
├── dashboard.py             # Streamlit dashboard
├── start_system.py          # Sistem başlatıcı
├── init_db.py               # Veritabanı başlatıcı
├── requirements.txt         # Python bağımlılıkları
└── README.md                # Bu dosya
```

### Veri Akışı

1. **HTTP İsteği Gelir**
   - Flask sunucusu isteği yakalar
   - Middleware isteği parse eder
   - İstek bilgileri `traffic.log` dosyasına yazılır

2. **IP Kontrolü**
   - Blocker modülü IP'yi `blocked_ips.json` dosyasında kontrol eder
   - Engellenmişse 403 Forbidden döner

3. **Analiz Süreci**
   - Decision Engine log dosyasını izler
   - Pre-filter ile ön filtreleme yapılır
   - Analyzer modülü üç katmanlı analiz yapar:
     a. Whitelist kontrolü
     b. RAG hafıza kontrolü
     c. AI analizi (Gerekirse)

4. **Karar ve Aksiyon**
   - Saldırı tespit edilirse IP engellenir
   - Yeni saldırılar Learner modülü tarafından öğrenilir
   - Sonuçlar loglanır ve dashboard'a yansır

## Modül Açıklamaları

### WAF Core Modülleri

#### server.py
Flask tabanlı HTTP sunucusu. Gelen istekleri karşılar, IP engelleme kontrolü yapar ve dashboard endpoint'i sağlar.

**Ana Fonksiyonlar:**
- `home()`: Ana endpoint, tüm HTTP isteklerini karşılar
- `dashboard()`: Flask tabanlı dashboard endpoint'i
- `get_recent_logs()`: Son 10 log kaydını okur
- `get_blocked_list()`: Engellenen IP listesini döndürür

#### middleware.py
İstek işleme katmanı. Gelen HTTP isteklerini parse eder ve yapılandırılmış formata çevirir.

**Ana Fonksiyonlar:**
- `request_parser(request)`: HTTP isteğini parse eder
- `log_transaction(data, action)`: Log kaydı oluşturur

#### blocker.py
IP engelleme motoru. `blocked_ips.json` dosyasını okur ve IP kontrolü yapar.

**Ana Fonksiyonlar:**
- `is_blocked(ip)`: IP'nin engellenmiş olup olmadığını kontrol eder

### AI Agent Modülleri

#### analyzer.py
Ana analiz motoru. Üç katmanlı analiz sistemi kullanır: Whitelist -> RAG -> AI.

**Ana Fonksiyonlar:**
- `analyze_log(log_entry)`: Log girdisini analiz eder
- API kota yönetimi ve retry mekanizması içerir

#### decision_engine.py
Karar mekanizması ve infaz memuru. Log dosyasını izler, analiz yapar ve aksiyon alır.

**Ana Fonksiyonlar:**
- `start_watching()`: Log dosyasını gerçek zamanlı izler
- `pre_filter(log_entry)`: Akıllı ön filtreleme yapar
- `block_ip(ip_address)`: IP'yi kara listeye ekler

#### llm_client.py
Google Gemini AI istemcisi. API bağlantısını yönetir.

#### daily_report.py
Günlük güvenlik raporu üretici. Log dosyalarını analiz eder ve executive summary oluşturur.

### RAG Memory Modülleri

#### retriever.py
Bilgi tabanı erişimi. `attack_signatures.json` dosyasındaki regex desenleri ile log satırlarını tarar.

**Ana Fonksiyonlar:**
- `search_knowledge(log_line)`: Log satırını regex desenleri ile tarar

#### learner.py
Otomatik öğrenme modülü. AI'ın tespit ettiği yeni saldırıları öğrenir ve veritabanına ekler.

**Ana Fonksiyonlar:**
- `learn_new_attack(attack_type, log_pattern, risk_level)`: Yeni saldırıyı öğrenir
- `load_db()`: Veritabanını yükler
- `save_db(data)`: Veritabanını kaydeder

#### whitelist_manager.py
Beyaz liste yöneticisi. Güvenli IP'leri ve path'leri yönetir.

**Ana Fonksiyonlar:**
- `add_ip(ip_address)`: Güvenli IP ekler
- `add_path(path)`: Güvenli path ekler
- `is_whitelisted(log_entry)`: Whitelist kontrolü yapar

### Dashboard Modülleri

#### dashboard.py
Streamlit tabanlı görsel izleme paneli. Gerçek zamanlı sistem durumu, log akışı ve istatistikler sunar.

**Özellikler:**
- Canlı log akışı
- Engellenen IP listesi
- Sistem kaynak kullanımı (CPU, RAM)
- Otomatik yenileme (2 saniyede bir)
- Sistem sıfırlama fonksiyonu

### Test Modülleri

Test modülleri, sistemin çalışmasını doğrulamak ve performansını test etmek için kullanılır.

#### attack_scripts/traffic_generator.py
Karışık trafik simülatörü. Normal ve saldırı trafiğini karışık olarak gönderir.

**Özellikler:**
- %20 saldırı, %80 normal trafik oranı
- Çeşitli saldırı türleri (SQL Injection, XSS, Path Traversal)
- Gerçekçi trafik simülasyonu
- Saniyede 5-10 istek hızı

**Kullanım:**
```bash
cd tests/attack_scripts
python traffic_generator.py
```

#### attack_scripts/force_attack.py
Zorunlu saldırı simülatörü. Belirli bir IP adresinden çeşitli saldırı türleri gönderir.

**Özellikler:**
- Sabit saldırgan IP adresi (test için)
- Çoklu saldırı vektörleri (SQL Injection, XSS, RCE, LFI)
- Saldırı sonuçlarını analiz eder
- Sistemin engelleme mekanizmasını test eder

**Ana Fonksiyonlar:**
- `run_simulation()`: Saldırı simülasyonunu başlatır
- Farklı saldırı kategorilerinden rastgele payload seçer
- HTTP yanıt kodlarını analiz eder (403, 200, 404)

**Kullanım:**
```bash
cd tests/attack_scripts
python force_attack.py
```

#### normal_traffic.py
Normal trafik simülatörü. Sadece güvenli, saldırı içermeyen istekler gönderir.

**Özellikler:**
- Sadece normal sayfa istekleri
- Gerçekçi kullanıcı davranışı simülasyonu
- Rastgele bekleme süreleri (0.5-2 saniye)
- Gerçek User-Agent header'ları

**Ana Fonksiyonlar:**
- `simulate_users()`: Normal kullanıcı trafiğini simüle eder
- Güvenli sayfa listesinden rastgele seçim yapar

**Kullanım:**
```bash
python tests/normal_traffic.py
```

#### stress_tests/locustfile.py
Yük testi konfigürasyonu. Locust framework kullanarak sistem yükünü test eder.

**Özellikler:**
- Eşzamanlı kullanıcı simülasyonu
- Yük testi ve performans analizi
- Web tabanlı test arayüzü
- Özelleştirilebilir bekleme süreleri

**Ana Bileşenler:**
- `TronwallUser`: Kullanıcı simülasyon sınıfı
- `visit()`: Ana endpoint'i test eden task

**Kullanım:**
```bash
cd tests/stress_tests
locust -f locustfile.py --host=http://localhost:5000
```

**Test Arayüzü:**
Test başladıktan sonra `http://localhost:8089` adresinden Locust web arayüzüne erişebilirsiniz.

## API Dokümantasyonu

### Flask Endpoints

#### GET/POST /
Ana endpoint. Tüm HTTP isteklerini karşılar.

**Yanıt:**
- `200 OK`: İstek başarılı - "TRONwall Active - System Secure"
- `403 Forbidden`: IP engellenmiş - "ERİŞİM ENGELLENDİ"

#### GET /dashboard
Flask tabanlı dashboard endpoint'i.

**Yanıt:** HTML dashboard sayfası

### Log Formatı

`traffic.log` dosyasındaki her satır bir JSON objesidir:

```json
{
    "timestamp": "2024-01-01 12:00:00",
    "ip": "192.168.1.100",
    "url": "http://example.com/page?id=1",
    "method": "GET",
    "user_agent": "Mozilla/5.0...",
    "payload": null,
    "action": "ALLOWED"
}
```

### Analiz Sonuç Formatı

AI analiz sonuçları şu formattadır:

```json
{
    "attack_detected": true,
    "attack_type": "SQL Injection",
    "confidence_score": 0.95,
    "suggested_action": "block_ip",
    "explanation": "SQL injection attempt detected in query parameter"
}
```

## Güvenlik

### Güvenlik Özellikleri

- **Çok Katmanlı Koruma**: Whitelist, RAG, AI analizi
- **Otomatik IP Engelleme**: Saldırgan IP'ler anında engellenir
- **Regex Injection Koruması**: `re.escape()` kullanımı
- **API Key Güvenliği**: `.env` dosyasında saklama
- **Hata Yönetimi**: Sistem çökmesi önleme mekanizmaları
- **Log Kayıtları**: Tüm aktiviteler kaydedilir

### Güvenlik Önerileri

1. `.env` dosyasını asla versiyon kontrol sistemine eklemeyin
2. Production ortamında `FLASK_DEBUG=False` kullanın
3. Düzenli olarak log dosyalarını temizleyin
4. API anahtarınızı düzenli olarak değiştirin
5. Whitelist'i düzenli olarak gözden geçirin
6. Saldırı imzalarını güncel tutun

### Bilinen Sınırlamalar

- JSON tabanlı veri saklama (büyük ölçekli sistemler için veritabanı önerilir)
- Tek sunucu mimarisi (yüksek trafik için cluster gerekebilir)
- API kota limitleri (Gemini API için)

## Sorun Giderme

### Yaygın Hatalar ve Çözümleri

#### Hata: "API Key bulunamadı!"
**Çözüm:** `.env` dosyasının proje kök dizininde olduğundan ve `GEMINI_API_KEY` değişkeninin doğru ayarlandığından emin olun.

#### Hata: "No module named 'google.generativeai'"
**Çözüm:**
```bash
pip install --upgrade google-generativeai
```

#### Hata: "Flask module not found"
**Çözüm:**
```bash
pip install --upgrade flask
```

#### Hata: "Port 5000 already in use"
**Çözüm:** Farklı bir port kullanın veya 5000 portunu kullanan uygulamayı kapatın.

#### Hata: "attack_signatures.json bulunamadı"
**Çözüm:** `python init_db.py` komutunu çalıştırın.

#### Dashboard açılmıyor
**Çözüm:**
```bash
pip install --upgrade streamlit
streamlit run dashboard.py
```

### Performans Sorunları

#### Sistem yavaş çalışıyor
- Log dosyasının boyutunu kontrol edin
- Pre-filter ayarlarını gözden geçirin
- RAG hafızasındaki pattern sayısını optimize edin

#### API kota limiti aşıldı
- `.env` dosyasında `AUTO_LEARNING_ENABLED=False` yapın
- Pre-filter hassasiyetini artırın
- API planınızı yükseltin

### Log Analizi

Log dosyalarını analiz etmek için:

```bash
# Son 100 satırı görüntüle
tail -n 100 traffic.log

# Hata kayıtlarını filtrele
grep "ERROR" traffic.log

# Engellenen istekleri göster
grep "BLOCKED" traffic.log
```

## Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları takip edin:

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

### Kod Standartları

- PEP 8 kod stilini takip edin
- Fonksiyon ve sınıflar için docstring kullanın
- Yeni özellikler için test yazın
- README'yi güncelleyin

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## Destek

Sorularınız veya sorunlarınız için:

- **Issues**: GitHub Issues sayfasını kullanın
- **Dokümantasyon**: Proje dokümantasyonunu inceleyin
- **E-posta**: destek@example.com

## Versiyon Geçmişi

### v1.0.0 (2024-01-01)
- İlk stabil sürüm
- Temel WAF fonksiyonları
- AI analiz entegrasyonu
- Otomatik öğrenme sistemi
- Dashboard arayüzü

## Yazar

TRONwall-Agent Development Team

## Referanslar

- [Flask Dokümantasyonu](https://flask.palletsprojects.com/)
- [Google Gemini AI](https://ai.google.dev/)
- [Streamlit Dokümantasyonu](https://docs.streamlit.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Not:** Bu sistem test ve geliştirme amaçlıdır. Production ortamında kullanmadan önce kapsamlı testler yapılmalıdır.

