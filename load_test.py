
import asyncio
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Configuration
NUM_CONCURRENT_USERS = 100
PROMPT = "Tell me a short story."
GEMINI_MODEL_NAME = "gemini-2.5-flash"

async def simulate_user(model, results_queue):
    """Simulates a single user request and measures performance."""
    try:
        start_time = time.time()
        first_token_time = None

        try:
            response_stream = model.generate_content(PROMPT, generation_config={
                "max_output_tokens": 200,
            }, stream=True)

            for chunk in response_stream:
                if first_token_time is None:
                    first_token_time = time.time()
        except StopAsyncIteration:
            print("Warning: StopAsyncIteration caught. The stream was likely empty.")

        end_time = time.time()

        if first_token_time:
            ttft = first_token_time - start_time
            total_latency = end_time - start_time
            await results_queue.put((ttft, total_latency))
        else:
            await results_queue.put((None, None))
    except Exception as e:
        print(f"An error occurred in simulate_user: {e}")
        await results_queue.put((None, None))
        
async def main():
    """Runs the load test with concurrent users."""
    load_dotenv()
    
    results_queue = asyncio.Queue()
    
    print(f"Starting load test with {NUM_CONCURRENT_USERS} concurrent users...")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in .env file")
        import sys
        sys.exit(0)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    tasks = [asyncio.create_task(simulate_user(model, results_queue)) for _ in range(NUM_CONCURRENT_USERS)]
    
    await asyncio.gather(*tasks)

    results = []
    while not results_queue.empty():
        results.append(await results_queue.get())

    valid_results = [res for res in results if res[0] is not None]

    if not valid_results:
        print("No successful requests were made.")
        return

    ttfts = [res[0] for res in valid_results]
    total_latencies = [res[1] for res in valid_results]

    avg_ttft = sum(ttfts) / len(ttfts)
    avg_total_latency = sum(total_latencies) / len(total_latencies)

    print("\n--- Load Test Results ---")
    print(f"Total Requests: {NUM_CONCURRENT_USERS}")
    print(f"Successful Requests: {len(valid_results)}")
    print(f"Average Time to First Token (TTFT): {avg_ttft:.4f} seconds")
    print(f"Average Total Latency: {avg_total_latency:.4f} seconds")
    print("------------------------")

if __name__ == "__main__":
    asyncio.run(main())