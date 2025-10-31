import os
from typing import Optional, Dict, Any
import requests
import base64
import json
from urllib.parse import quote_plus


def fetch_persona(
    api_url: Optional[str],
    token: Optional[str] = None,
    timeout: int = 5,
    ably_channel: Optional[str] = None,
    ably_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch persona information from a Backend Panel API.

    Expected return shape (example):
    {
        "name": "Kremna Assistant",
        "tone": "friendly, concise",
        "constraints": "No medical or legal advice; keep messages < 500 chars"
    }

    The actual backend may wrap persona under a `persona` key; function will try a few common shapes.
    Raises requests.HTTPError on non-2xx responses and ValueError on unexpected payloads.
    """
    # If Ably channel is provided, try to fetch the last message from Ably REST history
    if ably_channel and ably_api_key:
        # Ably REST history endpoint
        # We fetch the most recent message and expect its data to be JSON representing persona
        url = f"https://rest.ably.io/channels/{quote_plus(ably_channel)}/messages?limit=1"
        # Ably uses HTTP Basic auth with the API key as the username and an empty password.
        # So we encode 'APIKEY:' (note the trailing colon) in base64 for the Authorization header.
        basic_token = base64.b64encode(f"{ably_api_key}:".encode()).decode()
        headers = {"Accept": "application/json", "Authorization": f"Basic {basic_token}"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        arr = resp.json()
        # Ably returns an array of messages
        if isinstance(arr, list) and len(arr) > 0:
            # message body can be under 'data'
            msg = arr[0]
            data = msg.get("data") if isinstance(msg, dict) else None
            # If data is a string, try to parse JSON
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    # leave as raw string
                    pass
        else:
            raise ValueError("No messages found on Ably channel to extract persona")
    else:
        if not api_url:
            raise ValueError("api_url is required to fetch persona when Ably is not used")

        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        resp = requests.get(api_url, headers=headers, timeout=timeout)
        resp.raise_for_status()

        data = resp.json()

    # Try common shapes
    if not isinstance(data, dict):
        raise ValueError("Persona endpoint did not return a JSON object")

    # Direct fields
    name = data.get("name")
    tone = data.get("tone")
    constraints = data.get("constraints")

    # Wrapped under 'persona'
    if not (name or tone or constraints) and "persona" in data and isinstance(data["persona"], dict):
        p = data["persona"]
        name = name or p.get("name")
        tone = tone or p.get("tone")
        constraints = constraints or p.get("constraints")

    # Some backends use 'attributes' or 'settings'
    if not (name or tone or constraints):
        for key in ("attributes", "settings"):
            if key in data and isinstance(data[key], dict):
                s = data[key]
                name = name or s.get("name")
                tone = tone or s.get("tone")
                constraints = constraints or s.get("constraints")

    return {
        "name": name,
        "tone": tone,
        "constraints": constraints,
        "raw": data,
    }
