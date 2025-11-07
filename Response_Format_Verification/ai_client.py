"""
AI İstemci Modülü (LangChain Versiyonu)

Google Gemini API kullanarak persona tabanlı sohbet uygulaması (LangChain ile yeniden yazıldı).
"""

import os
import json
import datetime
import uuid
from typing import Optional, Dict, Any, List, Union
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import RunnableConfig

# Persona modülü import
try:
    from persona import fetch_persona
except ImportError:
    print("⚠️ 'persona.py' modülü bulunamadı. Persona yüklemesi atlanacaktır.")
    def fetch_persona(
        api_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 5,
        ably_channel: Optional[str] = None,
        ably_api_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        return None


# --- Sabitler ---
DEFAULT_TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 500
CHAT_MODEL_ID = "gemini-2.5-flash"
EXIT_COMMANDS = ["exit", "q", "quit"]


class AIClientError(Exception):
    """AI istemci hatalarını temsil eder."""
    pass


# --- Ortam ve Model Yükleme ---

def load_api_configuration() -> str:
    """GEMINI_API_KEY'i yükler ve doğrular."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "dummy" in api_key.lower():
        raise AIClientError("GEMINI_API_KEY eksik veya geçersiz. Lütfen .env dosyanızı kontrol edin.")
    return api_key


def initialize_langchain_model(api_key: str) -> ChatGoogleGenerativeAI:
    """LangChain ChatGoogleGenerativeAI modelini başlatır."""
    os.environ["GEMINI_API_KEY"] = api_key
    model = ChatGoogleGenerativeAI(model=CHAT_MODEL_ID, temperature=DEFAULT_TEMPERATURE)
    print(f"✅ LangChain ChatModel ({CHAT_MODEL_ID}) başarıyla başlatıldı.")
    return model


def load_backend_configuration() -> Dict[str, Optional[str]]:
    """Backend panel yapılandırmasını ortamdan çeker."""
    return {
        "url": os.getenv("BACKEND_PANEL_URL"),
        "token": os.getenv("BACKEND_PANEL_TOKEN"),
        "ably_channel": os.getenv("BACKEND_PANEL_ABLY_CHANNEL"),
        "ably_api_key": os.getenv("BACKEND_PANEL_ABLY_API_KEY"),
    }


def load_persona(config: Dict[str, Optional[str]]) -> Optional[Dict[str, Any]]:
    """Backend veya Ably'den persona verisini yükler."""
    if not (config["url"] or config["ably_channel"]):
        return None
    try:
        persona = fetch_persona(
            config["url"],
            token=config["token"],
            ably_channel=config["ably_channel"],
            ably_api_key=config["ably_api_key"],
        )
        print("✅ Persona verisi alındı:", persona)

        persona_name = persona.get("name") if isinstance(persona, dict) else "(isimsiz)"
        print(f"✅ Persona backend'den yüklendi: {persona_name}")
        return persona
    except Exception as e:
        print(f"⚠️ Persona backend'den yüklenemedi: {e}")
        return None


# --- Yardımcı Fonksiyonlar ---

def build_persona_prefix(persona: Dict[str, Any]) -> str:
    """Persona bilgisinden açıklayıcı metin oluşturur."""
    parts = []
    if persona.get("name"):
        parts.append(f"Persona adı: {persona.get('name')}")
    if persona.get("tone"):
        parts.append(f"Ton: {persona.get('tone')}")
    if persona.get("constraints"):
        parts.append(f"Kısıtlamalar: {persona.get('constraints')}")
    return " | ".join(parts) if parts else ""


def create_persona_system_message(persona: Optional[Dict[str, Any]]) -> Optional[SystemMessage]:
    """Persona'dan LangChain SystemMessage oluşturur."""
    if not persona:
        return None
    prefix = build_persona_prefix(persona)
    if prefix:
        return SystemMessage(content=f"Sen daima şu kurallara uyacaksın: {prefix}.")
    return None


def create_prompt_chain(system_message: Optional[SystemMessage]) -> ChatPromptTemplate:
    """System ve Human mesajlarını zincir halinde hazırlar."""
    messages: List[Any] = []
    if system_message:
        text = system_message.content if isinstance(system_message.content, str) else str(system_message.content)
        messages.append(SystemMessagePromptTemplate.from_template(text))
    messages.append(HumanMessagePromptTemplate.from_template("{user_prompt}"))
    return ChatPromptTemplate.from_messages(messages)


# --- Response Formatlama ve Görselleştirme ---

def format_response(reply: Optional[str] = None, error: Optional[Union[str, Exception]] = None) -> Dict[str, Any]:
    """AI yanıtını Chat Core için standart JSON formatına çevirir."""
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    assistant_id = "persona_001"  # ileride backend’den alınabilir

    if error:
        return {
            "assistant_id": assistant_id,
            "status": "error",
            "type": "system",
            "error_message": str(error),
            "timestamp": timestamp,
        }

    return {
        "assistant_id": assistant_id,
        "status": "success",
        "type": "message",
        "reply": reply,
        "timestamp": timestamp,
    }


def display_response(response: Optional[Dict[str, Any]]) -> None:
    """Yanıtı JSON formatında terminalde gösterir."""
    if not response:
        print("⚠️ Model boş bir yanıt döndürdü.")
        return

    print("🤖 Formatlı Yanıt:")
    print("--------------------------------------------------")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    print("--------------------------------------------------\n")


# --- Sohbet Döngüsü ---

def run_chat_loop(model: ChatGoogleGenerativeAI, persona: Optional[Dict[str, Any]]) -> None:
    """LangChain tabanlı ana sohbet döngüsü."""
    system_message = create_persona_system_message(persona)
    prompt_template = create_prompt_chain(system_message)
    chain = prompt_template | model

    print("💬 Sohbeti sonlandırmak için 'exit', 'q' veya 'quit' yazın.\n")
    if system_message:
        print(f"⚙️ Persona Etkin: {system_message.content}")

    while True:
        try:
            user_prompt = input("🧠 Prompt: ").strip()
            if user_prompt.lower() in EXIT_COMMANDS:
                print("👋 Sohbet sonlandırıldı.")
                break
            if not user_prompt:
                print("⚠️ Lütfen geçerli bir prompt girin.")
                continue

            print("\n⏳ Yanıt oluşturuluyor...\n")
            response_message = chain.invoke({"user_prompt": user_prompt}, config=RunnableConfig())

            raw_content = getattr(response_message, "content", None)
            response_text: Optional[str]

            if isinstance(raw_content, list):
                parts = [str(getattr(item, "text", item)) for item in raw_content]
                response_text = " ".join(parts).strip()
            elif isinstance(raw_content, str):
                response_text = raw_content.strip()
            elif isinstance(raw_content, dict) and raw_content.get("text"):
                response_text = str(raw_content.get("text")).strip()
            else:
                response_text = str(raw_content).strip() if raw_content else None

            formatted = format_response(reply=response_text)
            display_response(formatted)

        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            formatted = format_response(error=e)
            display_response(formatted)


# --- Ana Program ---

def main() -> None:
    """Ana giriş noktası."""
    try:
        api_key = load_api_configuration()
        model = initialize_langchain_model(api_key)
        backend_config = load_backend_configuration()
        persona = load_persona(backend_config)
        run_chat_loop(model, persona)
    except AIClientError as e:
        print(f"🚨 HATA: {e}")
    except Exception as e:
        print(f"🚨 Beklenmeyen HATA: {e}")


if __name__ == "__main__":
    main()
