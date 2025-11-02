"""
Dinamik Prompt Oluşturma Modülü

Bu modül, persona verilerini kullanarak dinamik sistem prompt'ları oluşturur.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from persona import fetch_persona


# Sabitler
SYSTEM_PROMPT_TEMPLATE = """
SEN BİR YARDIMCI ASİSTANSIN.

### KİMLİK VE ROL ###
Senin adın: {name}
Kullanıcılarla konuşurken kullanman gereken ses tonu: {tone}

### DAVRANIŞ KURALLARI VE KISITLAMALAR ###
Aşağıdaki kurallara MUTLAKA uymalısın:
{constraints}

### GÖREV ###
Bu kimlik ve kurallara bağlı kalarak kullanıcının sorularını yanıtla.
"""


class EnvironmentConfigError(Exception):
    """Ortam yapılandırması eksik veya hatalı olduğunda fırlatılır."""
    pass


class PersonaError(Exception):
    """Persona verisi alınırken veya işlenirken hata oluştuğunda fırlatılır."""
    pass


def load_environment_variables() -> Dict[str, str]:
    """
    .env dosyasından gerekli ortam değişkenlerini yükler.
    
    Dönüş Değeri:
        Dict[str, str]: Ortam değişkenlerini içeren sözlük
        
    Hatalar:
        EnvironmentConfigError: Gerekli değişkenler bulunamadığında
    """
    load_dotenv()
    
    required_vars = {
        "PERSONA_API_URL": os.getenv("PERSONA_API_URL"),
        "PERSONA_API_TOKEN": os.getenv("PERSONA_API_TOKEN"),
        "ABLY_API_KEY": os.getenv("ABLY_API_KEY"),
        "ABLY_CHANNEL": os.getenv("ABLY_CHANNEL")
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        raise EnvironmentConfigError(
            f"Eksik ortam değişkenleri: {', '.join(missing_vars)}\n"
            f"Lütfen .env dosyanızı kontrol edin."
        )
    
    return required_vars


def fetch_persona_data(config: Dict[str, str]) -> Dict[str, Any]:
    """
    API'den persona verilerini çeker.
    
    Parametreler:
        config: Ortam değişkenlerini içeren sözlük
        
    Dönüş Değeri:
        Dict[str, Any]: Persona verilerini içeren sözlük
        
    Hatalar:
        PersonaError: Persona verisi alınamazsa
    """
    print("Persona verisi çekiliyor...")
    
    persona_data = fetch_persona(
        api_url=config["PERSONA_API_URL"],
        token=config["PERSONA_API_TOKEN"],
        ably_api_key=config["ABLY_API_KEY"],
        ably_channel=config["ABLY_CHANNEL"]
    )
    
    if not persona_data:
        raise PersonaError("Persona verisi alınamadı.")
    
    return persona_data


def validate_persona_data(persona_data: Dict[str, Any]) -> None:
    """
    Persona verisinin gerekli alanlarını kontrol eder.
    
    Parametreler:
        persona_data: Kontrol edilecek persona verisi
        
    Hatalar:
        PersonaError: Gerekli alanlar eksikse
    """
    required_fields = ["name", "tone", "constraints"]
    missing_fields = [field for field in required_fields if not persona_data.get(field)]
    
    if missing_fields:
        raise PersonaError(
            f"Persona verisinde eksik alanlar: {', '.join(missing_fields)}"
        )


def create_system_prompt(persona_data: Dict[str, Any]) -> str:
    """
    Persona verilerinden sistem prompt'u oluşturur.
    
    Parametreler:
        persona_data: Persona bilgilerini içeren sözlük
        
    Dönüş Değeri:
        str: Oluşturulan sistem prompt'u
    """
    return SYSTEM_PROMPT_TEMPLATE.format(
        name=persona_data["name"],
        tone=persona_data["tone"],
        constraints=persona_data["constraints"]
    )


def display_system_prompt(system_prompt: str) -> None:
    """
    Oluşturulan sistem prompt'unu formatlı şekilde ekrana yazdırır.
    
    Parametreler:
        system_prompt: Gösterilecek sistem prompt'u
    """
    print("\n=== BAŞARILI: Persona Yüklendi ===")
    print("\n--- OLUŞTURULAN SYSTEM PROMPT ---")
    print(system_prompt)
    print("-----------------------------------")


def build_prompt() -> Optional[str]:
    """
    Ana fonksiyon: Ortam değişkenlerini yükler, persona verisini çeker
    ve sistem prompt'unu oluşturur.
    
    Dönüş Değeri:
        Optional[str]: Oluşturulan sistem prompt'u veya hata durumunda None
    """
    try:
        # Ortam değişkenlerini yükle
        config = load_environment_variables()
        
        # Persona verisini çek
        persona_data = fetch_persona_data(config)
        
        # Persona verisini doğrula
        validate_persona_data(persona_data)
        
        # Sistem prompt'unu oluştur
        system_prompt = create_system_prompt(persona_data)
        
        # Ekrana yazdır
        display_system_prompt(system_prompt)
        
        return system_prompt
        
    except EnvironmentConfigError as e:
        print(f"❌ Konfigürasyon Hatası: {e}")
        return None
        
    except PersonaError as e:
        print(f"❌ Persona Hatası: {e}")
        return None
        
    except Exception as e:
        print(f"❌ Beklenmeyen Hata: {e}")
        return None


if __name__ == "__main__":
    build_prompt()
