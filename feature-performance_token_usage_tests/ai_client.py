import os
import time
import csv
import google.generativeai as genai
from dotenv import load_dotenv

# -----------------------------#
#  1️⃣ Environment & Model Setup
# -----------------------------#

print("🔍 Loading .env file...")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("🚨 ERROR: OPENAI_API_KEY is missing or invalid.")
    exit()

genai.configure(api_key=api_key)

# ✅ Directly use a fixed model
MODEL_NAME = "models/gemini-2.5-flash"
print(f"✅ Using fixed model: {MODEL_NAME}\n")
model = genai.GenerativeModel(MODEL_NAME)

# -----------------------------#
#  2️⃣ Test Variables
# -----------------------------#
total_requests = 0
total_latency = 0.0
total_prompt_tokens = 0
total_output_tokens = 0
total_tokens = 0
csv_file = "performance_results.csv"

# Create CSV headers
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Prompt", "Response Time (s)", "Prompt Tokens", "Output Tokens", "Total Tokens"])

print("💬 Type 'exit', 'q', or 'quit' to end the test.\n")

# -----------------------------#
#  3️⃣ Main Loop
# -----------------------------#
while True:
    try:
        user_prompt = input("🧠 Prompt: ").strip()
        if user_prompt.lower() in ["exit", "q", "quit"]:
            print("👋 Test stopped.")
            break
        if not user_prompt:
            print("⚠️ Please enter a valid prompt.")
            continue

        start_time = time.time()
        print("\n⏳ Generating response...\n")

        # 🔹 Model call
        response = model.generate_content(
            user_prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 550,
            },
        )

        elapsed_time = time.time() - start_time

        # 🔹 Token usage info
        usage = getattr(response, "usage_metadata", None)
        if usage:
            prompt_tokens = getattr(usage, "prompt_token_count", 0)
            output_tokens = getattr(usage, "candidates_token_count", 0)
            total_token = getattr(usage, "total_token_count", 0)
        else:
            prompt_tokens = output_tokens = total_token = 0

        # 🔹 Update stats
        total_requests += 1
        total_latency += elapsed_time
        total_prompt_tokens += prompt_tokens
        total_output_tokens += output_tokens
        total_tokens += total_token

        # 🔹 Write to CSV
        with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([user_prompt, round(elapsed_time, 2), prompt_tokens, output_tokens, total_token])

        # 🔹 Display response
        print("🤖 Response:")
        print("--------------------------------------------------")

        try:
            if not response.candidates:
                print("⚠️ No candidates returned by the model.")
            else:
                candidate = response.candidates[0]

                # Handle finish_reason explanations
                finish_reason = getattr(candidate, "finish_reason", None)
                if finish_reason == 2:
                    print("⚠️ Response stopped due to safety filter (finish_reason = SAFETY).")
                elif not hasattr(candidate, "content") or not getattr(candidate.content, "parts", []):
                    print("⚠️ Model returned empty content.")
                else:
                    text = candidate.content.parts[0].text.strip()
                    print(text if text else "⚠️ Empty response text.")

        except Exception as e:
            print(f"❌ Error reading response: {e}")

        print("--------------------------------------------------")
        print(f"⏱️ Response time: {elapsed_time:.2f} sec")
        print(f"🔢 Token usage: {total_token} (Prompt: {prompt_tokens}, Output: {output_tokens})\n")

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted.")
        break
    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}\n")

# -----------------------------#
#  4️⃣ Test Summary
# -----------------------------#
if total_requests > 0:
    avg_latency = total_latency / total_requests
    avg_prompt_tokens = total_prompt_tokens / total_requests
    avg_output_tokens = total_output_tokens / total_requests
    avg_total_tokens = total_tokens / total_requests

    print("\n📊 Test Summary")
    print("--------------------------------------------------")
    print(f"Total requests: {total_requests}")
    print(f"Average latency: {avg_latency:.2f} s")
    print(f"Average prompt tokens: {avg_prompt_tokens:.2f}")
    print(f"Average output tokens: {avg_output_tokens:.2f}")
    print(f"Average total tokens: {avg_total_tokens:.2f}")
    print("--------------------------------------------------")
    print(f"📁 Results saved to: {csv_file}")