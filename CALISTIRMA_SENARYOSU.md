# TRONwall-Agent: Detaylı Çalıştırma Senaryosu

Bu doküman, TRONwall-Agent sistemini sunum yaparken kullanabileceğiniz adım adım çalıştırma senaryosunu içerir. Senaryo, tüm modüllerin ve özelliklerin çalıştığını göstermek için tasarlanmıştır.

## Senaryo Özeti

Bu senaryoda sırasıyla şunları göstereceğiz:
1. Sistem kurulumu ve başlatma
2. Normal trafik simülasyonu
3. Saldırı tespiti ve engelleme
4. Otomatik öğrenme mekanizması
5. Dashboard izleme
6. RAG hafıza sistemi
7. Whitelist özelliği
8. Günlük rapor üretimi

---

## ÖN HAZIRLIK (Sunum Öncesi)

### 1. Sistem Hazırlığı

Terminal pencerelerini hazırlayın (en az 3 terminal gerekli):

```
Terminal 1: WAF Sunucusu ve AI Motoru
Terminal 2: Dashboard
Terminal 3: Test/Saldırı Simülasyonu (Opsiyonel)
```

### 2. Dosya Kontrolü

Aşağıdaki dosyaların mevcut olduğundan emin olun:

```bash
# Proje kök dizininde kontrol edin
ls -la

# Olması gerekenler:
# - .env (API anahtarı ile)
# - traffic.log
# - rag_memory/data/attack_signatures.json
# - rag_memory/data/whitelist.json
# - ai_agent/blocked_ips.json
```

### 3. Ön Kontrol Komutu

```bash
python init_db.py
```

Bu komut tüm dosyaların yerinde olduğundan emin olur.

---

## SUNUM SENARYOSU

### BÖLÜM 1: Sistem Başlatma ve Temel Yapı

**Amaç:** Sistemin temel bileşenlerinin çalıştığını göstermek

#### Adım 1.1: Sistem Başlatma

**Terminal 1'de çalıştırın:**

```bash
python start_system.py
```

**Ne Gösteriyoruz:**
- Sistemin otomatik başlatma mekanizması
- WAF sunucusunun başlaması
- AI karar motorunun aktif olması
- Log izleme sisteminin devreye girmesi

**Ekran Çıktısı Örneği:**
```
 TRONwall Sistemi Başlatılıyor...
Sistemler Aktif. Analiz terminalden izlenebilir.
--- TRONwall Karar Mekanizması & İnfaz Memuru Başlatıldı ---
Smart Filtering (Akıllı Filtreleme) Aktif.
```

**Açıklama Yapılacaklar:**
- "Sistem iki ana bileşenden oluşuyor: WAF sunucusu ve AI karar motoru"
- "Akıllı filtreleme sistemi aktif, gereksiz AI çağrılarını önlüyor"

#### Adım 1.2: Sistem Durumu Kontrolü

Yeni bir tarayıcı sekmesinde açın:

```
http://localhost:5000
```

**Beklenen Çıktı:**
```
TRONwall Active - System Secure
```

**Açıklama:**
- "WAF sunucusu başarıyla çalışıyor ve istekleri karşılıyor"
- "Henüz saldırı tespit edilmediği için sistem güvenli durumda"

---

### BÖLÜM 2: Normal Trafik ve Whitelist Özelliği

**Amaç:** Normal trafiğin nasıl işlendiğini ve whitelist özelliğini göstermek

#### Adım 2.1: Normal HTTP İsteği

**Terminal 3'te (veya yeni bir terminal):**

```bash
curl http://localhost:5000/
```

veya tarayıcıdan tekrar `http://localhost:5000` adresini açın.

**Terminal 1'de Gözlemlenecek:**
```
[ATLANDI] Temiz İstek: 127.0.0.1
```

**Açıklama:**
- "Akıllı filtreleme sistemi bu isteği temiz olarak algıladı"
- "AI'ya gerek kalmadan direkt geçirildi - performans optimizasyonu"

#### Adım 2.2: Whitelist Özelliği

**Önce whitelist dosyasını kontrol edin:**

```bash
cat rag_memory/data/whitelist.json
```

**Terminal 3'te whitelist'teki bir path'e istek atın:**

```bash
curl http://localhost:5000/dashboard
```

**Açıklama:**
- "Whitelist sistemi aktif, güvenli path'ler direkt geçiriliyor"
- "Bu özellik, false positive'leri azaltıyor"

---

### BÖLÜM 3: Saldırı Tespiti - Bilinen Saldırılar (RAG Hafıza)

**Amaç:** RAG hafıza sisteminin çalıştığını göstermek

#### Adım 3.1: SQL Injection Saldırısı

