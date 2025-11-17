import requests
import time
import os
import threading
import psutil
import redis
from collections import Counter
import json
import nltk # Make sure you ran 'pip3 install nltk'

# --- 1. CONFIGURATION ---

# !!! CRITICAL: PASTE YOUR CREDENTIALS HERE !!!
# 1. Your Laptop's Tailscale IP
LAPTOP_IP = "YOUR_LAPTOP_TAILSCALE_IP" # e.g., "100.x.x.x"

# 2. Your Redis.com (AWS) Credentials
REDIS_HOST = "YOUR_REDIS_HOST_ID" # e.g., "redis-12345.aws.ap-south-1.redislabs.com"
REDIS_PORT = "YOUR_REDIS_PORT_ID" # e.g., "12345" (IT IS NOT 6380)
REDIS_PASSWORD = "YOUR_REDIS_PASSWORD"
# !!! END OF CONFIGURATION !!!


# --- Endpoints ---
BRAWN_NODE_URL = f"http://{LAPTOP_IP}:11434"

# --- Models for the "Committee" ---
# Brawn models (Laptop) - This is the one we'll use for both simple/complex for now
CHEAP_MODEL = "tinyllama" 
REAL_MODEL_ON_BRAWN = "phi3:mini" # (We'll use this after your 20GB upgrade)

# Brain models (Mocked)
MOCK_MODELS_ON_BRAIN = ["llama3:8b", "mistral:7b"]

# --- Hardware Watchdog (For the VM) ---
MAX_RAM_PERCENT = 85.0
WATCHDOG_POLL_RATE = 5

# --- COMPLEXITY KEYWORDS ---
# If a prompt contains these, it's "complex"
COMPLEX_KEYWORDS = [
    'analyze', 'compare', 'summarize', 'explain', 'contrast', 
    'report', 'review', 'optim', 'debug', 'code', 'write me a'
]

# --- 2. HARDWARE WATCHDOG (FIXED) ---
def hardware_watchdog():
    """Monitors the VM's RAM."""
    print(f"[Watchdog] MONITORING VM RAM: < {MAX_RAM_PERCENT}%")
    try:
        while True:
            ram_usage = psutil.virtual_memory().percent
            print(f"[Watchdog] Status: VM RAM {ram_usage}%")
            time.sleep(WATCHDOG_POLL_RATE)
    except KeyboardInterrupt:
        pass

# --- 3. REDIS CACHE CONNECTION (FIXED) ---
def get_redis_connection():
    """
    Connects to your Redis.com Cache.
    """
    print(f"Attempting to connect to Redis cache at {REDIS_HOST}:{REDIS_PORT}...")
    
    # We will build the connection string manually.
    # Note: "redis://" (not "rediss://") as free tier doesn't use SSL by default.
    CONNECTION_STRING = f"redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
    
    try:
        # We use from_url, which is the most reliable method
        r = redis.from_url(CONNECTION_STRING, decode_responses=True)
        r.ping()
        print(f"[Cache] SUCCESS: Connected to Redis at {REDIS_HOST}")
        return r
    except Exception as e:
        print(f"!!! FATAL CACHE ERROR: {e}")
        print("    1. Check your REDIS_HOST, REDIS_PORT, and REDIS_PASSWORD.")
        print("    2. Check your Azure VM's 'Outbound port rule' matches the IP and Port.")
        return None

# --- 4. MODEL CALLER ---
def call_ai_model(model_name, prompt):
    """
    This function now ONLY calls the Brawn (laptop) node.
    """
    print(f"[Router] Querying BRAWN Node ({LAPTOP_IP}) for: {model_name}")
    try:
        response = requests.post(
            f"{BRAWN_NODE_URL}/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=30 # 30 second timeout
        )
        response.raise_for_status() # Will raise an error for 500, 404, etc.
        return response.json()['response'].strip()
    except Exception as e:
        print(f"!!! ERROR: BRAWN node offline. {e}")
        return "Error: Brawn Node is offline."

# --- 5. THE NEW "SMART ROUTER" ---
def is_complex_query(prompt):
    """
    This is your new "Smart Router" logic.
    It checks if the prompt is simple or complex.
    """
    print("[Router] Analyzing prompt complexity...")
    prompt_lower = prompt.lower()
    for keyword in COMPLEX_KEYWORDS:
        if keyword in prompt_lower:
            print(f"[Router] COMPLEX query detected (keyword: '{keyword}')")
            return True
            
    print("[Router] SIMPLE query detected.")
    return False

