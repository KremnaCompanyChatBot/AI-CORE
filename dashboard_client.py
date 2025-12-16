"""
Dashboard API İstemci Modülü

Dashboard'dan assistant ve chat verilerini çeker ve işler.
"""

from typing import Dict, List, Any, Optional
import requests
from datetime import datetime


class DashboardError(Exception):
    """Dashboard API hatalarını temsil eder."""
    pass


def fetch_dashboard_data(api_url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Dashboard API'den tüm verileri çeker.
    
    Parametreler:
        api_url: Dashboard API endpoint URL'i
        timeout: İstek zaman aşımı süresi (saniye)
        
    Dönüş Değeri:
        Dict[str, Any]: Dashboard'dan gelen ham veri
        
    Hatalar:
        DashboardError: API'den veri çekilemezse
    """
    try:
        response = requests.get(api_url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        # Status kontrolü
        if data.get("status") != "success":
            raise DashboardError(f"Dashboard API başarısız status döndü: {data.get('status')}")
        
        return data
        
    except requests.RequestException as e:
        raise DashboardError(f"Dashboard API'den veri çekilirken hata: {e}")


def get_assistants(dashboard_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Dashboard verisinden assistant listesini çıkarır.
    
    Parametreler:
        dashboard_data: Dashboard API'den gelen ham veri
        
    Dönüş Değeri:
        List[Dict]: Assistant listesi
        [{"assistantId": "a1", "name": "AI Tarihçi"}, ...]
    """
    data = dashboard_data.get("data", {})
    assistants = data.get("assistants", [])
    
    return assistants


def get_assistant_by_id(dashboard_data: Dict[str, Any], assistant_id: str) -> Optional[Dict[str, str]]:
    """
    Belirli bir assistant ID'ye göre assistant bilgisini getirir.
    
    Parametreler:
        dashboard_data: Dashboard API'den gelen ham veri
        assistant_id: Aranacak assistant ID'si
        
    Dönüş Değeri:
        Optional[Dict]: Assistant bilgisi veya None
    """
    assistants = get_assistants(dashboard_data)
    
    for assistant in assistants:
        if assistant.get("assistantId") == assistant_id:
            return assistant
    
    return None


def get_chats_by_assistant(dashboard_data: Dict[str, Any], assistant_id: str) -> List[Dict[str, Any]]:
    """
    Belirli bir assistant'a ait tüm chat'leri getirir.
    
    Parametreler:
        dashboard_data: Dashboard API'den gelen ham veri
        assistant_id: Assistant ID'si
        
    Dönüş Değeri:
        List[Dict]: Chat listesi
    """
    data = dashboard_data.get("data", {})
    all_chats = data.get("chats", [])
    
    # Belirli assistant'a ait chat'leri filtrele
    assistant_chats = [
        chat for chat in all_chats 
        if chat.get("assistantId") == assistant_id
    ]
    
    return assistant_chats


def get_messages_by_user(
    dashboard_data: Dict[str, Any], 
    assistant_id: str, 
    user_id: str
) -> List[Dict[str, Any]]:
    """
    Belirli bir kullanıcının belirli bir assistant ile yaptığı chat'in mesajlarını getirir.
    
    Parametreler:
        dashboard_data: Dashboard API'den gelen ham veri
        assistant_id: Assistant ID'si
        user_id: Kullanıcı ID'si
        
    Dönüş Değeri:
        List[Dict]: Mesaj listesi
    """
    chats = get_chats_by_assistant(dashboard_data, assistant_id)
    
    for chat in chats:
        if chat.get("userId") == user_id:
            return chat.get("messages", [])
    
    return []


def get_chat_history_text(messages: List[Dict[str, Any]]) -> str:
    """
    Mesaj listesini okunabilir metin formatına çevirir.
    
    Parametreler:
        messages: Mesaj listesi
        
    Dönüş Değeri:
        str: Formatlanmış chat geçmişi
    """
    if not messages:
        return "Mesaj geçmişi yok."
    
    history_lines = []
    
    for msg in messages:
        sender = msg.get("sender", "unknown")
        message = msg.get("message", "")
        timestamp = msg.get("timestamp", "")
        
        # Sender'ı Türkçeleştir
        sender_text = "Kullanıcı" if sender == "user" else "Asistan"
        
        history_lines.append(f"[{timestamp}] {sender_text}: {message}")
    
    return "\n".join(history_lines)


def get_analytics(dashboard_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Dashboard verisinden analytics bilgilerini çıkarır.
    
    Parametreler:
        dashboard_data: Dashboard API'den gelen ham veri
        
    Dönüş Değeri:
        List[Dict]: Analytics listesi
    """
    data = dashboard_data.get("data", {})
    analytics = data.get("analytics", [])
    
    return analytics


def print_dashboard_summary(dashboard_data: Dict[str, Any]) -> None:
    """
    Dashboard verisinin özetini ekrana yazdırır.
    
    Parametreler:
        dashboard_data: Dashboard API'den gelen ham veri
    """
    assistants = get_assistants(dashboard_data)
    
    data = dashboard_data.get("data", {})
    chats = data.get("chats", [])
    analytics = data.get("analytics", [])
    
    print("\n" + "="*60)
    print("DASHBOARD VERİ ÖZETİ")
    print("="*60)
    
    print(f"\n📋 Toplam Assistant: {len(assistants)}")
    for assistant in assistants:
        print(f"  - [{assistant['assistantId']}] {assistant['name']}")
    
    print(f"\n💬 Toplam Chat: {len(chats)}")
    for chat in chats:
        assistant_id = chat.get("assistantId")
        user_id = chat.get("userId")
        message_count = len(chat.get("messages", []))
        print(f"  - {assistant_id} <-> {user_id}: {message_count} mesaj")
    
    print(f"\n📊 Toplam Analytics Event: {len(analytics)}")
    for event in analytics[:3]:  # İlk 3 event
        event_name = event.get("event_name")
        count = event.get("count")
        print(f"  - {event_name}: {count} kez")
    
    print("\n" + "="*60)


# Test fonksiyonu
def test_with_sample_data():
    """
    Örnek JSON verisi ile test eder.
    """
    # Örnek JSON verisi
    sample_data = {
        "status": "success",
        "timestamp": "2025-10-22T12:00:00Z",
        "data": {
            "assistants": [
                {"assistantId": "a1", "name": "AI Tarihçi"},
                {"assistantId": "a2", "name": "AI Matematikçi"},
                {"assistantId": "a3", "name": "AI Danışman"}
            ],
            "chats": [
                {
                    "assistantId": "a1",
                    "userId": "u123",
                    "messages": [
                        {
                            "id": "m1",
                            "sender": "user",
                            "message": "Selam!",
                            "timestamp": "2025-10-22T01:40:51Z"
                        },
                        {
                            "id": "m2",
                            "sender": "assistant",
                            "message": "Merhaba!",
                            "timestamp": "2025-10-22T01:40:52Z"
                        }
                    ]
                },
                {
                    "assistantId": "a2",
                    "userId": "u345",
                    "messages": [
                        {
                            "id": "m3",
                            "sender": "user",
                            "message": "Merhaba!",
                            "timestamp": "2025-10-22T01:40:51Z"
                        },
                        {
                            "id": "m4",
                            "sender": "assistant",
                            "message": "Harika!",
                            "timestamp": "2025-10-22T01:40:52Z"
                        }
                    ]
                }
            ],
            "analytics": [
                {
                    "event_name": "cta_click",
                    "page_url": "/landing",
                    "event_label": "Üye Ol Butonu",
                    "count": 52,
                    "created_at": "2025-10-22T10:00:00Z"
                },
                {
                    "event_name": "cta_click",
                    "page_url": "/landing",
                    "event_label": "Giriş yap Butonu",
                    "count": 120,
                    "created_at": "2025-10-22T10:00:00Z"
                }
            ]
        },
        "meta": {
            "request_id": "req_89231abc",
            "version": "1.0.0"
        }
    }
    
    # Özet yazdır
    print_dashboard_summary(sample_data)
    
    # Assistant bilgisi çek
    print("\n--- Assistant Detayı ---")
    assistant = get_assistant_by_id(sample_data, "a1")
    if assistant:
        print(f"✓ {assistant['name']} bulundu (ID: {assistant['assistantId']})")
    
    # Mesaj geçmişi çek
    print("\n--- Chat Geçmişi ---")
    messages = get_messages_by_user(sample_data, "a1", "u123")
    history = get_chat_history_text(messages)
    print(history)


if __name__ == "__main__":
    test_with_sample_data()
