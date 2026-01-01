# TRONwall-Agent: Detaylı Proje Analiz Raporu

## 📋 Proje Özeti

**TRONwall-Agent**, yapay zeka destekli otonom bir Web Application Firewall (WAF) sistemidir. Sistem, gerçek zamanlı trafik analizi yaparak siber saldırıları tespit eder, engeller ve öğrenme yeteneği sayesinde sürekli kendini geliştirir.

### Ana Özellikler
- 🤖 **AI Destekli Analiz**: Google Gemini AI ile akıllı tehdit tespiti
- 🧠 **Otomatik Öğrenme**: Yeni saldırıları otomatik olarak öğrenip hafızaya kaydetme
- 📚 **RAG (Retrieval-Augmented Generation)**: Geçmiş saldırı verilerini hızlıca geri çağırma
- 🛡️ **Gerçek Zamanlı Engelleme**: Saldırgan IP'leri otomatik olarak kara listeye alma
- 📊 **Canlı Dashboard**: Streamlit ile görsel izleme paneli
- ⚡ **Akıllı Filtreleme**: Gereksiz AI çağrılarını önleyen ön filtreleme mekanizması

---

## 🏗️ Mimari Yapı ve Modüller

### 1. **WAF Core Modülü** (`waf_core/`)

#### 1.1 `server.py` - Flask Web Sunucusu
**İşlevi:**
- Flask tabanlı HTTP sunucusu (Port 5000)
- Gelen HTTP isteklerini yakalar ve işler
- İstekleri middleware'e yönlendirir
- Dashboard endpoint'i sağlar (`/dashboard`)

**Temel Özellikler:**
- `GET` ve `POST` isteklerini dinler
- IP engelleme kontrolü yapar
- Tüm istekleri `traffic.log` dosyasına kaydeder
- HTML dashboard template'i render eder

**Kritik Fonksiyonlar:**
```python
- home(): Ana endpoint, istekleri karşılar
- dashboard(): Canlı izleme paneli
- get_recent_logs(): Son 10 log kaydını okur
- get_blocked_list(): Engellenen IP'leri listeler
```

#### 1.2 `middleware.py` - İstek İşleme Katmanı
**İşlevi:**
- Gelen HTTP isteklerini parse eder
- İstek bilgilerini yapılandırılmış formata çevirir
- Log kayıtlarını oluşturur

**Çıktı Formatı:**
```json
{
  "timestamp": "2024-01-01 12:00:00",
  "ip": "192.168.1.100",
  "url": "http://example.com/page",
  "method": "GET",
  "user_agent": "Mozilla/5.0...",
  "payload": "...",
  "action": "ALLOWED" veya "BLOCKED"
}
```

#### 1.3 `blocker.py` - IP Engelleme Motoru
**İşlevi:**
- `blocked_ips.json` dosyasını okur
- Gelen IP adreslerini kara listede kontrol eder
- Liste ve sözlük formatlarını destekler

**Akıllı Özellik:**
- Hem `["ip1", "ip2"]` formatını
- Hem de `{"blocked_ips": ["ip1", "ip2"]}` formatını destekler
- Hata durumunda sistem çökmez, sadece loglar

---

### 2. **AI Agent Modülü** (`ai_agent/`)

#### 2.1 `analyzer.py` - Ana Analiz Motoru
**İşlevi:**
- Log girdilerini 3 katmanlı analiz sisteminden geçirir
- Google Gemini AI ile tehdit analizi yapar
- RAG hafızasını kullanır
- Whitelist kontrolü yapar

**Analiz Hiyerarşisi (3 Katmanlı Sistem):**

**Katman 0: Whitelist Kontrolü**
- Güvenli IP'ler ve path'ler kontrol edilir
- Eşleşme varsa direkt geçirilir (AI çağrılmaz)
- Performans optimizasyonu sağlar

**Katman 1: RAG Hafıza Kontrolü**
- `attack_signatures.json` dosyasındaki regex desenleri taranır
- Eşleşme bulunursa AI'ya sormadan direkt sonuç döner
- Hızlı ve maliyet-etkin çözüm

**Katman 2: AI Analizi (Gemini)**
- Bilinmeyen loglar için Google Gemini AI'ya sorulur
- JSON formatında yapılandırılmış cevap alınır
- Yeni saldırı tespit edilirse otomatik öğrenme modülüne gönderilir

**Çıktı Formatı:**
```json
{
  "attack_detected": true/false,
  "attack_type": "SQL Injection",
  "confidence_score": 0.95,
  "suggested_action": "block_ip",
  "explanation": "Açıklama metni"
}
```

