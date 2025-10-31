import os
import google.generativeai as genai
from dotenv import load_dotenv

from persona import fetch_persona

load_dotenv()

# API key for Gemini (keystore name retained for backward compatibility)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or "dummy" in api_key.lower():
    print("🚨 ERROR: OPENAI_API_KEY is missing or invalid.")
    exit()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Backend Panel configuration (optional). If not provided, persona fetch is skipped.
BACKEND_PANEL_URL = os.getenv("BACKEND_PANEL_URL")
BACKEND_PANEL_TOKEN = os.getenv("BACKEND_PANEL_TOKEN")
BACKEND_PANEL_ABLY_CHANNEL = os.getenv("BACKEND_PANEL_ABLY_CHANNEL")
BACKEND_PANEL_ABLY_API_KEY = os.getenv("BACKEND_PANEL_ABLY_API_KEY")

persona = None
if BACKEND_PANEL_URL or BACKEND_PANEL_ABLY_CHANNEL:
    try:
        persona = fetch_persona(
            BACKEND_PANEL_URL,
            token=BACKEND_PANEL_TOKEN,
            ably_channel=BACKEND_PANEL_ABLY_CHANNEL,
            ably_api_key=BACKEND_PANEL_ABLY_API_KEY,
        )
        print("✅ Persona loaded from backend panel:", persona.get("name") or "(no name)")
    except Exception as e:
        persona = None
        print(f"⚠️ Could not load persona from backend: {e}")

print("✅ Gemini client initialized successfully.")
print("💬 Type 'exit', 'q', or 'quit' to end the conversation.\n")

while True:
    try:
        user_prompt = input("🧠 Prompt: ").strip()

        if user_prompt.lower() in ["exit", "q", "quit"]:
            print("👋 Conversation ended.")
            break

        if not user_prompt:
            print("⚠️ Please enter a valid prompt.")
            continue

        # If persona is available, prepend persona instructions to the prompt in a minimal, non-invasive way
        persona_prefix = ""
        if persona:
            parts = []
            if persona.get("name"):
                parts.append(f"Persona name: {persona.get('name')}")
            if persona.get("tone"):
                parts.append(f"Tone: {persona.get('tone')}")
            if persona.get("constraints"):
                parts.append(f"Constraints: {persona.get('constraints')}")
            if parts:
                persona_prefix = " | ".join(parts)

        full_prompt = f"{persona_prefix}\n\n{user_prompt}" if persona_prefix else user_prompt

        print("\n⏳ Generating response...\n")

        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 500,
            },
        )

        if not response or not response.text:
            print("⚠️ The model returned an empty response.")
        else:
            print("🤖 Response:")
            print("--------------------------------------------------")
            print(response.text.strip())
            print("--------------------------------------------------\n")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
        break
    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}\n")