# --- 6. "SUPER AI" (The Consensus Engine) ---
def run_system(prompt, cache_client):
    """
    This is the main "Super AI" function.
    It now includes the Router logic.
    """
    print("="*50)
    print(f"[Super AI] New Prompt Received: '{prompt}'")
    
    # --- CACHE CHECK (Step 1) ---
    cache_key = f"prompt:{prompt}"
    try:
        cached_answer = cache_client.get(cache_key)
        if cached_answer:
            print("[Cache] HIT! Returning answer instantly.")
            print(f"\nFINAL ANSWER (FROM CACHE):\n{cached_answer}")
            print("="*50)
            return
    except Exception as e:
        print(f"[Cache] WARNING: Redis check failed. {e}.")

    print("[Cache] MISS! Proceeding to Smart Router...")
    
    final_answer = ""
    had_an_error = False

    # --- SMART ROUTER LOGIC (Step 2) ---
    if is_complex_query(prompt):
        # --- PATH A: "EXPENSIVE" 3-MODEL CONSENSUS ---
        print("[Super AI] Executing 3-Model Consensus...")
        responses = {}
        
        # --- (THIS SECTION IS FOR AFTER YOUR 20GB RAM UPGRADE) ---
        # --- (For now, it calls 1 real + 2 mocks) ---
        
        # 1. Call the real "cheap" model
        responses[CHEAP_MODEL] = call_ai_model(CHEAP_MODEL, prompt)
        
        # 2. Call the mock models
        for model in MOCK_MODELS_ON_BRAIN:
            print(f"[Router] Simulating MOCK request on BRAIN for: {model}")
            responses[model] = f"Mock response from {model} for a complex query."
        
        if "Error:" in responses[CHEAP_MODEL]: had_an_error = True

        print("\n[Super AI] --- VOTES RECEIVED ---")
        for model, resp in responses.items(): print(f"  > {model}: {resp[:75]}...") 

        # --- Consensus Logic ---
        vote_counts = Counter(responses.values())
        most_common_answer, count = vote_counts.most_common(1)[0]
        
        print("\n[Super AI] --- RESOLUTION ---")
        if count > (len(responses) / 2):
            print(f"[Super AI] Consensus Reached (Vote: {count}/{len(responses)})")
            final_answer = most_common_answer
            print(f"\nFINAL VERIFIED ANSWER:\n{final_answer}")
        else:
            print(f"[Super AI] CONFLICT DETECTED: No clear majority.")
            final_answer = responses[CHEAP_MODEL] # Default to cheapest real model
            print(f"\nFINAL ANSWER (UNVERIFIED):\n{final_answer}")
        
    else:
        # --- PATH B: "CHEAP" SINGLE-MODEL QUERY ---
        print("[Super AI] Executing Cheap Path (1 model)...")
        final_answer = call_ai_model(CHEAP_MODEL, prompt)
        if "Error:" in final_answer: had_an_error = True
        print(f"\nFINAL ANSWER (Simple):\n{final_answer}")

    
    # --- SAVE TO CACHE (Step 3) ---
    if not had_an_error:
        try:
            cache_client.set(cache_key, final_answer, ex=3600) # Save for 1 hour
            print("[Cache] SUCCESS: Saved new answer to cache.")
        except Exception as e:
            print(f"[Cache] WARNING: Could not write to cache. {e}")
    else:
        print("[Cache] SKIPPING: An error occurred, will not save to cache.")
        
    print("="*50)

# --- 7. MAIN EXECUTION ---
if __name__ == "__main__":
    if "YOUR_TAILSCALE_IP_HERE" in LAPTOP_IP or "PASTE_YOUR_PUBLIC_ENDPOINT_HERE" in REDIS_HOST:
        print("="*50)
        print("!!! FATAL ERROR: SCRIPT NOT CONFIGURED !!!")
        print("    Please edit the script and fill in your")
        print("    LAPTOP_IP, REDIS_HOST, REDIS_PORT, and REDIS_PASSWORD.")
        print("="*50)
        exit()

    print("Checking dependencies... (psutil, requests, redis, nltk)")
    
    # Download the NLTK data (only need to do this once)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK 'punkt' data... (one-time setup)")
        nltk.download('punkt', quiet=True)

    watchdog = threading.Thread(target=hardware_watchdog, daemon=True)
    watchdog.start()
    cache_client = get_redis_connection()
    
    if cache_client:
        try:
            # --- TEST 1: The "Simple" Prompt ---
            run_system("What is 2+2?", cache_client)
            time.sleep(1)
            
            # --- TEST 2: The "Complex" Prompt ---
            run_system("Please analyze the pros and cons of this project.", cache_client)
            time.sleep(1)
            
            # --- TEST 3: The "Cache" Test ---
            print("\n--- RUNNING SIMPLE PROMPT AGAIN TO TEST CACHE ---")
            run_system("What is 2+2?", cache_client)

        except KeyboardInterrupt:
            print("\n[System] User requested shutdown...")
    else:
        print("[System] Shutting down due to cache connection failure.")
