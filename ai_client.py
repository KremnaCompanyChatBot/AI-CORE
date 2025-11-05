
"""
AI İstemci Modülü (LangChain Versiyonu)

Google Gemini API kullanarak persona tabanlı sohbet uygulaması (LangChain ile yeniden yazıldı).
"""


# Gerekli kütüphaneler import ediliyor
import os
from typing import Optional, Dict, Any, List
import google.generativeai as genai  # genai sadece anahtar yapılandırması için bırakıldı
from dotenv import load_dotenv  # Ortam değişkenlerini yüklemek için
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini model entegrasyonu
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage  # Mesaj tipleri
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate  # Prompt şablonları
from langchain.schema.runnable import RunnableConfig  # Zincir yapılandırması


# Genel açıklama:
# Bu modül, ortam değişkenlerinden yapılandırma okuyup (ör. GEMINI_API_KEY,
# BACKEND_PANEL_URL, ABLY bilgileri), persona verisini backend veya Ably'den
# çekip LangChain / Google Gemini (ChatGoogleGenerativeAI) modeli ile etkileşen
# bir sohbet döngüsü sağlar.


# Varsayılan persona modülü import'u (orijinal koddan)
# Gerçek bir uygulamada, fetch_persona'nın LangChain/API uyumlu olması gerekebilir.
try:
    from persona import fetch_persona
