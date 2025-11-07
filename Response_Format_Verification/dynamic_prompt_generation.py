
"""
Dinamik Prompt Oluşturma Modülü (LangChain Versiyonu)

Bu modül, persona verilerini kullanarak dinamik sistem prompt'ları oluşturur
ve LangChain PromptTemplate yapısını kullanır.
"""


# Gerekli kütüphaneler import ediliyor
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv  # Ortam değişkenlerini yüklemek için
from langchain.prompts import (
    ChatPromptTemplate,              # Sohbet için prompt şablonu
    SystemMessagePromptTemplate,     # Sistem mesajı şablonu
    HumanMessagePromptTemplate       # Kullanıcı mesajı şablonu
)
from langchain.schema import SystemMessage  # LangChain sistem mesajı tipi


# Genel amaç:
# Bu modül persona verilerini alıp (fetch_persona aracılığıyla),
# LangChain için uygun bir SystemMessage içeriği oluşturur ve
# ChatPromptTemplate hazırlayarak model çağrılarına hazırlar.
# Fonksiyonlar:
# - load_environment_variables: .env'den gerekli değişkenleri okur
# - fetch_persona_data: persona verisini çeker
# - validate_persona_data: zorunlu alanların varlığını kontrol eder
# - create_langchain_system_message: SystemMessage oluşturur
# - build_dynamic_prompt_template: ChatPromptTemplate döner


# Varsayılan persona modülü import'u (orijinal koddan)
try:
    # fetch_persona'nın aynı imza ile çalıştığını varsayıyoruz
    from persona import fetch_persona 
