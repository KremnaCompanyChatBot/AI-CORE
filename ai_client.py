import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
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

if not api_key or "dummy" in api_key.lower():
    print("🚨 HATA: API anahtarı ayarlanmadı veya test anahtarı kullanılıyor. Lütfen .env dosyanızı gerçek API anahtarınızla güncelleyin.")
    exit()

try:
    
    genai.configure(api_key=api_key)

    
    model = genai.GenerativeModel('gemini-2.5-flash')

    print("✅ Gemini İstemcisi Başarıyla Kuruldu.")

    print("\n⏳ AI İsteği Gönderiliyor (JSON Formatında)...")

    # Prompt'u JSON formatında yanıt vermesi için hazırlıyoruz
    prompt = """New York şehri hakkında bilgi ver ve yanıtı şu JSON formatında ver:
{
    "city_name": "şehir adı",
    "population_2024": nüfus,
    "short_summary": "kısa özet"
}"""

    # API çağrısı
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.0,
            max_output_tokens=500,
        )
    )

    # Yanıt kontrolü
    if not response.candidates or not response.candidates[0].content.parts:
        print(f"\n⚠️  API yanıt vermedi. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'Bilinmiyor'}")
        exit()

    ai_yanit_json_string = response.text
    print("\n🤖 AI Yanıtı (Ham JSON Stringi):")
    print("--------------------------------------------------")
    print(ai_yanit_json_string)
    print("--------------------------------------------------")

    # JSON parsing ve Pydantic doğrulama
    try:
        # Yanıt bazen markdown kod bloğu içinde gelebilir, temizleyelim
        clean_json = ai_yanit_json_string.strip()
        if clean_json.startswith("```"):
            # Markdown kod bloğunu temizle
            clean_json = clean_json.split("```")[1]
            if clean_json.startswith("json"):
                clean_json = clean_json[4:]
            clean_json = clean_json.strip()

        data = json.loads(clean_json)
        validated_data = CityInfo(**data)

        print("\n✅ Doğrulama Başarılı! (Pydantic ile):")
        print(f"  Şehir Adı (Doğrulanmış): {validated_data.city_name}")
        print(f"  Nüfus (Doğrulanmış, Integer): {validated_data.population_2024}")
        print(f"  Özet (Doğrulanmış): {validated_data.short_summary}")

    except Exception as e:
        print(f"\n❌ JSON Doğrulama Hatası: Gelen çıktı beklenen şemaya uymadı. Hata: {e}")

except Exception as e:
    print(f"\n❌ Beklenmedik bir hata oluştu: {e}")