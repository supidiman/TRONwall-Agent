# RAG Memory Modülü

Bu modül, TRONwall ajanı için "Uzun Süreli Hafıza" görevi görür.

## Neden JSON Yapısı Seçildi?
1. **Hız:** Python ile diskten okuması ve parse etmesi milisaniyeler sürer.
2. **Taşınabilirlik:** Ekstra veritabanı kurulumu (MySQL, PostgreSQL) gerektirmez.
3. **LLM Uyumu:** JSON formatı, AI modelleri (Gemini) tarafından en iyi anlaşılan veri formatıdır.

## Nasıl Çalışır?
Sistem, gelen log içinde `patterns` dizisindeki kelimeleri arar. Eşleşme bulursa, AI'a "Bu log bir SQL Injection olabilir, işte kanıtı" diyerek bağlam (context) sağlar.