except ImportError:
    print("⚠️ 'persona.py' modülü bulunamadı. Persona yüklemesi atlanacaktır.")
    # Stub fallback; persona.py yoksa çağrıları bozmayacak şekilde aynı
    # imzaya sahip bir fonksiyon tanımlıyoruz.
    def fetch_persona(
        api_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 5,
        ably_channel: Optional[str] = None,
        ably_api_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        return None



# --- Sabitler ---
# LangChain'de SystemMessage'ı ayrı bir şablonda tanımlamak daha temizdir.
# Değişkenleri {name}, {tone}, {constraints} olarak tutuyoruz.
SYSTEM_PROMPT_TEMPLATE_PART = """
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



# Ortam yapılandırması eksik veya hatalı olduğunda fırlatılır
class EnvironmentConfigError(Exception):
    """Ortam yapılandırması eksik veya hatalı olduğunda fırlatılır."""
    pass

# Persona verisi alınırken veya işlenirken hata oluştuğunda fırlatılır
class PersonaError(Exception):
    """Persona verisi alınırken veya işlenirken hata oluştuğunda fırlatılır."""
    pass



def load_environment_variables() -> Dict[str, Optional[str]]:
    """
    .env dosyasından gerekli ortam değişkenlerini yükler.
    Gerekli API ve Ably bilgilerini okur, eksikse hata fırlatır.
    """
    load_dotenv()  # .env dosyasını yükler
    
    # Gerekli ortam değişkenleri bir sözlükte toplanıyor
    required_vars = {
        "PERSONA_API_URL": os.getenv("PERSONA_API_URL"),
        "PERSONA_API_TOKEN": os.getenv("PERSONA_API_TOKEN"),
        "ABLY_API_KEY": os.getenv("ABLY_API_KEY"),
        "ABLY_CHANNEL": os.getenv("ABLY_CHANNEL")
    }
    
    # Eksik değişkenler kontrol ediliyor
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        # Eksik varsa özel hata fırlatılır
        raise EnvironmentConfigError(
            f"Eksik ortam değişkenleri: {', '.join(missing_vars)}\n"
            f"Lütfen .env dosyanızı kontrol edin."
        )
    
    return required_vars



def fetch_persona_data(config: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    API'den persona verilerini çeker.
    fetch_persona fonksiyonu ile API veya Ably'den veri alınır.
    """
    print("Persona verisi çekiliyor...")
    
    # API veya Ably üzerinden persona verisi çekiliyor
    persona_data = fetch_persona(
        api_url=config["PERSONA_API_URL"],
        token=config["PERSONA_API_TOKEN"],
        ably_api_key=config["ABLY_API_KEY"],
        ably_channel=config["ABLY_CHANNEL"]
    )
    
    # Veri alınamazsa hata fırlatılır
    if not persona_data:
        raise PersonaError("Persona verisi alınamadı veya boş döndü.")
    
    return persona_data



def validate_persona_data(persona_data: Dict[str, Any]) -> None:
    """
    Persona verisinin gerekli alanlarını kontrol eder.
    'name', 'tone', 'constraints' alanları eksikse hata fırlatır.
    """
    required_fields = ["name", "tone", "constraints"]
    missing_fields = [field for field in required_fields if not persona_data.get(field)]
    
    if missing_fields:
        # Eksik alan varsa özel hata fırlatılır
        raise PersonaError(
            f"Persona verisinde eksik alanlar: {', '.join(missing_fields)}"
        )



def create_langchain_system_message(persona_data: Dict[str, Any]) -> SystemMessage:
    """
    Persona verilerinden bir LangChain SystemMessage nesnesi oluşturur.
    Persona bilgileri şablona yerleştirilerek sistem mesajı hazırlanır.
    """
    # Persona bilgileri şablona yerleştiriliyor
    formatted_content = SYSTEM_PROMPT_TEMPLATE_PART.format(
        name=persona_data["name"],
        tone=persona_data["tone"],
        constraints=persona_data["constraints"]
    )
    
    # LangChain SystemMessage nesnesi olarak döndürülüyor
    return SystemMessage(content=formatted_content)



def build_dynamic_prompt_template(system_message: SystemMessage) -> ChatPromptTemplate:
    """
    Sistem mesajı (Persona) ve kullanıcı girdisi için nihai LangChain
    ChatPromptTemplate'i oluşturur.
    Modelin hem sistem hem kullanıcı mesajlarını doğru şekilde işlemesini sağlar.
    """
    # Prompt şablonunun bileşenleri hazırlanıyor
    # Bazı LangChain sürümlerinde SystemMessage.content beklenen tipte
    # olmayabilir; güvenli bir şekilde string'e çeviriyoruz.
    template_text = system_message.content if isinstance(system_message.content, str) else str(system_message.content)

    message_templates: List[Any] = [
        # 1. Sistem Mesajı (Persona)
        SystemMessagePromptTemplate.from_template(template_text),
        # 2. Kullanıcı Mesajı (Dinamik Girdi)
        HumanMessagePromptTemplate.from_template("{user_prompt}")
    ]
    
    # Nihai prompt şablonu döndürülüyor
    return ChatPromptTemplate.from_messages(message_templates)



def display_system_prompt(system_message: SystemMessage) -> None:
    """
    Oluşturulan sistem mesajını formatlı şekilde ekrana yazdırır.
    Sistem mesajı içeriği ekrana basılır.
    """
    print("\n=== BAŞARILI: Persona Yüklendi ===")
    print("\n--- OLUŞTURULAN LANGCHAIN SYSTEM MESSAGE İÇERİĞİ ---")
    # SystemMessage nesnesinin içeriğini yazdırıyoruz
    print(system_message.content) 
    print("----------------------------------------------------")



def build_prompt() -> Optional[ChatPromptTemplate]:
    """
    Ana fonksiyon: Ortam değişkenlerini yükler, persona verisini çeker
    ve LangChain ChatPromptTemplate'i oluşturur.
    Tüm adımlar sırasıyla çalıştırılır, hata olursa ekrana basılır.
    """
    try:
        # Ortam değişkenlerini yükle
        config = load_environment_variables()
        
        # Persona verisini çek
        persona_data = fetch_persona_data(config)
        
        # Persona verisini doğrula
        validate_persona_data(persona_data)
        
        # LangChain SystemMessage oluştur
        system_message = create_langchain_system_message(persona_data)
        
        # Ekrana yazdır
        display_system_prompt(system_message)
        
        # Nihai Prompt Template oluştur
        prompt_template = build_dynamic_prompt_template(system_message)
        
        return prompt_template
        
    except EnvironmentConfigError as e:
        # Ortam değişkeni hatası ekrana basılır
        print(f"❌ Konfigürasyon Hatası: {e}")
        return None
        
    except PersonaError as e:
        # Persona verisi hatası ekrana basılır
        print(f"❌ Persona Hatası: {e}")
        return None
        
    except Exception as e:
        # Diğer beklenmeyen hatalar ekrana basılır
        print(f"❌ Beklenmeyen Hata: {e}")
        return None



# Ana dosya olarak çalıştırıldığında şablonun başarıyla oluşturulup oluşturulmadığı test edilir
if __name__ == "__main__":
    # Sadece şablonun başarıyla oluşturulup oluşturulmadığını test eder
    final_template = build_prompt()
    
    if final_template:
        print("\n--- Şablon Testi ---")
        # Örnek bir kullanıcı girdisi ile test etme
        test_input = final_template.format_messages(user_prompt="Merhaba, nasılsın?")
        print(f"Test Prompt Mesajları (LangChain Formatında):\n{test_input}")