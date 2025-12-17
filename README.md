# 🤖 AI Chatbot Sistemi

Modern, özelleştirilebilir AI chatbot sistemi - Google Gemini API ile güçlendirilmiş

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-API-orange.svg)](https://ai.google.dev/)

---

## ✨ Özellikler

- 🎯 **Dinamik Agent Konfigürasyonu** - Dashboard entegrasyonu
- 💬 **Akıllı Sohbet Yönetimi** - Bağlam farkındalığı ile chat history
- 🔍 **Otomatik Konu Tespiti** - Fiyat, garanti, ürün bilgisi kategorileri
- 🚫 **Yasaklı Konu Kontrolü** - Prohibited topics filtreleme
- 📊 **Token Takibi** - Maliyet optimizasyonu
- 🌐 **Modern Web Arayüzü** - Test ve demo için hazır UI
- 🔄 **Geriye Dönük Uyumluluk** - Eski persona formatı desteği

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```powershell
# Bağımlılıkları yükle
.\.venv\Scripts\pip install fastapi uvicorn python-dotenv google-generativeai requests
```

### 2. API Anahtarı

`main/.env` dosyasını oluştur:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Sunucuları Başlat

```powershell
# Terminal 1 - Main Sunucu
cd main
..\.venv\Scripts\python.exe main_receiver.py

# Terminal 2 - Port Yönetimi
cd "port-yönetimi"
..\.venv\Scripts\python.exe local_api_server.py
```

### 4. Web Arayüzünü Aç

```powershell
start web-ui\chatbot.html
```

---

## 📸 Ekran Görüntüsü

```
┌─────────────────────────────────────────────────────┐
│  🤖 Premium Müşteri Temsilcisi                      │
│  Size nasıl yardımcı olabilirim?                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────┐               │
│  │ Merhaba! Ben Premium Müşteri     │               │
│  │ Temsilcinizim. Size nasıl        │               │
│  │ yardımcı olabilirim?              │               │
│  └──────────────────────────────────┘               │
│                                                     │
│              ┌──────────────────────────────┐       │
│              │ Fiyatlarınız neden bu kadar  │       │
│              │ yüksek?                      │       │
│              └──────────────────────────────┘       │
│                                                     │
│  ┌──────────────────────────────────┐               │
│  │ Değerli müşterimiz, fiyatlandır- │               │
│  │ mamız kalite standartlarımıza... │               │
│  │                                  │               │
│  │ 📊 Konu: fiyat_itirazi           │               │
│  │ 🔢 Token: 850                    │               │
│  │ ✅ Onaylandı                     │               │
│  └──────────────────────────────────┘               │
│                                                     │
├─────────────────────────────────────────────────────┤
│  [Mesajınızı yazın...]              [Gönder]       │
└─────────────────────────────────────────────────────┘
```

---

## 📡 API Kullanımı

### Agent Konfigürasyonu Kaydet

```bash
POST http://localhost:9000/agent_config
Content-Type: application/json

{
  "agentId": "agent_123",
  "persona_title": "Premium Müşteri Temsilcisi",
  "model_instructions": {
    "tone": "Resmi, Saygılı",
    "rules": ["Cevaplar 4 cümleyi geçmemelidir."],
    "prohibited_topics": ["Rakiplerin fiyatları"]
  }
}
```

### Sohbet Başlat

```bash
POST http://localhost:9000/chat
Content-Type: application/json

{
  "agent_id": "agent_123",
  "session_id": "sess_001",
  "user_message": "Merhaba!",
  "chat_history": []
}
```

**Yanıt:**
```json
{
  "status": "success",
  "reply": "Merhaba! Size nasıl yardımcı olabilirim?",
  "metadata": {
    "topic_detected": "genel",
    "tokens_used": 45,
    "blocked": false
  }
}
```

---

## 🧪 Test

### Otomatik Test
```powershell
.\test_new_format.ps1
```

### Manuel Test
Web arayüzünü kullan:
```powershell
start web-ui\chatbot.html
```

---

## 📁 Proje Yapısı

```
chat-bot/
├── main/                    # Ana sunucu (Port 9000)
│   ├── main_receiver.py    # FastAPI sunucu
│   └── .env                # API anahtarı
├── port-yönetimi/          # Proxy sunucu (Port 8000)
│   └── local_api_server.py
├── web-ui/                 # Web arayüzü
│   └── chatbot.html
├── personas.db             # SQLite veritabanı
└── API_DOCUMENTATION.md    # Detaylı dokümantasyon
```

---

## 📚 Dokümantasyon

- **API Dokümantasyonu**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Web UI Kılavuzu**: [web-ui/README.md](web-ui/README.md)

---

## 🔧 Yapılandırma

### Gemini Model Değiştir

`main/main_receiver.py` dosyasında:
```python
model = genai.GenerativeModel("models/gemini-2.5-flash")
```

Mevcut modelleri listele:
```powershell
.\.venv\Scripts\python.exe .\list_models.py
```

---

## 🎯 Kullanım Senaryoları

### 1. Dashboard Entegrasyonu
Dashboard ekibi agent konfigürasyonlarını kaydeder.

### 2. Chat Core Entegrasyonu
Chat Core ekibi kullanıcı mesajlarını gönderir, AI yanıtları alır.

### 3. Standalone Kullanım
Web arayüzü ile direkt test ve demo.

---

## 🐛 Sorun Giderme

### API Anahtarı Hatası
```
GEMINI_API_KEY .env'de yok
```
**Çözüm**: `main/.env` dosyasına API anahtarını ekle.

### Port Kullanımda
```
Address already in use
```
**Çözüm**: Eski process'i kapat veya farklı port kullan.

Daha fazla bilgi: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 🔐 Güvenlik

- ✅ API anahtarını `.env` dosyasında sakla
- ✅ `.env` dosyasını `.gitignore`'a ekle
- ✅ Production'da CORS ayarlarını güncelle
- ✅ HTTPS kullan

---

## 📊 Performans

### Gemini API Limitleri (Free Tier)
- Requests/minute: 15
- Requests/day: 1,500
- Tokens/minute: 1,000,000

Token kullanımını `metadata.tokens_used` ile takip et.

---

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing`)
5. Pull Request açın

---

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

---

## 📞 İletişim

Sorularınız için dokümantasyona bakın:
- [API Dokümantasyonu](API_DOCUMENTATION.md)
- [Web UI Kılavuzu](web-ui/README.md)

---

**Geliştirici**: AI Chatbot Team  
**Versiyon**: 1.0.0  
**Son Güncelleme**: 2025-12-17

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
