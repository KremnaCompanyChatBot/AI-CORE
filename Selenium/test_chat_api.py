import os
import requests
#  pytest -q çalıştır.
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:9000")
AGENT_ID = os.getenv("AGENT_ID", "agent_8823_xyz")


def post_chat(user_message: str, timeout: int = 30):
    url = f"{BASE_URL}/chat"
    payload = {
        "agent_id": AGENT_ID,
        "user_message": user_message,
    }
    return requests.post(url, json=payload, timeout=timeout)


def test_chat_returns_success_and_reply():
    r = post_chat("Merhaba, pytest ile API test ediyorum")

    # HTTP seviyesinde kontrol
    assert r.status_code == 200, f"HTTP {r.status_code} döndü. Body: {r.text}"

    data = r.json()

    # API seviyesinde kontrol
    assert data.get("status") == "success", f"status success değil. JSON: {data}"
    assert isinstance(data.get("reply"), str) and data["reply"].strip(), f"reply boş. JSON: {data}"

    # (Opsiyonel) metadata kontrolü
    md = data.get("metadata", {})
    assert md.get("agent_id") == AGENT_ID, f"metadata.agent_id beklenen değil. JSON: {data}"


def test_chat_missing_fields_returns_error():
    # agent_id veya user_message eksik olunca error dönmeli
    url = f"{BASE_URL}/chat"
    r = requests.post(url, json={"agent_id": AGENT_ID}, timeout=30)

    # Bazı backend'ler 200 ile error JSON döndürür, bazıları 4xx döndürür.
    # Bu yüzden iki ihtimali de kabul edip JSON'u doğruluyoruz.
    assert r.status_code in (200, 400, 422), f"Beklenmeyen HTTP {r.status_code}. Body: {r.text}"

    try:
        data = r.json()
    except Exception:
        assert False, f"JSON dönmedi. Body: {r.text}"

    assert data.get("status") == "error", f"status error değil. JSON: {data}"
