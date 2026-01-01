# TRONwall-Agent: Hızlı Özet Rapor

## 🎯 Proje Ne İş Yapar?

**TRONwall-Agent**, web uygulamalarını siber saldırılara karşı koruyan, yapay zeka destekli otomatik bir güvenlik duvarıdır. Sistem:

- ✅ Gelen HTTP isteklerini gerçek zamanlı analiz eder
- ✅ Saldırıları otomatik tespit eder ve engeller
- ✅ Yeni saldırı türlerini öğrenir ve hafızaya kaydeder
- ✅ Saldırgan IP'leri otomatik olarak kara listeye alır
- ✅ Canlı izleme dashboard'u sunar

---

## 🏗️ Ana Modüller ve İşlevleri

### 1. **WAF Core** (Güvenlik Duvarı Çekirdeği)
- **server.py**: Web sunucusu, HTTP isteklerini karşılar
- **middleware.py**: İstekleri işler ve loglar
- **blocker.py**: Engellenen IP'leri kontrol eder

### 2. **AI Agent** (Yapay Zeka Ajanı)
- **analyzer.py**: Log analizi yapar (3 katmanlı sistem)
- **decision_engine.py**: Karar verir ve IP engeller
- **llm_client.py**: Google Gemini AI bağlantısı
- **daily_report.py**: Günlük güvenlik raporu oluşturur

### 3. **RAG Memory** (Hafıza Sistemi)
- **retriever.py**: Geçmiş saldırı verilerini arar
- **learner.py**: Yeni saldırıları öğrenir
- **whitelist_manager.py**: Güvenli IP/Path yönetimi

### 4. **Dashboard** (İzleme Paneli)
- **dashboard.py**: Streamlit tabanlı görsel izleme arayüzü

---

## 🔄 Sistem Nasıl Çalışır?

### Adım 1: İstek Gelir
```
Kullanıcı → HTTP İsteği → Flask Sunucusu
```

### Adım 2: İlk Kontroller
```
IP Engellenmiş mi? → Evet → ❌ 403 Forbidden
IP Engellenmiş mi? → Hayır → Devam
```

### Adım 3: Log Kaydı
```
İstek → Parse Edilir → traffic.log'a Yazılır
```

### Adım 4: Analiz Süreci (3 Katmanlı)

**Katman 0: Whitelist**
- Güvenli IP/Path mi? → Evet → ✅ Geçir

**Katman 1: RAG Hafıza**
- Bilinen saldırı mı? → Evet → ⚡ Hızlı Engelle

**Katman 2: AI Analizi**
- Gemini AI'ya sor → Saldırı var mı?
  - Evet → Engelle + Öğren
  - Hayır → Geçir

### Adım 5: Aksiyon
```
Saldırı Tespit Edildi → IP Engellenir → blocked_ips.json'a Eklenir
```

---

## 📊 Veri Dosyaları

| Dosya | İçerik | Kullanım |
|-------|--------|----------|
| `traffic.log` | Tüm HTTP istekleri | Log kayıtları |
| `blocked_ips.json` | Engellenen IP'ler | IP engelleme |
| `attack_signatures.json` | Saldırı desenleri | Hızlı tespit |
| `whitelist.json` | Güvenli IP/Path'ler | Hızlı geçiş |

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
python init_db.py
```

### 2. API Anahtarı
`.env` dosyası oluştur:
```
GEMINI_API_KEY=your_key_here
```

### 3. Sistem Başlat
```bash
python start_system.py
```

### 4. Dashboard
```bash
streamlit run dashboard.py
```

---

## 🎯 Öne Çıkan Özellikler

1. **3 Katmanlı Analiz**: Whitelist → RAG → AI
2. **Akıllı Filtreleme**: Gereksiz AI çağrılarını önler
3. **Otomatik Öğrenme**: Yeni saldırıları hafızaya kaydeder
4. **Gerçek Zamanlı**: Anlık tespit ve engelleme
5. **Canlı Dashboard**: Görsel izleme ve istatistikler

---

## 📈 Performans

- **Ön Filtreleme**: %80-90 gereksiz AI çağrısını önler
- **RAG Hafıza**: Bilinen saldırılar için 0ms yanıt
- **Whitelist**: Güvenli trafik için anında geçiş

---

## 🔒 Güvenlik Katmanları

1. IP Engelleme (Kara Liste)
2. Ön Filtreleme (Şüpheli Karakterler)
3. Whitelist Kontrolü
4. RAG Hafıza Kontrolü
5. AI Analizi (Gemini)
6. Otomatik Öğrenme

---

## 📝 Tespit Edilen Saldırı Türleri

- ✅ SQL Injection
- ✅ XSS (Cross-Site Scripting)
- ✅ Path Traversal
- ✅ Command Injection
- ✅ Log4Shell
- ✅ Ve daha fazlası (otomatik öğrenme ile)

---

## 🎓 Öğrenme Süreci

```
Yeni Saldırı Tespit Edildi
    ↓
Saldırı Deseni Regex'e Çevrilir
    ↓
attack_signatures.json'a Eklenir
    ↓
Gelecekte Aynı Saldırı Hızlıca Tespit Edilir
```

---

## 📊 Dashboard Metrikleri

- Toplam Analiz Sayısı
- Engellenen Tehdit Sayısı
- CPU Kullanımı
- RAM Kullanımı
- Son 10 Log Kaydı
- Engellenen IP Listesi

---

## 🛠️ Kullanılan Teknolojiler

- **Python 3.x**: Programlama dili
- **Flask**: Web framework
- **Google Gemini AI**: Yapay zeka
- **Streamlit**: Dashboard
- **JSON**: Veri saklama

---

## 💡 Sonuç

**TRONwall-Agent**, modern AI teknolojileri ile geleneksel güvenlik yaklaşımlarını birleştiren, otomatik çalışan ve sürekli öğrenen bir güvenlik sistemidir. Küçük ve orta ölçekli web uygulamaları için ideal bir çözümdür.

---

**Detaylı bilgi için:**
- `PROJE_ANALIZ_RAPORU.md` - Tam detaylı analiz
- `SISTEM_MIMARISI.md` - Mimari şemalar ve diyagramlar

