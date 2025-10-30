import os
from openai import OpenAI
from dotenv import load_dotenv
from openai import APIStatusError, APITimeoutError 

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or "dummy" in api_key.lower(): # Anahtarın varlığını ve gerçekliğini kontrol et
    print("🚨 HATA: OPENAI_API_KEY ayarlanmadı veya test anahtarı kullanılıyor. Lütfen .env dosyanızı gerçek API anahtarınızla güncelleyin.")
    exit()

try:
    client = OpenAI(
        api_key=api_key,
        # Timeout ayarı: İstek 15 saniyede yanıt vermezse zaman aşımına uğrar.
        timeout=15.0 
    )

    print("✅ OpenAI İstemcisi Başarıyla Kuruldu.")


    print("\n⏳ AI İsteği Gönderiliyor...")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": "Sen yardımsever ve kısa cevaplar veren bir asistansın."},
            {"role": "user", "content": "Denizlerdeki en büyük canlı nedir ve neden bu kadar büyümüştür?"}
        ],
        temperature=0.6, 
        max_tokens=100    
    )

    ai_yanit = response.choices[0].message.content
    print("\n🤖 AI Yanıtı:")
    print("--------------------------------------------------")
    print(ai_yanit)
    print("--------------------------------------------------")


except APITimeoutError:
    print("\n❌ Hata: API isteği zaman aşımına uğradı.")
except APIStatusError as e:
    print(f"\n❌ Hata: API'den bir durum hatası döndü ({e.status_code}).")
except Exception as e:
    print(f"\n❌ Beklenmedik bir hata oluştu: {e}")