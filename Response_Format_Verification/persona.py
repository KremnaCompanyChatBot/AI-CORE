
"""
Persona Modülü (Veri Çekme ve Formatlama)

Bu modül, Backend Panel API'den veya Ably kanalından persona bilgilerini çeker.
(LangChain entegrasyonu için veri formatını hazırlar.)
"""


# Gerekli kütüphaneler import ediliyor
import os
from typing import Optional, Dict, Any
import requests  # HTTP istekleri için
import base64    # Ably kimlik doğrulama için
import json      # JSON verisi işlemek için
from urllib.parse import quote_plus  # URL güvenliği için


# --- Sabitler ---
# Ably REST API'nin taban URL'si
ABLY_REST_BASE_URL = "https://rest.ably.io"
# Kanal mesajı çekerken kaç mesaj alınacak (son mesaj için 1)
MESSAGE_LIMIT = 1
# HTTP isteklerinde kullanılacak varsayılan zaman aşımı süresi (saniye)
DEFAULT_TIMEOUT = 20



# Persona verisi çekilirken oluşan hatalar için özel exception
class PersonaFetchError(Exception):
    """Persona verisi çekilirken oluşan hatalar için özel exception."""
    pass



def _encode_ably_auth(api_key: str) -> str:
    """
    Ably API anahtarını HTTP Basic Auth formatına dönüştürür.
    Ably API'ye istek atarken kimlik doğrulama için gerekli olan base64 kodlu stringi üretir.
    """
    # Not: Ably dokümantasyonuna göre Basic auth header genelde
    # base64('<key>:<secret>') formatındadır. Bu projede
    # .env içinde sağlanan `api_key` değişkeninin tam formatı
    # (ör. 'key:secret' mi yoksa yalnızca 'key' mi) değişkenlik
    # gösterebilir. Burada güvenli olması için sonuna ':' eklenip
    # base64'e çevriliyor. Eğer `api_key` zaten 'key:secret' biçimindeyse
    # bu ek ':' beklenmedik bir formata sebep olabilir — uygulamanızın
    # Ably anahtar formatını doğrulamanızı tavsiye ederim.
    # auth_string = f"{api_key}:"
    # # API anahtarı sonuna ':' eklenerek base64'e çevriliyor
    # return base64.b64encode(auth_string.encode()).decode()

    auth_string = api_key.strip()  # ':' EKLEME!
    return base64.b64encode(auth_string.encode()).decode()



def _fetch_from_ably(
    channel: str,
    api_key: str,
    timeout: int = DEFAULT_TIMEOUT
) -> Any:
    """
    Ably REST API'den kanal geçmişinden son mesajı çeker.
    Ably kanalında yayınlanan son persona mesajını almak için kullanılır.
    """
    # Kanal adını URL'de güvenli hale getirmek için quote_plus kullanılır
    url = f"{ABLY_REST_BASE_URL}/channels/{quote_plus(channel)}/messages?limit={MESSAGE_LIMIT}"

    # Kimlik doğrulama için base64 kodlu token hazırlanıyor
    basic_token = _encode_ably_auth(api_key)
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {basic_token}"
    }
    
    try:
        # Ably API'ye GET isteği atılıyor
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Yanıt iki şekilde gelebilir: dict veya doğrudan liste
        response_json = response.json()
        messages = response_json.get("messages") if isinstance(response_json, dict) and "messages" in response_json else response_json

        # Mesaj listesi yoksa hata fırlatılır
        if not isinstance(messages, list) or len(messages) == 0:
            raise PersonaFetchError("Ably kanalında persona mesajı bulunamadı")

        # Son mesaj alınır, 'data' alanı beklenir
        message = messages[0]
        data = message.get("data") if isinstance(message, dict) else None

        # Data string ise JSON'a parse edilmeye çalışılır
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass  # Parse edilemezse ham string olarak bırakılır

        return data
        
    except requests.RequestException as e:
        # HTTP isteklerinde hata olursa özel exception fırlatılır
        raise PersonaFetchError(f"Ably API'den veri çekilirken hata: {e}")



