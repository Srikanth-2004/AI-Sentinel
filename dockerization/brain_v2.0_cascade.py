import requests
import time
import os
import threading
import psutil
import redis
import nltk
import concurrent.futures

# --- 1. CONFIGURATION ---

# Read from Environment Variables (Best Practice for Docker)
LAPTOP_IP = os.getenv("LAPTOP_IP", "100.110.15.96") 
REDIS_HOST = os.getenv("REDIS_HOST", "")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# Fallback check
if not REDIS_HOST or not REDIS_PASSWORD:
    print("!!! WARNING: REDIS_HOST or REDIS_PASSWORD not set in environment variables.")

BRAWN_NODE_URL = f"http://{LAPTOP_IP}:11434"

# --- Models sorted by Role ---
MODEL_SCOUT = "tinyllama"      # Fast, dumb (3 seconds)
MODEL_EXPERT = "llama3:8b"     # Smart, slow (40-60 seconds)
MODEL_JUDGE = "mistral:7b"     # Tie-breaker (Only if needed)

# --- Hardware Watchdog ---
MAX_RAM_PERCENT = 85.0
WATCHDOG_POLL_RATE = 5

# --- 2. WATCHDOG ---
def hardware_watchdog():
    try:
        while True:
            time.sleep(WATCHDOG_POLL_RATE)
    except KeyboardInterrupt: pass

# --- 3. REDIS CONNECTION ---
def get_redis_connection():
    print(f"Connecting to Redis at {REDIS_HOST}...")
    # Construct connection string
    # Handle cases where port is a string
    CONNECTION_STRING = f"redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
    try:
        r = redis.from_url(CONNECTION_STRING, decode_responses=True)
        r.ping()
        return r
    except Exception as e:
        print(f"!!! CACHE ERROR: {e}")
        return None

# --- 4. MODEL CALLER ---
def call_ai_model(model_name, prompt):
    print(f"[Router] Calling '{model_name}' from Brawn...")
    start_time = time.time()
    try:
        response = requests.post(
            f"{BRAWN_NODE_URL}/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=300 # 5 min timeout for heavy models
        )
        response.raise_for_status() 
        duration = time.time() - start_time
        print(f"[Router] '{model_name}' finished in {duration:.2f}s.")
        return response.json()['response'].strip()
    except Exception as e:
        print(f"!!! ERROR: '{model_name}' failed. {e}")
        return "Error"

# --- 5. CASCADE LOGIC (The New Brain) ---
def run_system(prompt, cache_client):
    print("="*50)
    print(f"[Super AI] Prompt: '{prompt}'")
    
    # 1. Cache Check
    cache_key = f"prompt:{prompt}"
    if cache_client:
        try:
            cached = cache_client.get(cache_key)
            if cached:
                print("[Cache] HIT! Returning instantly.")
                print(f"\nFINAL ANSWER:\n{cached}\n{'='*50}")
                return
        except Exception as e:
            print(f"[Cache] Read Error: {e}")

    print("[Cache] MISS. Starting Cascade...")
    final_answer = ""

    # --- STAGE 1: THE SCOUT (Fastest) ---
    print("\n--- STAGE 1: SCOUT (tinyllama) ---")
    ans_scout = call_ai_model(MODEL_SCOUT, prompt)
    
    # Simple Heuristic: If it's a short/simple answer, we trust it.
    if len(ans_scout) < 150 and "Error" not in ans_scout: 
        print("[Router] Scout answer is simple and valid. Early Exit.")
        final_answer = ans_scout

    else:
        # --- STAGE 2: THE EXPERT (Heavy) ---
        print("\n--- STAGE 2: EXPERT (llama3) ---")
        print("[Router] Query is complex. Escalating to Llama-3...")
        ans_expert = call_ai_model(MODEL_EXPERT, prompt)
        
        if "Error" in ans_expert:
            print("[Router] Expert failed. Falling back to Scout.")
            final_answer = ans_scout
        else:
            print("[Router] Expert finished. Overriding Scout.")
            final_answer = ans_expert

    print(f"\nFINAL VERIFIED ANSWER:\n{final_answer}")

    # Save to Cache
    if cache_client and "Error" not in final_answer:
        try:
            cache_client.set(cache_key, final_answer, ex=3600)
            print("[Cache] Saved.")
        except Exception as e:
            print(f"[Cache] Write Error: {e}")
    
    print("="*50)

if __name__ == "__main__":
    # NLTK setup
    try: nltk.data.find('tokenizers/punkt')
    except LookupError: nltk.download('punkt', quiet=True)
    
    watchdog = threading.Thread(target=hardware_watchdog, daemon=True)
    watchdog.start()
    cache_client = get_redis_connection()
    
    if cache_client:
        print("\n=== AI CONSENSUS ENGINE READY ===")
        print("Type 'exit' to quit.\n")
        
        while True:
            try:
                # Get input from you (the user)
                user_prompt = input("\n[You]: ")
                
                if user_prompt.lower() in ['exit', 'quit']:
                    print("[System] Shutting down...")
                    break
                
                if not user_prompt.strip():
                    continue

                # Run your system with the user's prompt
                run_system(user_prompt, cache_client)
                
            except KeyboardInterrupt:    
                print("\n[System] Interrupted. Exiting...")
                break
            except Exception as e:
                print(f"[System] Error: {e}")
    else:
        print("[System] Shutting down due to cache connection failure.")