**Hata Yönetimi:**
- API kota hatalarını (429) yakalar
- 3 deneme hakkı ile retry mekanizması
- Her denemede 20 saniye bekleme

#### 2.2 `decision_engine.py` - Karar Mekanizması ve İnfaz Memuru
**İşlevi:**
- `traffic.log` dosyasını gerçek zamanlı izler
- Akıllı ön filtreleme yapar
- AI analiz sonuçlarına göre aksiyon alır
- Saldırgan IP'leri kara listeye ekler

**Akıllı Filtreleme (Smart Filtering):**
```python
pre_filter() fonksiyonu:
- Şüpheli karakterler: <, >, ', --, script, union, select
- HTTP 200 (Başarılı) istekleri direkt geçirilir
- Hata kodları (404, 500, 403) AI'ya gönderilir
```

**İş Akışı:**
1. Log dosyası sürekli izlenir (tail -f benzeri)
2. Her yeni satır için ön filtreleme yapılır
3. Şüpheli istekler AI'ya gönderilir
4. Saldırı tespit edilirse IP engellenir
5. Sonuçlar konsola yazdırılır

#### 2.3 `llm_client.py` - Gemini AI İstemcisi
**İşlevi:**
- Google Gemini API bağlantısını yönetir
- API anahtarını `.env` dosyasından okur
- Test amaçlı basit prompt gönderir

#### 2.4 `daily_report.py` - Günlük Rapor Üretici
**İşlevi:**
- Günlük log dosyasını analiz eder
- Saldırı türlerini ve kaynak ülkeleri sayar
- Gemini AI ile executive summary oluşturur
- `daily_executive_summary.txt` dosyasına kaydeder

**Analiz Metrikleri:**
- Toplam engellenen saldırı sayısı
- En yaygın saldırı türü
- En yaygın kaynak ülke

---

### 3. **RAG Memory Modülü** (`rag_memory/`)

#### 3.1 `retriever.py` - Bilgi Tabanı Erişimi
**İşlevi:**
- `attack_signatures.json` dosyasını yükler
- Regex desenleri ile log satırlarını tarar
- Eşleşen saldırıları döndürür

**Özellikler:**
- Case-insensitive arama (büyük/küçük harf duyarsız)
- Regex hata yönetimi
- Hızlı pattern matching

**Veri Yapısı:**
```json
{
  "id": "A001",
  "name": "SQL Injection",
  "regex_patterns": ["(?i)(\\bunion\\s+select\\b)"],
  "risk_level": "CRITICAL",
  "rule_template": {"action": "block_ip"}
}
```

#### 3.2 `learner.py` - Otomatik Öğrenme Modülü
**İşlevi:**
- AI'ın tespit ettiği yeni saldırıları öğrenir
- Saldırı desenlerini regex'e çevirir
- `attack_signatures.json` dosyasına ekler
- Mükerrer kayıtları önler

**Öğrenme Süreci:**
1. AI yeni saldırı tespit eder
2. Log pattern'i regex'e çevrilir (`re.escape()`)
3. Mükerrer kontrolü yapılır
4. Yeni ID üretilir (A001, A002, ...)
5. Veritabanına kaydedilir

**Güvenlik:**
- Regex injection önleme (`re.escape()`)
- Güvenli dosya yazma
- Hata yönetimi

#### 3.3 `whitelist_manager.py` - Beyaz Liste Yöneticisi
**İşlevi:**
- Güvenli IP'leri ve path'leri yönetir
- Log kontrolünde whitelist kontrolü yapar
- JSON tabanlı veri saklama

**Özellikler:**
- IP ekleme/çıkarma
- Path ekleme/çıkarma
- Otomatik dosya oluşturma

**Veri Yapısı:**
```json
{
  "allowed_ips": ["127.0.0.1", "192.168.1.1"],
  "allowed_paths": ["/dashboard", "/login"],
  "trusted_users": ["admin"]
}
```

---

### 4. **Dashboard Modülü** (`dashboard.py`)

**İşlevi:**
- Streamlit tabanlı görsel izleme paneli
- Gerçek zamanlı sistem durumu
- Canlı log akışı
- Engellenen IP listesi
- Sistem kaynak kullanımı (CPU, RAM)

**Özellikler:**
- Otomatik yenileme (2 saniyede bir)
- Galaktik tema (mor-siyah gradient)
- Renk kodlu log gösterimi:
  - 🔴 Kırmızı: Tehlikeli saldırılar
  - 🟢 Yeşil: Güvenli trafik
  - ⚪ Gri: Normal loglar