except ImportError:
    print("⚠️ 'persona.py' modülü bulunamadı. Persona yüklemesi atlanacaktır.")
    # Fallback fonksiyonu: persona.py yoksa tip uyumluluğu için aynı imzaya
    # sahip bir stub tanımlıyoruz. Tip olarak Optional[Dict[str, Any]] döner.
    def fetch_persona(
        api_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 5,
        ably_channel: Optional[str] = None,
        ably_api_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        return None


# --- Sabitler ---
# Model sıcaklığı (cevapların çeşitliliği)
DEFAULT_TEMPERATURE = 0.7
# Maksimum çıktı token sayısı (kullanılmıyor ama ileride eklenebilir)
MAX_OUTPUT_TOKENS = 500
# Gemini model adı
GEMINI_MODEL_NAME = "gemini-2.5-flash"
# LangChain için model versiyonu
CHAT_MODEL_ID = "gemini-2.5-flash"

# Sohbetten çıkış komutları
EXIT_COMMANDS = ["exit", "q", "quit"]



# AI istemci hatalarını temsil eden özel exception
class AIClientError(Exception):
    """AI istemci hatalarını temsil eder."""
    pass



def load_api_configuration() -> str:
    """
    Ortam değişkenlerinden API anahtarını yükler ve doğrular.
    Gemini API anahtarı eksik veya geçersizse hata fırlatır.
    """
    load_dotenv()  # .env dosyasını yükler
    
    # Gemini için anahtarın GEMINI_API_KEY olması beklenir.
    api_key = os.getenv("GEMINI_API_KEY") 
    
    # Anahtar yoksa veya dummy ise hata fırlatılır
    if not api_key or "dummy" in api_key.lower():
        raise AIClientError(
            "GEMINI_API_KEY eksik veya geçersiz. "
            "Lütfen .env dosyanızı kontrol edin."
        )
    
    return api_key



def initialize_langchain_model(api_key: str) -> ChatGoogleGenerativeAI:
    """
    LangChain ChatGoogleGenerativeAI modelini yapılandırır ve başlatır.
    Google Gemini API anahtarı ile LangChain modelini başlatır.
    """
    # Ortam değişkeni ayarlanıyor (LangChain otomatik çekebilsin diye)
    if "GEMINI_API_KEY" not in os.environ:
         os.environ["GEMINI_API_KEY"] = api_key
         
    # Model nesnesi oluşturuluyor
    model = ChatGoogleGenerativeAI(
        model=CHAT_MODEL_ID,
        temperature=DEFAULT_TEMPERATURE,
        # streaming=True  # Akış isteseydik buraya eklenebilirdi
    )
    print(f"✅ LangChain ChatModel ({CHAT_MODEL_ID}) başarıyla başlatıldı.")
    return model


# --- Backend ve Persona İşlevleri (Orijinal mantık korunmuştur) ---


def load_backend_configuration() -> Dict[str, Optional[str]]:
    """
    Ortam değişkenlerinden backend ve Ably yapılandırmasını yükler.
    Sohbet için gerekli bağlantı bilgilerini döndürür.
    """
    return {
        "url": os.getenv("BACKEND_PANEL_URL"),
        "token": os.getenv("BACKEND_PANEL_TOKEN"),
        "ably_channel": os.getenv("BACKEND_PANEL_ABLY_CHANNEL"),
        "ably_api_key": os.getenv("BACKEND_PANEL_ABLY_API_KEY")
    }



def load_persona(config: Dict[str, Optional[str]]) -> Optional[Dict[str, Any]]:
    """
    Backend veya Ably'den persona verisini yükler.
    Persona verisi yoksa veya hata olursa None döner.
    """
    if not (config["url"] or config["ably_channel"]):
        return None
    
    try:
        # Persona verisi çekiliyor
        persona = fetch_persona(
            config["url"],
            token=config["token"],
            ably_channel=config["ably_channel"],
            ably_api_key=config["ably_api_key"]
        )
        # persona None dönebilir; bu nedenle önce dict olduğundan emin ol
        persona_name = persona.get("name") if isinstance(persona, dict) and persona.get("name") else "(isimsiz)"
        print(f"✅ Persona backend'den yüklendi: {persona_name}")
        return persona

    except Exception as e:
        print(f"⚠️ Persona backend'den yüklenemedi: {e}")
        return None



def build_persona_prefix(persona: Dict[str, Any]) -> str:
    """
    Persona sözlüğünden özet bir string oluşturur.
    Ad, ton ve kısıtlamaları birleştirir.
    """
    parts = []
    
    if persona.get("name"):
        parts.append(f"Persona adı: {persona.get('name')}")
    
    if persona.get("tone"):
        parts.append(f"Ton: {persona.get('tone')}")
    
    if persona.get("constraints"):
        parts.append(f"Kısıtlamalar: {persona.get('constraints')}")
    
    # Parçaları birleştirip döndür
    return " | ".join(parts) if parts else ""



def create_persona_system_message(persona: Optional[Dict[str, Any]]) -> Optional[SystemMessage]:
    """
    Persona bilgilerinden bir SystemMessage oluşturur.
    Persona özetini sistem mesajı olarak döndürür.
    """
    if not persona:
        return None
    
    persona_prefix = build_persona_prefix(persona)
    
    if persona_prefix:
        # SystemMessage, modelin davranışını yönlendirmek için en uygunudur.
        return SystemMessage(content=f"Sen daima şu kurallara uyacaksın: {persona_prefix}.")
    
    return None


# --- LangChain Entegrasyonu ve Sohbet Döngüsü ---


def create_prompt_chain(system_message: Optional[SystemMessage]) -> ChatPromptTemplate:
    """
    Sistem mesajını (persona) ve kullanıcı girdisini birleştiren zinciri oluşturur.
    Sohbet için prompt zinciri hazırlanır.
    """
    # Temel mesajlar listesi hazırlanıyor
    # Not: LangChain tipleri ve kullanılan sürümler arasında type-hint uyuşmazlıkları
    # olabiliyor (ör. PromptTemplate vs BaseMessage). Statik analizörlerin fazla
    # agresif hata vermesini engellemek için burada daha gevşek bir tip kullanıyoruz.
    messages: List[Any] = []
    
    # Persona varsa ekle
    if system_message:
        # Bazı LangChain sürümlerinde SystemMessage.content'in tipi
        # beklenmeyen bir yapı (ör. liste veya dict) olabilir; buradan
        # güvenli bir string geçirerek type-hata riskini azaltıyoruz.
        template_text = system_message.content if isinstance(system_message.content, str) else str(system_message.content)
        messages.append(SystemMessagePromptTemplate.from_template(template_text))
        
    # Kullanıcı prompt'u ekleniyor
    messages.append(HumanMessagePromptTemplate.from_template("{user_prompt}"))
    
    # ChatPromptTemplate oluşturulup döndürülüyor
    return ChatPromptTemplate.from_messages(messages)



def run_chat_loop(
    model: ChatGoogleGenerativeAI,
    persona: Optional[Dict[str, Any]]
) -> None:
    """
    Ana sohbet döngüsünü çalıştırır (LangChain kullanılarak).
    Kullanıcıdan prompt alır, modele gönderir ve yanıtı ekrana basar.
    """
    system_message = create_persona_system_message(persona)
    
    # Prompt Zincirini Oluştur
    prompt_template = create_prompt_chain(system_message)
    
    # Zinciri oluştur: Prompt Template -> LLM
    # LangChain'in modern 'Runnable' yapısı kullanılır.
    chain = prompt_template | model

    print("💬 Sohbeti sonlandırmak için 'exit', 'q' veya 'quit' yazın.\n")
    
    if system_message:
        print(f"⚙️ Persona Etkin: {system_message.content}")
        
    while True:
        try:
            # Kullanıcıdan prompt alınıyor
            user_prompt = input("🧠 Prompt: ").strip()
              
            # Çıkış kontrolü
            if user_prompt.lower() in EXIT_COMMANDS:
                print("👋 Sohbet sonlandırıldı.")
                break
              
            # Boş prompt kontrolü
            if not user_prompt:
                print("⚠️ Lütfen geçerli bir prompt girin.")
                continue
              
            print("\n⏳ Yanıt oluşturuluyor...\n")
            
            # Zinciri Çalıştır
            # Zincire gönderilecek input dictionary formatında olmalıdır.
            response_message = chain.invoke(
                {"user_prompt": user_prompt},
                config=RunnableConfig()
            )

            # Yanıt mesaj nesnesinden metni al
            # Model adaptörleri farklı tiplerde content dönebilir (str, list, dict, vs.).
            raw_content = getattr(response_message, "content", None)

            response_text: Optional[str]
            if isinstance(raw_content, list):
                # Liste halinde parçalar gelebilir; string olanları birleştir
                parts: List[str] = []
                for item in raw_content:
                    if isinstance(item, str):
                        parts.append(item)
                    elif hasattr(item, "text"):
                        parts.append(str(getattr(item, "text")))
                    else:
                        parts.append(str(item))
                response_text = " ".join(parts).strip() if parts else None

            elif isinstance(raw_content, str):
                response_text = raw_content.strip() if raw_content else None

            else:
                # Sözlük/nesne gibi diğer tipler için güvenli bir deneme
                try:
                    if isinstance(raw_content, dict) and raw_content.get("text"):
                        response_text = str(raw_content.get("text")).strip()
                    else:
                        response_text = str(raw_content).strip() if raw_content else None
                except Exception:
                    response_text = None

            # Yanıtı göster
            display_response(response_text)
              
        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu.")
            break
            
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}\n")