**Terminal 3'te çalıştırın:**

```bash
curl "http://localhost:5000/?id=1' OR '1'='1"
```

**Terminal 1'de Gözlemlenecek:**
```
b[AI Analiz Ediyor...] 127.0.0.1
HAFIZADA BULUNDU! (Gemini Atlandı)
[İNFAZ] 127.0.0.1 kara listeye alındı.
```

**Açıklama:**
- "Sistem SQL Injection saldırısını tespit etti"
- "ÖNEMLİ: RAG hafıza sistemi devreye girdi, AI'ya sormadan direkt sonuç döndü"
- "Bu sayede hem hızlı yanıt hem de API maliyeti tasarrufu sağlandı"

#### Adım 3.2: Engellenmiş IP Kontrolü

**Tarayıcıdan tekrar erişmeyi deneyin:**

```
http://localhost:5000
```

**Beklenen Çıktı:**
```
ERİŞİM ENGELLENDİ
```

**Açıklama:**
- "IP otomatik olarak engellendi"
- "Artık bu IP'den gelen tüm istekler engelleniyor"

**Engellenen IP'leri kontrol edin:**

```bash
cat ai_agent/blocked_ips.json
```

---

### BÖLÜM 4: Otomatik Öğrenme Sistemi

**Amaç:** Sistemin yeni saldırıları nasıl öğrendiğini göstermek

#### Adım 4.1: Engellenen IP'yi Temizleme

**Önce engellenen IP'yi temizleyin (gösterim için):**

```bash
echo "[]" > ai_agent/blocked_ips.json
```

veya dosyayı düzenleyerek IP'yi çıkarın.

#### Adım 4.2: Bilinmeyen Saldırı Tespiti

**Terminal 3'te yeni bir saldırı gönderin (sistemde olmayan bir pattern):**

```bash
curl "http://localhost:5000/?test=<svg/onload=alert(1)>"
```

**Terminal 1'de Gözlemlenecek:**
```
[AI Analiz Ediyor...] 127.0.0.1
Bilinmiyor. Gemini'ye soruluyor...
YENİ SALDIRI TESPİT EDİLDİ! Hafızaya kaydediliyor...
ÖĞRENİLDİ: XSS (ID: A0XX) hafızaya kazındı!
```

**Açıklama:**
- "Sistem bilinmeyen bir saldırı tespit etti"
- "AI analizi yapıldı ve sonuç alındı"
- "OTOMATIK ÖĞRENME: Sistem bu saldırıyı hafızaya kaydetti"
- "Bir sonraki sefer aynı saldırı geldiğinde AI'ya sormadan direkt engellenecek"

#### Adım 4.3: Öğrenilen Saldırıyı Kontrol Etme

**Yeni öğrenilen saldırıyı kontrol edin:**

```bash
cat rag_memory/data/attack_signatures.json | tail -30
```

**Açıklama:**
- "Görüldüğü gibi yeni saldırı attack_signatures.json dosyasına eklendi"
- "Regex pattern otomatik oluşturuldu"

#### Adım 4.4: Öğrenilen Saldırının Tekrar Test Edilmesi

**Aynı saldırıyı tekrar gönderin:**

```bash
curl "http://localhost:5000/?test=<svg/onload=alert(1)>"
```

**Terminal 1'de Gözlemlenecek:**
```
HAFIZADA BULUNDU! (Gemini Atlandı)
```

**Açıklama:**
- "Bu sefer AI'ya sorulmadı!"
- "RAG hafıza sistemi direkt sonuç döndürdü"
- "Sistem öğrendi ve artık daha hızlı tepki veriyor"

---

### BÖLÜM 5: Dashboard İzleme

**Amaç:** Görsel izleme panelinin özelliklerini göstermek

#### Adım 5.1: Dashboard'u Başlatma

**Terminal 2'de çalıştırın:**

```bash
streamlit run dashboard.py
```

**Tarayıcıda açın:**

```
http://localhost:8501
```

**Açıklama:**
- "Dashboard başlatıldı, gerçek zamanlı izleme paneli aktif"

#### Adım 5.2: Dashboard Özelliklerini Gösterme

**Dashboard'da gösterilecekler:**

1. **Sistem Sağlığı (Sidebar)**
   - CPU kullanımı
   - RAM kullanımı
   - "Sistem kaynaklarını gerçek zamanlı izliyoruz"

2. **Engellenen Tehditler Tablosu**
   - Engellenen IP listesi
   - "Hangi IP'lerin engellendiğini görüyoruz"

3. **Operasyonel İstatistikler**
   - Toplam analiz sayısı
   - Engellenen tehdit sayısı
   - "Sistem metrikleri anlık güncelleniyor"

