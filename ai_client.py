import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or "dummy" in api_key.lower():
    print("🚨 ERROR: OPENAI_API_KEY is missing or invalid.")
    exit()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

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

        print("\n⏳ Generating response...\n")

        response = model.generate_content(
            user_prompt,
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
