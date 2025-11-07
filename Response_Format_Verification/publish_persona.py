import requests
import json
import base64
from dotenv import load_dotenv
import os

load_dotenv()

ABLY_API_KEY = os.getenv("BACKEND_PANEL_ABLY_API_KEY")
CHANNEL = os.getenv("BACKEND_PANEL_ABLY_CHANNEL")

# 🔹 Auth header için base64 encode
encoded_auth = base64.b64encode(ABLY_API_KEY.encode()).decode()

persona_data = {
    "name": "Motivasyon Koçu",
    "tone": "Pozitif, enerjik, ilham verici",
    "constraints": "Cevaplar motive edici ve kısa olsun."
}

headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/json"
}

payload = {
    "name": "persona",
    "data": persona_data
}

response = requests.post(
    f"https://rest.ably.io/channels/{CHANNEL}/messages",
    headers=headers,
    json=payload
)

print("Status Code:", response.status_code)
print("Response:", response.text)