4. **Canlı Log Akışı**
   - Renkli log gösterimi
   - "Tüm aktiviteler canlı olarak izleniyor"
   - Kırmızı: Tehlikeli saldırılar
   - Yeşil: Güvenli trafik

#### Adım 5.3: Gerçek Zamanlı Güncelleme

**Terminal 3'te yeni bir saldırı gönderin:**

```bash
curl "http://localhost:5000/?id=1 UNION SELECT * FROM users"
```

**Dashboard'da gözlemlenecekler:**
- Log akışına yeni kayıt eklenecek
- Engellenen IP listesi güncellenecek
- İstatistikler anında değişecek

**Açıklama:**
- "Dashboard 2 saniyede bir otomatik yenileniyor"
- "Tüm değişiklikler anında yansıyor"

---

### BÖLÜM 6: Çoklu Saldırı Türleri

**Amaç:** Sistemin farklı saldırı türlerini nasıl tespit ettiğini göstermek

#### Adım 6.1: XSS Saldırısı

**Terminal 3'te:**

```bash
curl "http://localhost:5000/?name=<script>alert('XSS')</script>"
```

**Terminal 1'de Gözlemlenecek:**
```
HAFIZADA BULUNDU! (Gemini Atlandı)
[İNFAZ] 127.0.0.1 kara listeye alındı.
```

#### Adım 6.2: Path Traversal Saldırısı

**Yeni bir IP simülasyonu için (farklı bir terminal):**

```bash
curl "http://localhost:5000/download?file=../../../etc/passwd"
```

**Açıklama:**
- "Farklı saldırı türlerini tespit edebiliyor"
- "Her saldırı türü için özel pattern matching var"

#### Adım 6.3: Command Injection

```bash
curl "http://localhost:5000/?cmd=; ls -la"
```

**Açıklama:**
- "Command injection saldırıları da tespit ediliyor"
- "Sistem çok çeşitli saldırı türlerine karşı koruma sağlıyor"

---

### BÖLÜM 7: Flask Dashboard

**Amaç:** Flask tabanlı dashboard'un özelliklerini göstermek

#### Adım 7.1: Flask Dashboard Erişimi

**Tarayıcıda:**

```
http://localhost:5000/dashboard
```

**Gösterilecekler:**
- Son 10 log kaydı tablosu
- Engellenen IP listesi tablosu
- Otomatik yenileme (5 saniyede bir)

**Açıklama:**
- "Flask tabanlı basit bir dashboard da mevcut"
- "Streamlit'e alternatif olarak kullanılabilir"

---

### BÖLÜM 8: Günlük Rapor Üretimi

**Amaç:** Günlük rapor sisteminin çalıştığını göstermek

#### Adım 8.1: Günlük Rapor Oluşturma

**Yeni bir terminalde:**

```bash
cd ai_agent
python daily_report.py
```

**Beklenen Çıktı:**
```
 Günlük Executive Summary oluşturuldu:
----------------------------------------
[Gemini AI tarafından oluşturulan özet]
----------------------------------------
```

**Oluşturulan raporu gösterin:**

```bash
cat daily_executive_summary.txt
```

**Açıklama:**
- "Sistem günlük güvenlik raporu oluşturabiliyor"
- "AI destekli executive summary üretiliyor"
- "Yönetim için özet bilgi sağlanıyor"

---

### BÖLÜM 9: Performans ve Optimizasyon Gösterimi

**Amaç:** Sistem optimizasyonlarının etkisini göstermek

#### Adım 9.1: Trafik Log Analizi

**Log dosyasını kontrol edin:**

```bash
wc -l traffic.log
```

**Son birkaç kaydı gösterin:**

```bash
tail -20 traffic.log
```

**Açıklama:**
- "Tüm aktiviteler loglanıyor"
- "Log analizi için veri toplanıyor"

#### Adım 9.2: Ön Filtreleme İstatistikleri

**Terminal 1'deki çıktıları analiz edin:**

- Kaç istek "[ATLANDI]" olarak işaretlendi?
- Kaç istek AI'ya gönderildi?

**Açıklama:**
- "Akıllı filtreleme sayesinde %80-90 daha az AI çağrısı yapılıyor"
- "Performans optimizasyonu sağlanıyor"

#### Adım 9.3: RAG Hafıza Performansı

**attack_signatures.json dosyasındaki pattern sayısını gösterin:**

```bash
cat rag_memory/data/attack_signatures.json | grep -c '"id"'
```

**Açıklama:**
- "Sistemde X adet saldırı imzası var"
- "Bu imzalar RAG hafızasında tutuluyor"
- "Bilinen saldırılar için 0ms yanıt süresi"