- Sistem sıfırlama butonu

**Metrikler:**
- Toplam analiz sayısı
- Engellenen tehdit sayısı
- CPU kullanımı
- RAM kullanımı

---

### 5. **Yardımcı Modüller**

#### 5.1 `start_system.py` - Sistem Başlatıcı
**İşlevi:**
- WAF sunucusunu arka planda başlatır
- AI karar motorunu arka planda başlatır
- Tüm modülleri koordine eder

#### 5.2 `init_db.py` - Veritabanı Başlatıcı
**İşlevi:**
- Gerekli klasörleri oluşturur (`data/`, `logs/`)
- Varsayılan JSON dosyalarını oluşturur
- İlk kurulum için hazırlık yapar

---

## 🔄 Sistem İş Akışı (Data Flow)

### Senaryo 1: Normal İstek
```
1. Kullanıcı → HTTP İsteği → Flask Server (server.py)
2. Middleware → İsteği Parse Et → Log'a Yaz
3. Blocker → IP Kontrolü → Whitelist'te mi?
4. Decision Engine → Log'u Oku → Pre-filter → Temiz
5. Sonuç: İstek Geçirildi ✅
```

### Senaryo 2: Saldırı Tespiti (Bilinmeyen)
```
1. Kullanıcı → Saldırı İsteği → Flask Server
2. Middleware → Parse → Log'a Yaz
3. Decision Engine → Log'u Oku → Pre-filter → Şüpheli!
4. Analyzer → Whitelist Kontrolü → Yok
5. Analyzer → RAG Kontrolü → Eşleşme Yok
6. Analyzer → Gemini AI'ya Sor → Saldırı Tespit Edildi!
7. Learner → Yeni Saldırıyı Öğren → attack_signatures.json'a Ekle
8. Decision Engine → IP'yi Engelle → blocked_ips.json'a Ekle
9. Blocker → Gelecek İstekleri Engelle
10. Sonuç: Saldırı Engellendi 🛡️
```

### Senaryo 3: Saldırı Tespiti (Bilinen)
```
1. Kullanıcı → Saldırı İsteği → Flask Server
2. Middleware → Parse → Log'a Yaz
3. Decision Engine → Log'u Oku → Pre-filter → Şüpheli!
4. Analyzer → Whitelist Kontrolü → Yok
5. Analyzer → RAG Kontrolü → Eşleşme Bulundu! (Hızlı)
6. Decision Engine → IP'yi Engelle → blocked_ips.json'a Ekle
7. Sonuç: Saldırı Engellendi (AI çağrılmadı, hızlı!) ⚡
```

---

## 🛠️ Kullanılan Teknolojiler

### Backend
- **Python 3.x**: Ana programlama dili
- **Flask**: Web framework (HTTP sunucusu)
- **Google Gemini AI**: Yapay zeka analiz motoru
- **Streamlit**: Dashboard framework

### Veri Yönetimi
- **JSON**: Hafıza ve konfigürasyon dosyaları
- **Text Logs**: Trafik kayıtları (`traffic.log`)

### Kütüphaneler
- `google-generativeai`: Gemini API entegrasyonu
- `python-dotenv`: Ortam değişkenleri yönetimi
- `requests`: HTTP istekleri (test için)
- `psutil`: Sistem kaynak izleme
- `pandas`: Veri analizi (dashboard)

---

## 📊 Veri Yapıları

### 1. `traffic.log` - Trafik Kayıtları
Her satır bir JSON objesi:
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

### 2. `blocked_ips.json` - Engellenen IP'ler
```json
["192.168.1.100", "10.0.0.50", "172.16.0.1"]
```

### 3. `attack_signatures.json` - Saldırı İmzaları
```json
[
  {
    "id": "A001",
    "name": "SQL Injection",
    "regex_patterns": ["(?i)(\\bunion\\s+select\\b)"],
    "risk_level": "CRITICAL",
    "rule_template": {"action": "block_ip"}
  }
]
```

### 4. `whitelist.json` - Güvenli Liste
```json
{
  "allowed_ips": ["127.0.0.1"],
  "allowed_paths": ["/dashboard"],
  "trusted_users": ["admin"]
}
```

---

## 🎯 Öne Çıkan Özellikler

### 1. **3 Katmanlı Analiz Sistemi**
- **Katman 0**: Whitelist (En Hızlı)
- **Katman 1**: RAG Hafıza (Hızlı)
- **Katman 2**: AI Analizi (Yavaş ama Kapsamlı)

