# 🚂 Railway Deployment Kılavuzu

## Hızlı Başlangıç

### 1. Railway Hesabı
- [railway.app](https://railway.app/) → GitHub ile giriş yapın

### 2. Proje Oluştur
```bash
# Railway CLI (opsiyonel)
npm i -g @railway/cli
railway login
railway init
railway up
```

**VEYA Web UI ile:**
1. Dashboard → **New Project**
2. **Deploy from GitHub repo** seçin
3. Bu repo'yu seçin
4. Railway otomatik Dockerfile'ı algılar

### 3. Environment Variables
Railway dashboard → **Variables** → Ekle:

```
GEMINI_API_KEY=your_valid_gemini_api_key_here
```

### 4. Domain
Railway otomatik `xxx.up.railway.app` domain verir. 

**Settings** → **Public Networking** → Domain'i kopyalayın.

### 5. Test Et
```
https://YOUR-APP.up.railway.app/
```

---

## 📋 Deployment Checklist

- [x] Dockerfile PORT env variable kullanıyor
- [x] main_receiver.py PORT env variable'dan okuyor
- [x] .railwayignore gereksiz dosyaları hariç tutuyor
- [ ] Railway'e GEMINI_API_KEY eklenmiş
- [ ] Agent config ilk deploy sonrası POST edilecek

---

## 🔧 Railway Environment Variables

| Variable | Açıklama | Zorunlu |
|----------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API anahtarı | ✅ Evet |
| `PORT` | Railway otomatik set eder | ✅ Otomatik |

---

## 🗄️ Veritabanı (SQLite)

⚠️ **Önemli:** Railway ephemeral filesystem kullanır. Container yeniden başlatılınca SQLite DB sıfırlanır.

**Çözümler:**

### Seçenek 1: Agent Config'i Her Deploy'da Kaydet
Deploy sonrası bu komutu çalıştırın:
```bash
curl -X POST https://YOUR-APP.up.railway.app/agent_config \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "agent_8823_xyz",
    "persona_title": "Premium Müşteri Temsilcisi",
    "model_instructions": {
      "tone": "Resmi, Saygılı",
      "rules": ["Kısa cevaplar", "Değer odaklı"],
      "prohibited_topics": ["Rakip fiyatları"]
    },
    "initial_context": {
      "company_slogan": "Kalite Asla Tesadüf Değildir"
    }
  }'
```

### Seçenek 2: Railway Volume (Kalıcı Depolama)
1. Railway Dashboard → **Volumes**
2. **New Volume** → Mount path: `/app/data`
3. `main_receiver.py` → DB_PATH: `/app/data/personas.db`

### Seçenek 3: Railway Postgres (Önerilen - Ücretli)
1. **New** → **Database** → **Postgres**
2. `main_receiver.py`'yi SQLite yerine Postgres kullanacak şekilde düzenle

---

## 🚀 Deploy Sonrası

### Agent Config Kaydı
```powershell
$config = @{
    agentId = "agent_8823_xyz"
    persona_title = "Premium Müşteri Temsilcisi"
    model_instructions = @{
      tone = "Resmi, Saygılı, Çözüm Odaklı"
      rules = @("Kısa cevaplar", "Değer odaklı")
      prohibited_topics = @("Rakip fiyatları")
    }
    initial_context = @{
      company_slogan = "Kalite Asla Tesadüf Değildir"
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "https://YOUR-APP.up.railway.app/agent_config" `
  -ContentType 'application/json; charset=utf-8' -Body $config
```

### Test
```
https://YOUR-APP.up.railway.app/
```

---

## 📊 Logs & Monitoring

Railway Dashboard → **Deployments** → Seçilen deploy → **View Logs**

```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Started server process
INFO:     Application startup complete.
```

---

## 🔄 Auto-Deploy

Railway GitHub ile entegre. Her push otomatik deploy tetikler.

**Disable etmek için:** Settings → **Auto-Deploy** → OFF

---

## 💡 İpuçları

1. **Free Tier:** 500 saat/ay ($5 değerinde) ücretsiz
2. **Custom Domain:** Settings → Add domain
3. **Scaling:** Railway otomatik ölçeklendirir
4. **Logs:** Real-time log streaming
5. **Metrics:** CPU, RAM, Network kullanımı

---

## 🐛 Sorun Giderme

### Port Hatası
```
Error binding to port
```
✅ `main_receiver.py` PORT env'i kullanıyor (düzeltildi)

### API Key Invalid
```
Gemini API hatası: 400 API key not valid
```
✅ Railway Variables → `GEMINI_API_KEY` kontrol et

### Agent Bulunamadı
```
Agent bulunamadı: agent_8823_xyz
```
✅ Deploy sonrası agent config POST et (yukarıdaki komut)

### SQLite DB Sıfırlanıyor
✅ Railway Volume kullan veya Postgres'e geç

---

## 📞 Destek

- Railway Docs: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- API Dokümantasyonu: `API_DOCUMENTATION.md`

---

**Deploy ettikten sonra bu komutu çalıştırmayı unutmayın:**
```bash
curl -X POST https://YOUR-APP.up.railway.app/agent_config -H "Content-Type: application/json" -d @register_agent.json
```