def _fetch_from_api(
    api_url: str,
    token: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Backend Panel API'den persona bilgilerini çeker.
    API URL'sine GET isteği atarak persona verisini JSON formatında döndürür.
    """
    # Header hazırlanıyor, token varsa Bearer olarak ekleniyor
    headers = {"Accept": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        # API'ye GET isteği atılıyor
        response = requests.get(api_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        # Başarılı yanıtın JSON gövdesi döndürülüyor
        return response.json()

    except requests.RequestException as e:
        # Hata durumunda özel exception fırlatılıyor
        raise PersonaFetchError(f"Backend API'den veri çekilirken hata: {e}")



def _extract_persona_fields(data: Any) -> Dict[str, Any]:
    """
    Farklı API formatlarından persona alanlarını çıkarır.
    Gelen JSON objesinden 'name', 'tone', 'constraints' gibi alanları bulup döndürür.
    """
    # Beklenen giriş bir dict (JSON objesi) olmalı. Değilse hata veriyoruz.
    if not isinstance(data, dict):
        raise PersonaFetchError("Persona endpoint'i JSON objesi dönmedi")

    # En yaygın anahtar isimleri kontrol ediliyor
    name = data.get("name")
    tone = data.get("tone")
    constraints = data.get("constraints")

    # Bazı backendlere göre persona verisi 'persona' anahtarı altında olabilir
    if not (name or tone or constraints) and "persona" in data and isinstance(data.get("persona"), dict):
        persona_obj = data["persona"]  # burası dict olduğundan eminiz (yukarıdaki isinstance)
        name = name or persona_obj.get("name")
        tone = tone or persona_obj.get("tone")
        constraints = constraints or persona_obj.get("constraints")

    # Diğer yaygın yerleşimler: 'attributes' veya 'settings'
    if not (name or tone or constraints):
        for key in ("attributes", "settings"):
            if key in data and isinstance(data[key], dict):
                nested = data[key]
                name = name or nested.get("name")
                tone = tone or nested.get("tone")
                constraints = constraints or nested.get("constraints")

    # Son olarak, hem kullanımı kolay alanlar hem de ham yanıtı döndürülüyor
    return {
        "name": name,
        "tone": tone,
        "constraints": constraints,
        "raw": data,  # Ham JSON yanıtı
    }



def fetch_persona(
    api_url: Optional[str] = None,
    token: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
    ably_channel: Optional[str] = None,
    ably_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Backend Panel API'den veya Ably kanalından persona bilgilerini çeker.
    Öncelik: Ably bilgileri varsa Ably'den, yoksa API URL'den veri çekilir.
    """
    # Tercih sırası: eğer Ably bilgileri sağlanmışsa Ably üzerinden,
    # aksi halde API URL'i varsa doğrudan backend API üzerinden al.
    if ably_channel and ably_api_key:
        # Ably'den çekme seçeneği genelde realtime veya opsiyonel
        # bir yapı sağlar; test ortamlarında bu değerlerin doğru
        # olduğundan emin olun.
        print("Ably üzerinden persona çekiliyor...")
        data = _fetch_from_ably(ably_channel, ably_api_key, timeout)
    elif api_url:
        print("Backend API üzerinden persona çekiliyor...")
        data = _fetch_from_api(api_url, token, timeout)
    else:
        # Ne Ably ne de API URL verilmemişse hata fırlatılır
        raise ValueError(
            "En az bir kaynak belirtilmelidir: ya (ably_channel ve ably_api_key) ya da api_url."
        )

    # Ham veriden name/tone/constraints alanlarını çıkarıp döndür
    return _extract_persona_fields(data)


# Bu modülün amacı veri çekmek olduğundan, ana çalıştırma bloğu eklenmemiştir.
# Test veya doğrudan çalıştırma için main fonksiyonu eklenmemiştir.