def display_response(response: Optional[str]) -> None:
    """
    Model yanıtını formatlı şekilde ekrana yazdırır.
    Yanıt yoksa uyarı verir.
    """
    if not response:
        print("⚠️ Model boş bir yanıt döndürdü.")
        return
    
    print("🤖 Yanıt:")
    print("--------------------------------------------------")
    print(response)
    print("--------------------------------------------------\n")



def main() -> None:
    """
    Ana program giriş noktası.
    Tüm adımlar sırasıyla çalıştırılır, hata olursa ekrana basılır.
    """
    try:
        # API anahtarını yükle ve doğrula
        api_key = load_api_configuration()
        
        # Gemini modelini LangChain ile başlat
        model = initialize_langchain_model(api_key)
        
        # Backend yapılandırmasını yükle
        backend_config = load_backend_configuration()
        
        # Persona'yı yükle (varsa)
        persona = load_persona(backend_config)
        
        # Sohbet döngüsünü başlat
        run_chat_loop(model, persona)
        
    except AIClientError as e:
        # API anahtarı hatası ekrana basılır
        print(f"🚨 HATA: {e}")
        exit(1)
        
    except Exception as e:
        # Diğer beklenmeyen hatalar ekrana basılır
        print(f"🚨 Beklenmeyen HATA: {e}")
        exit(1)



# Ana dosya olarak çalıştırıldığında ana fonksiyon başlatılır
if __name__ == "__main__":
    main()