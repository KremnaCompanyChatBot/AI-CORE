"""
Persona Modülü

Bu modül, Backend Panel API'den veya Ably kanalından persona bilgilerini çeker.
"""

import os
from typing import Optional, Dict, Any
import requests
import base64
import json
from urllib.parse import quote_plus


# Sabitler
ABLY_REST_BASE_URL = "https://rest.ably.io"
MESSAGE_LIMIT = 1
DEFAULT_TIMEOUT = 5


class PersonaFetchError(Exception):
    """Persona verisi çekilirken oluşan hatalar için özel exception."""
    pass


def _encode_ably_auth(api_key: str) -> str:
    """
    Ably API anahtarını HTTP Basic Auth formatına dönüştürür.
    
    Parametreler:
        api_key: Ably API anahtarı
        
    Dönüş Değeri:
        str: Base64 kodlanmış authentication string
    """
    auth_string = f"{api_key}:"
    return base64.b64encode(auth_string.encode()).decode()


def _fetch_from_ably(
    channel: str,
    api_key: str,
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Ably REST API'den kanal geçmişinden son mesajı çeker.
    
    Parametreler:
        channel: Ably kanal adı
        api_key: Ably API anahtarı
        timeout: İstek zaman aşımı süresi (saniye)
        
    Dönüş Değeri:
        Dict[str, Any]: Ably'den çekilen persona verisi
        
    Hatalar:
        PersonaFetchError: Mesaj bulunamazsa veya API hatası oluşursa
    """
    url = f"{ABLY_REST_BASE_URL}/channels/{quote_plus(channel)}/messages?limit={MESSAGE_LIMIT}"
    
    basic_token = _encode_ably_auth(api_key)
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {basic_token}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        messages = response.json()
        
        if not isinstance(messages, list) or len(messages) == 0:
            raise PersonaFetchError("Ably kanalında persona mesajı bulunamadı")
        
        # İlk mesajın verisini al
        message = messages[0]
        data = message.get("data") if isinstance(message, dict) else None
        
        # Eğer data string ise JSON'a dönüştürmeyi dene
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                # Ham string olarak bırak
                pass
        
        return data
        
    except requests.RequestException as e:
        raise PersonaFetchError(f"Ably API'den veri çekilirken hata: {e}")


def _fetch_from_api(
    api_url: str,
    token: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Backend Panel API'den persona bilgilerini çeker.
    
    Parametreler:
        api_url: Backend API endpoint URL'i
        token: Yetkilendirme token'ı (opsiyonel)
        timeout: İstek zaman aşımı süresi (saniye)
        
    Dönüş Değeri:
        Dict[str, Any]: API'den çekilen persona verisi
        
    Hatalar:
        PersonaFetchError: API hatası oluşursa
    """
    headers = {"Accept": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        raise PersonaFetchError(f"Backend API'den veri çekilirken hata: {e}")


def _extract_persona_fields(data: Any) -> Dict[str, Any]:
    """
    Farklı API formatlarından persona alanlarını çıkarır.
    
    Backend'ler farklı yapılarda veri dönebilir:
    - Doğrudan ana obje içinde: {"name": "...", "tone": "...", "constraints": "..."}
    - persona anahtarı altında: {"persona": {"name": "...", "tone": "...", "constraints": "..."}}
    - attributes veya settings altında: {"attributes": {"name": "...", ...}}
    
    Parametreler:
        data: API'den gelen ham veri
        
    Dönüş Değeri:
        Dict[str, Any]: Çıkarılan persona alanları
        
    Hatalar:
        PersonaFetchError: Veri uygun formatta değilse
    """
    if not isinstance(data, dict):
        raise PersonaFetchError("Persona endpoint'i JSON objesi dönmedi")
    
    # Doğrudan ana objede ara
    name = data.get("name")
    tone = data.get("tone")
    constraints = data.get("constraints")
    
    # 'persona' anahtarı altında ara
    if not (name or tone or constraints) and "persona" in data:
        persona_obj = data.get("persona")
        if isinstance(persona_obj, dict):
            name = name or persona_obj.get("name")
            tone = tone or persona_obj.get("tone")
            constraints = constraints or persona_obj.get("constraints")
    
    # 'attributes' veya 'settings' anahtarları altında ara
    if not (name or tone or constraints):
        for key in ("attributes", "settings"):
            if key in data and isinstance(data[key], dict):
                nested = data[key]
                name = name or nested.get("name")
                tone = tone or nested.get("tone")
                constraints = constraints or nested.get("constraints")
    
    return {
        "name": name,
        "tone": tone,
        "constraints": constraints,
        "raw": data,
    }


def fetch_persona(
    api_url: Optional[str],
    token: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
    ably_channel: Optional[str] = None,
    ably_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Backend Panel API'den veya Ably kanalından persona bilgilerini çeker.
    
    Beklenen dönüş formatı (örnek):
    {
        "name": "Kremna Assistant",
        "tone": "friendly, concise",
        "constraints": "No medical or legal advice; keep messages < 500 chars"
    }
    
    Fonksiyon, farklı backend formatlarını destekler ve persona verilerini 
    'persona', 'attributes' veya 'settings' anahtarları altında arayabilir.
    
    Parametreler:
        api_url: Backend API endpoint URL'i (Ably kullanılmıyorsa zorunlu)
        token: API yetkilendirme token'ı (opsiyonel)
        timeout: HTTP istek zaman aşımı süresi (saniye, varsayılan: 5)
        ably_channel: Ably kanal adı (opsiyonel)
        ably_api_key: Ably API anahtarı (opsiyonel)
        
    Dönüş Değeri:
        Dict[str, Any]: Persona bilgilerini içeren sözlük
            - name: Asistan adı
            - tone: Konuşma tonu
            - constraints: Davranış kısıtlamaları
            - raw: Ham API yanıtı
            
    Hatalar:
        PersonaFetchError: Veri çekilemezse veya geçersiz formatta olursa
        ValueError: Gerekli parametreler eksikse
    """
    # Eğer Ably kanalı sağlanmışsa, Ably'den çek
    if ably_channel and ably_api_key:
        data = _fetch_from_ably(ably_channel, ably_api_key, timeout)
    else:
        # Ably kullanılmıyorsa, API URL gerekli
        if not api_url:
            raise ValueError(
                "api_url parametresi gerekli (Ably kullanılmadığında)"
            )
        data = _fetch_from_api(api_url, token, timeout)
    
    # Farklı backend formatlarından persona alanlarını çıkar
    return _extract_persona_fields(data)