### 2. **Akıllı Ön Filtreleme**
- Gereksiz AI çağrılarını önler
- Maliyet ve performans optimizasyonu
- Basit pattern matching ile hızlı eleme

### 3. **Otomatik Öğrenme**
- Yeni saldırıları otomatik öğrenir
- Regex pattern'leri otomatik oluşturur
- Mükerrer kayıtları önler

### 4. **Hata Toleransı**
- API kota hatalarını yönetir
- Retry mekanizması
- Graceful degradation (hata olsa bile çalışır)

### 5. **Gerçek Zamanlı İzleme**
- Log dosyası tail işlemi
- Canlı dashboard
- Anlık bildirimler

---

## 🚀 Sistem Başlatma

### Adım 1: Kurulum
```bash
python init_db.py  # Veritabanı ve klasörleri oluştur
```

### Adım 2: Ortam Değişkenleri
`.env` dosyası oluştur:
```
GEMINI_API_KEY=your_api_key_here
```

### Adım 3: Sistem Başlatma
```bash
python start_system.py
```

Bu komut:
- WAF sunucusunu başlatır (Port 5000)
- AI karar motorunu başlatır
- Tüm modülleri aktif eder

### Adım 4: Dashboard
```bash
streamlit run dashboard.py
```

---

## 📈 Performans Optimizasyonları

1. **Ön Filtreleme**: %80-90 gereksiz AI çağrısını önler
2. **RAG Hafıza**: Bilinen saldırılar için AI çağrılmaz
3. **Whitelist**: Güvenli trafik direkt geçirilir
4. **Regex Caching**: Pattern'ler bir kez compile edilir
5. **Lazy Loading**: Modüller sadece gerektiğinde yüklenir

---

## 🔒 Güvenlik Özellikleri

1. **IP Engelleme**: Saldırgan IP'ler otomatik engellenir
2. **Regex Injection Koruması**: `re.escape()` kullanımı
3. **API Key Güvenliği**: `.env` dosyasında saklanır
4. **Hata Yönetimi**: Sistem çökmesi önlenir
5. **Log Kayıtları**: Tüm aktiviteler kaydedilir

---

## 📝 Test Modülleri

### `tests/attack_scripts/traffic_generator.py`
- Otomatik saldırı trafiği üretir
- %20 saldırı, %80 normal trafik
- Sistem testleri için kullanılır

### `tests/stress_tests/locustfile.py`
- Yük testleri için Locust script'i
- Performans testleri

---

## 🎓 Öğrenme ve Gelişim

Sistem, her yeni saldırı tespitinde:
1. Saldırı desenini öğrenir
2. Regex pattern'i oluşturur
3. Veritabanına kaydeder
4. Gelecekte aynı saldırıyı hızlıca tanır

Bu sayede sistem zamanla daha akıllı hale gelir ve daha az AI çağrısı yapar.

---

## 📊 İstatistikler ve Metrikler

Dashboard'da görüntülenen:
- Toplam analiz sayısı
- Engellenen tehdit sayısı
- CPU kullanımı
- RAM kullanımı
- Son 10 log kaydı
- Engellenen IP listesi

---

## 🔮 Gelecek Geliştirmeler (Öneriler)

1. **Veritabanı Entegrasyonu**: JSON yerine SQL/NoSQL
2. **Machine Learning**: Daha gelişmiş pattern recognition
3. **Distributed System**: Çoklu sunucu desteği
4. **API Gateway**: RESTful API endpoint'leri
5. **Alert System**: Email/SMS bildirimleri
6. **GeoIP Blocking**: Ülke bazlı engelleme
7. **Rate Limiting**: DDoS koruması
8. **SSL/TLS**: HTTPS desteği

---

## 📌 Sonuç

**TRONwall-Agent**, modern yapay zeka teknolojileri ile geleneksel güvenlik yaklaşımlarını birleştiren, otonom çalışan ve sürekli öğrenen bir güvenlik sistemidir. 

**Temel Avantajlar:**
- ✅ Otomatik tehdit tespiti
- ✅ Sürekli öğrenme yeteneği
- ✅ Düşük maliyet (akıllı filtreleme)
- ✅ Gerçek zamanlı izleme
- ✅ Kolay kurulum ve kullanım
- ✅ Genişletilebilir mimari

Sistem, küçük ve orta ölçekli web uygulamaları için ideal bir güvenlik çözümüdür.

---

**Rapor Tarihi:** 2024  
**Versiyon:** 1.0  
**Hazırlayan:** AI Analiz Sistemi

