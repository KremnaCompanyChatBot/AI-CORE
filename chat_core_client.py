"""
Chat Core API İstemci Modülü

Chat Core'dan gelen chat request'lerini işler.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class ChatCoreError(Exception):
    """Chat Core API hatalarını temsil eder."""
    pass


def parse_chat_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chat Core'dan gelen request'i parse eder.
    
    Parametreler:
        request_data: Chat Core'dan gelen JSON verisi
        
    Dönüş Değeri:
        Dict: Parse edilmiş veri
        {
            "agent_id": str,
            "session_id": str,
            "user_message": str,
            "chat_history": List[Dict]
        }
        
    Hatalar:
        ChatCoreError: Gerekli alanlar eksikse
    """
    # Zorunlu alanları kontrol et
    required_fields = ["agent_id", "session_id", "user_message"]
    
    for field in required_fields:
        if field not in request_data:
            raise ChatCoreError(f"Eksik alan: {field}")
    
    return {
        "agent_id": request_data["agent_id"],
        "session_id": request_data["session_id"],
        "user_message": request_data["user_message"],
        "chat_history": request_data.get("chat_history", [])
    }


def format_chat_history_for_gemini(chat_history: List[Dict[str, Any]]) -> str:
    """
    Chat geçmişini Gemini için uygun formata çevirir.
    
    Parametreler:
        chat_history: Chat Core'dan gelen mesaj listesi
        
    Dönüş Değeri:
        str: Formatlanmış chat geçmişi metni
    """
    if not chat_history:
        return ""
    
    history_lines = []
    
    for msg in chat_history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        timestamp = msg.get("created_at", "")
        
        # Role'ü Türkçeleştir
        role_text = "Kullanıcı" if role == "user" else "Asistan"
        
        history_lines.append(f"{role_text}: {content}")
    
    # Geçmiş mesajlar başlığı ile birleştir
    history_text = "\n".join(history_lines)
    
    return f"--- Önceki Konuşma ---\n{history_text}\n--- Güncel Soru ---\n"


def build_full_prompt_with_history(
    user_message: str,
    chat_history: List[Dict[str, Any]],
    persona: Optional[Dict[str, Any]] = None
) -> str:
    """
    Kullanıcı mesajını, chat geçmişini ve persona bilgilerini birleştirerek tam prompt oluşturur.
    
    Parametreler:
        user_message: Kullanıcının son mesajı
        chat_history: Önceki konuşma geçmişi
        persona: Persona bilgileri (opsiyonel)
        
    Dönüş Değeri:
        str: Gemini'ye gönderilecek tam prompt
    """
    prompt_parts = []
    
    # Persona prefix'i ekle (varsa)
    if persona:
        persona_info = []
        if persona.get("name"):
            persona_info.append(f"Sen {persona['name']} adında bir asistansın.")
        if persona.get("tone"):
            persona_info.append(f"Konuşma tonun: {persona['tone']}")
        if persona.get("constraints"):
            persona_info.append(f"Kurallar: {persona['constraints']}")
        
        if persona_info:
            prompt_parts.append("\n".join(persona_info))
    
    # Chat geçmişini ekle
    if chat_history:
        history_text = format_chat_history_for_gemini(chat_history)
        prompt_parts.append(history_text)
    
    # Kullanıcının son mesajını ekle
    prompt_parts.append(user_message)
    
    return "\n\n".join(prompt_parts)


def create_chat_response(
    agent_response: str,
    agent_id: str,
    session_id: str
) -> Dict[str, Any]:
    """
    Chat Core'a gönderilecek response formatını oluşturur.
    
    Parametreler:
        agent_response: AI'dan gelen yanıt
        agent_id: Agent ID'si
        session_id: Session ID'si
        
    Dönüş Değeri:
        Dict: Response JSON
    """
    return {
        "agent_id": agent_id,
        "session_id": session_id,
        "response": agent_response,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }


def validate_chat_history(chat_history: List[Dict[str, Any]]) -> bool:
    """
    Chat geçmişinin formatının geçerli olup olmadığını kontrol eder.
    
    Parametreler:
        chat_history: Kontrol edilecek chat geçmişi
        
    Dönüş Değeri:
        bool: Geçerliyse True
    """
    if not isinstance(chat_history, list):
        return False
    
    for msg in chat_history:
        if not isinstance(msg, dict):
            return False
        
        # role ve content alanları zorunlu
        if "role" not in msg or "content" not in msg:
            return False
        
        # role sadece user veya assistant olabilir
        if msg["role"] not in ["user", "assistant"]:
            return False
    
    return True


# Test fonksiyonu
def test_chat_core_client():
    """
    Chat Core client fonksiyonlarını test eder.
    """
    print("🧪 Chat Core Client Testi\n")
    
    # Örnek request
    sample_request = {
        "agent_id": "agent_8823_xyz",
        "session_id": "sess_user_999",
        "user_message": "Fiyatlarınız neden bu kadar yüksek?",
        "chat_history": [
            {
                "role": "user",
                "content": "Merhaba",
                "created_at": "2025-11-23T10:00:00Z"
            },
            {
                "role": "assistant",
                "content": "Merhaba, size nasıl yardımcı olabilirim?",
                "created_at": "2025-11-23T10:00:05Z"
            }
        ]
    }
    
    # Request'i parse et
    print("--- Request Parse ---")
    parsed = parse_chat_request(sample_request)
    print(f"✓ Agent ID: {parsed['agent_id']}")
    print(f"✓ Session ID: {parsed['session_id']}")
    print(f"✓ User Message: {parsed['user_message']}")
    print(f"✓ History Count: {len(parsed['chat_history'])}")
    
    # Chat geçmişini formatla
    print("\n--- Chat History Format ---")
    history_text = format_chat_history_for_gemini(parsed['chat_history'])
    print(history_text)
    
    # Persona ile tam prompt oluştur
    print("\n--- Full Prompt with Persona ---")
    test_persona = {
        "name": "Yardımcı Asistan",
        "tone": "Profesyonel ve nazik",
        "constraints": "Kısa cevaplar ver. Spekülasyon yapma."
    }
    
    full_prompt = build_full_prompt_with_history(
        parsed['user_message'],
        parsed['chat_history'],
        test_persona
    )
    print(full_prompt)
    
    # Response oluştur
    print("\n--- Response Format ---")
    response = create_chat_response(
        "Fiyatlarımız, kaliteli hizmet ve uzman kadromuz nedeniyle belirlenmiştir.",
        parsed['agent_id'],
        parsed['session_id']
    )
    print(f"✓ Response: {response['response'][:50]}...")
    print(f"✓ Timestamp: {response['timestamp']}")
    
    # Validation testi
    print("\n--- Validation Test ---")
    is_valid = validate_chat_history(parsed['chat_history'])
    print(f"✓ Chat history geçerli: {is_valid}")
    
    print("\n✅ Test tamamlandı!")


if __name__ == "__main__":
    test_chat_core_client()
