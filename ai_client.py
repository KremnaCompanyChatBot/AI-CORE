import os
from openai import OpenAI
from dotenv import load_dotenv
from openai import APIStatusError, APITimeoutError 
from pydantic import BaseModel, Field

class CityInfo(BaseModel):
    """Kullanıcı tarafından verilen şehir hakkında bilgi içerir."""
    
    city_name: str = Field(
        description="Şehrin tam adı."
    )
    population_2024: int = Field(
        description="Şehrin 2024 yılındaki tahmini nüfusu."
    )
    short_summary: str = Field(
        description="Şehirle ilgili 20 kelimeyi geçmeyen kısa ve ilgi çekici bir özet."
    )

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or "dummy" in api_key.lower(): # Anahtarın varlığını ve gerçekliğini kontrol et
    print("🚨 HATA: OPENAI_API_KEY ayarlanmadı veya test anahtarı kullanılıyor. Lütfen .env dosyanızı gerçek API anahtarınızla güncelleyin.")
    exit()

try:
    client = OpenAI(
        api_key=api_key,
        timeout=25.0 
    )

    print("✅ OpenAI İstemcisi Başarıyla Kuruldu.")



    print("\n⏳ AI İsteği Gönderiliyor (JSON Formatında)...")
    
    response = client.chat.completions.create(
        
        model="gpt-3.5-turbo-0125", 
        messages=[
            
            {"role": "system", "content": "Sen, kullanıcıdan gelen istek üzerine sadece JSON formatında, Pydantic şemasına uygun yanıt üreten bir asistansın."},
            
            
            {"role": "user", "content": "New York şehri hakkında bilgi ver."},
        ],
        temperature=0.0, # Yapılandırılmış çıktı istediğimiz için yaratıcılığı (rastgeleliği) sıfıra yakın tutarız.
        max_tokens=500,  # Token limitini JSON'u kapsayacak şekilde ayarlıyoruz.
        
        # KRİTİK AYAR: Modelin JSON nesnesi döndürmesini zorunlu kılıyoruz
        response_format={"type": "json_object"},
    )
    
    ai_yanit_json_string = response.choices[0].message.content
    print("\n🤖 AI Yanıtı (Ham JSON Stringi):")
    print("--------------------------------------------------")
    print(ai_yanit_json_string)
    print("--------------------------------------------------")


    import json
    try:
        data = json.loads(ai_yanit_json_string)
        validated_data = CityInfo(**data)
        
        print("\n✅ Doğrulama Başarılı! (Pydantic ile):")
        print(f"  Şehir Adı (Doğrulanmış): {validated_data.city_name}")
        print(f"  Nüfus (Doğrulanmış, Integer): {validated_data.population_2024}")
        print(f"  Özet (Doğrulanmış): {validated_data.short_summary}")
        
    except Exception as e:
        print(f"\n❌ JSON Doğrulama Hatası: Gelen çıktı beklenen şemaya uymadı. Hata: {e}")


except APITimeoutError:
    print("\n❌ Hata: API isteği zaman aşımına uğradı.")
except APIStatusError as e:
    print(f"\n❌ Hata: API'den bir durum hatası döndü ({e.status_code}).")
except Exception as e:
    print(f"\n❌ Beklenmedik bir hata oluştu: {e}")