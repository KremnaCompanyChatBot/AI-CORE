"""
AI İstemci Modülü

Google Gemini API kullanarak persona tabanlı sohbet uygulaması.
"""

import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

from persona import fetch_persona


# Sabitler
DEFAULT_TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 500
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Çıkış komutları
EXIT_COMMANDS = ["exit", "q", "quit"]


class AIClientError(Exception):
    """AI istemci hatalarını temsil eder."""
    pass


def load_api_configuration() -> str:
    """
    Ortam değişkenlerinden API anahtarını yükler ve doğrular.
    
    Dönüş Değeri:
        str: Geçerli API anahtarı
        
    Hatalar:
        AIClientError: API anahtarı eksik veya geçersizse
    """
    load_dotenv()
    
    # Geriye dönük uyumluluk için OPENAI_API_KEY kullanılıyor
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or "dummy" in api_key.lower():
        raise AIClientError(
            "OPENAI_API_KEY eksik veya geçersiz. "
            "Lütfen .env dosyanızı kontrol edin."
        )
    
    return api_key


def initialize_gemini_model(api_key: str) -> genai.GenerativeModel:
    """
    Gemini AI modelini yapılandırır ve başlatır.
    
    Parametreler:
        api_key: Google AI API anahtarı
        
    Dönüş Değeri:
        GenerativeModel: Yapılandırılmış Gemini modeli
    """
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL_NAME)


def load_backend_configuration() -> Dict[str, Optional[str]]:
    """
    Backend panel yapılandırma değerlerini ortam değişkenlerinden yükler.
    
    Dönüş Değeri:
        Dict[str, Optional[str]]: Backend yapılandırma parametreleri
    """
    return {
        "url": os.getenv("BACKEND_PANEL_URL"),
        "token": os.getenv("BACKEND_PANEL_TOKEN"),
        "ably_channel": os.getenv("BACKEND_PANEL_ABLY_CHANNEL"),
        "ably_api_key": os.getenv("BACKEND_PANEL_ABLY_API_KEY")
    }


def load_persona(config: Dict[str, Optional[str]]) -> Optional[Dict[str, Any]]:
    """
    Backend panel'den persona bilgilerini yükler.
    
    Parametreler:
        config: Backend yapılandırma parametreleri
        
    Dönüş Değeri:
        Optional[Dict[str, Any]]: Persona verisi veya None
    """
    # Backend panel URL veya Ably kanalı yoksa persona yükleme
    if not (config["url"] or config["ably_channel"]):
        return None
    
    try:
        persona = fetch_persona(
            config["url"],
            token=config["token"],
            ably_channel=config["ably_channel"],
            ably_api_key=config["ably_api_key"]
        )
        
        persona_name = persona.get("name") or "(isimsiz)"
        print(f"✅ Persona backend'den yüklendi: {persona_name}")
        return persona
        
    except Exception as e:
        print(f"⚠️ Persona backend'den yüklenemedi: {e}")
        return None


def build_persona_prefix(persona: Dict[str, Any]) -> str:
    """
    Persona bilgilerinden prefix string oluşturur.
    
    Parametreler:
        persona: Persona bilgileri
        
    Dönüş Değeri:
        str: Persona prefix string'i
    """
    parts = []
    
    if persona.get("name"):
        parts.append(f"Persona adı: {persona.get('name')}")
    
    if persona.get("tone"):
        parts.append(f"Ton: {persona.get('tone')}")
    
    if persona.get("constraints"):
        parts.append(f"Kısıtlamalar: {persona.get('constraints')}")
    
    return " | ".join(parts) if parts else ""


def create_full_prompt(user_prompt: str, persona: Optional[Dict[str, Any]]) -> str:
    """
    Kullanıcı prompt'una persona bilgilerini ekler.
    
    Parametreler:
        user_prompt: Kullanıcının girdiği prompt
        persona: Persona bilgileri (opsiyonel)
        
    Dönüş Değeri:
        str: Persona bilgileri eklenmiş tam prompt
    """
    if not persona:
        return user_prompt
    
    persona_prefix = build_persona_prefix(persona)
    
    if persona_prefix:
        return f"{persona_prefix}\n\n{user_prompt}"
    
    return user_prompt


def generate_response(
    model: genai.GenerativeModel,
    prompt: str
) -> Optional[str]:
    """
    AI modelinden yanıt oluşturur.
    
    Parametreler:
        model: Gemini AI modeli
        prompt: Gönderilecek prompt
        
    Dönüş Değeri:
        Optional[str]: Model yanıtı veya None
    """
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": DEFAULT_TEMPERATURE,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        }
    )
    
    if response and response.text:
        return response.text.strip()
    
    return None


def display_response(response: Optional[str]) -> None:
    """
    Model yanıtını formatlı şekilde ekrana yazdırır.
    
    Parametreler:
        response: Gösterilecek yanıt
    """
    if not response:
        print("⚠️ Model boş bir yanıt döndürdü.")
        return
    
    print("🤖 Yanıt:")
    print("--------------------------------------------------")
    print(response)
    print("--------------------------------------------------\n")


def run_chat_loop(
    model: genai.GenerativeModel,
    persona: Optional[Dict[str, Any]]
) -> None:
    """
    Ana sohbet döngüsünü çalıştırır.
    
    Parametreler:
        model: Gemini AI modeli
        persona: Persona bilgileri (opsiyonel)
    """
    print("💬 Sohbeti sonlandırmak için 'exit', 'q' veya 'quit' yazın.\n")
    
    while True:
        try:
            user_prompt = input("🧠 Prompt: ").strip()
             
            # Çıkış kontrolü
            if user_prompt.lower() in EXIT_COMMANDS:
                print("👋 Sohbet sonlandırıldı.")
                break
            
            # Boş prompt kontrolü
            if not user_prompt:
                print("⚠️ Lütfen geçerli bir prompt girin.")
                continue
            
            # Tam prompt oluştur (persona ile)
            full_prompt = create_full_prompt(user_prompt, persona)
            
            print("\n⏳ Yanıt oluşturuluyor...\n")
            
            # Yanıt üret ve göster
            response = generate_response(model, full_prompt)
            display_response(response)
            
        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu.")
            break
            
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}\n")


def main() -> None:
    """Ana program giriş noktası."""
    try:
        # API anahtarını yükle ve doğrula
        api_key = load_api_configuration()
        
        # Gemini modelini başlat
        model = initialize_gemini_model(api_key)
        print("✅ Gemini istemcisi başarıyla başlatıldı.")
        
        # Backend yapılandırmasını yükle
        backend_config = load_backend_configuration()
        
        # Persona'yı yükle (varsa)
        persona = load_persona(backend_config)
        
        # Sohbet döngüsünü başlat
        run_chat_loop(model, persona)
        
    except AIClientError as e:
        print(f"🚨 HATA: {e}")
        exit(1)
        
    except Exception as e:
        print(f"🚨 Beklenmeyen Hata: {e}")
        exit(1)


if __name__ == "__main__":
    main()