---

### BÖLÜM 10: Sistem Özeti ve Kapanış

**Amaç:** Tüm özellikleri özetlemek

#### Adım 10.1: Sistem Bileşenlerinin Özeti

**Gösterilen özellikler:**

1. **WAF Core Modülleri**
   - Flask sunucusu çalışıyor
   - IP engelleme aktif
   - Middleware istekleri işliyor

2. **AI Agent Modülleri**
   - AI analizi çalışıyor
   - Otomatik öğrenme aktif
   - Karar mekanizması çalışıyor

3. **RAG Memory Sistemi**
   - Hafıza sistemi aktif
   - Hızlı pattern matching çalışıyor
   - Otomatik öğrenme ile gelişiyor

4. **Dashboard Sistemi**
   - Streamlit dashboard çalışıyor
   - Flask dashboard alternatifi mevcut
   - Gerçek zamanlı izleme aktif

5. **Güvenlik Özellikleri**
   - Çok katmanlı koruma
   - Otomatik IP engelleme
   - Whitelist/Blacklist yönetimi

#### Adım 10.2: Son İstatistikler

**Dashboard'dan son durumu gösterin:**
- Toplam analiz sayısı
- Engellenen tehdit sayısı
- Sistem kaynak kullanımı

**Açıklama:**
- "Sistem başarıyla çalıştı"
- "Tüm modüller aktif ve çalışıyor"
- "Gerçek zamanlı koruma sağlanıyor"

---

## SORUN GİDERME (Sunum Sırasında)

### Senaryo 1: Port Zaten Kullanılıyor

**Hata:**
```
Address already in use
```

**Çözüm:**
```bash
# Portu kullanan process'i bulun
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Process'i sonlandırın veya farklı port kullanın
```

### Senaryo 2: API Key Hatası

**Hata:**
```
API Key bulunamadı!
```

**Çözüm:**
```bash
# .env dosyasını kontrol edin
cat .env

# API key'i kontrol edin
```

### Senaryo 3: Dashboard Açılmıyor

**Hata:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Çözüm:**
```bash
pip install streamlit
```

### Senaryo 4: Log Dosyası Boş

**Durum:** Terminal'de çıktı görünmüyor

**Çözüm:**
```bash
# Log dosyasını kontrol edin
tail -f traffic.log

# Manuel istek gönderin
curl http://localhost:5000/
```

---

## SUNUM İPUÇLARI

### Zaman Yönetimi

- **Toplam Süre:** 15-20 dakika önerilir
- **Her bölüm:** 2-3 dakika
- **Soru-Cevap:** Son 5 dakika

### Vurgulanması Gerekenler

1. **3 Katmanlı Analiz Sistemi**
   - Whitelist → RAG → AI sırası
   - Performans optimizasyonu

2. **Otomatik Öğrenme**
   - Yeni saldırıların otomatik öğrenilmesi
   - Sistemin sürekli gelişmesi

3. **Gerçek Zamanlı İzleme**
   - Dashboard ile canlı izleme
   - Anlık karar verme

4. **Performans Optimizasyonu**
   - Akıllı filtreleme
   - RAG hafıza ile hızlı yanıt

### Görsel Destek

- **Ekran 1:** Terminal 1 (Sistem çıktıları)
- **Ekran 2:** Dashboard (Görsel panel)
- **Ekran 3:** Kod gösterimi (İsteğe bağlı)

### Soru Beklentileri

**Olası Sorular ve Cevaplar:**

**S:** Production'da kullanılabilir mi?
**C:** Test amaçlı geliştirilmiştir. Production için ek güvenlik önlemleri gerekebilir.

**S:** API maliyeti nedir?
**C:** Akıllı filtreleme ile %80-90 tasarruf sağlanıyor. RAG hafıza ile daha da azalıyor.

**S:** Ölçeklenebilir mi?
**C:** Mevcut sürüm tek sunucu için. Cluster desteği için geliştirme gerekir.

**S:** Veritabanı kullanıyor mu?
**C:** Şu an JSON tabanlı. Büyük ölçek için veritabanı entegrasyonu önerilir.

---

## SONUÇ

Bu senaryo, TRONwall-Agent sisteminin tüm özelliklerini ve modüllerini kapsamlı bir şekilde göstermek için tasarlanmıştır. Senaryoyu takip ederek:

- Sistemin çalışma mantığını gösterebilirsiniz
- Tüm modüllerin aktif olduğunu kanıtlayabilirsiniz
- Otomatik öğrenme sistemini gözlemleyebilirsiniz
- Dashboard özelliklerini tanıtabilirsiniz
- Performans optimizasyonlarını açıklayabilirsiniz

Başarılar!

