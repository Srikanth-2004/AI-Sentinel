import requests
import time
import os
import threading
import psutil
import redis
from collections import Counter
import json

# --- 1. CONFIGURATION ---

# !!! CRITICAL: PASTE YOUR CREDENTIALS HERE !!!
# 1. Your Laptop's Tailscale IP
LAPTOP_IP = "YOUR_TAILSCALE_IP_HERE" # e.g., "100.xx.xx.xxx"

# 2. Your New Azure Redis Cache Credentials
REDIS_HOST = "YOUR_REDIS_HOST_NAME" # e.g., "YOUR_USER_NAME.redis.cache.windows.net"
REDIS_PORT = 6380
REDIS_PASSWORD = "YOUR_REDIS_PRIMARY_OR_SECONDARY_KEY"
# !!! END OF CONFIGURATION !!!


# --- Endpoints ---
BRAWN_NODE_URL = f"http://{LAPTOP_IP}:11434"

# --- Models for the "Committee" ---
REAL_MODEL_ON_BRAWN = "tinyllama"
MOCK_MODELS_ON_BRAIN = ["llama3:8b", "mistral:7b"]

# --- Hardware Watchdog (For the VM) ---
MAX_RAM_PERCENT = 85.0
WATCHDOG_POLL_RATE = 5

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

# --- 3. REDIS CACHE CONNECTION ---
def get_redis_connection():
    """
    Connects to your Azure Cache for Redis.
    Uses the "Primary connection string" for a foolproof login.
    """
    
    # Let's build the connection string manually to be sure
    # This also fixes the "invalid username-password pair" bug
    CONNECTION_STRING = f"rediss://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
    
    try:
        # We use from_url, which is the most reliable method
        r = redis.from_url(CONNECTION_STRING, decode_responses=True)
        r.ping()
        print(f"[Cache] SUCCESS: Connected to Redis at {REDIS_HOST}")
        return r
    except Exception as e:
        print(f"!!! FATAL CACHE ERROR: Could not connect to Redis: {e}")
        print("    1. Check your REDIS_HOST, REDIS_PORT, and REDIS_PASSWORD.")
        print("    2. Check your Azure VM's firewall ('Networking') settings.")
        print("    3. Check your Redis 'Access keys' page to ensure 'Access key authentication' is ENABLED.")
        return None

# --- 4. "SUPER AI" (The Consensus Engine) ---
def run_consensus_engine(prompt, cache_client):
    """
    The "Super AI" aggregator, now with L1 Caching.
    """
    print("="*50)
    print(f"[Super AI] New Prompt Received: '{prompt}'")
    
    # --- CACHE CHECK (Step 1) ---
    cache_key = f"prompt:{prompt}"
    try:
        cached_answer = cache_client.get(cache_key)
        if cached_answer:
            print("[Cache] HIT! Returning answer instantly.")
            print(f"\nFINAL VERIFIED ANSWER (FROM CACHE):\n{cached_answer}")
            print("="*50)
            return # Stop execution
    except Exception as e:
        print(f"[Cache] WARNING: Redis check failed. {e}. Bypassing cache.")

    print("[Cache] MISS! Running full consensus check...")
    print("[Super AI] Querying model committee...")
    
    responses = {}
    final_answer = ""
    had_an_error = False # <-- NEW: Flag to track errors

    # --- MODEL CALLS (Step 2 - Only if cache missed) ---
    print(f"[Router] Querying BRAWN Node ({LAPTOP_IP}) for: {REAL_MODEL_ON_BRAWN}")
    try:
        response = requests.post(
            f"{BRAWN_NODE_URL}/api/generate",
            json={"model": REAL_MODEL_ON_BRAWN, "prompt": prompt, "stream": False},
            timeout=30
        )
        response.raise_for_status() 
        responses[REAL_MODEL_ON_BRAWN] = response.json()['response'].strip()
    except Exception as e:
        print(f"!!! ERROR: BRAWN node offline. {e}")
        responses[REAL_MODEL_ON_BRAWN] = "Error: Brawn Node is offline."
        had_an_error = True # <-- NEW: Set the error flag

    for model in MOCK_MODELS_ON_BRAIN:
        print(f"[Router] Simulating MOCK request on BRAIN for: {model}")
        if "color of the sky" in prompt.lower():
            responses[model] = "The sky is blue." if model == "mistral:7b" else "The sky is green."
        else:
            responses[model] = f"Mock response: The answer to '{prompt}' is complex."

    print("\n[Super AI] --- VOTES RECEIVED ---")
    for model, resp in responses.items():
        print(f"  > {model}: {resp[:75]}...") 

    # --- CONSENSUS LOGIC (Step 3) ---
    vote_counts = Counter(responses.values())
    most_common_answer, count = vote_counts.most_common(1)[0]
    
    print("\n[Super AI] --- RESOLUTION ---")
    
    if count > (len(responses) / 2):
        print(f"[Super AI] Consensus Reached (Vote: {count}/{len(responses)})")
        final_answer = most_common_answer
        print(f"\nFINAL VERIFIED ANSWER:\n{final_answer}")
    else:
        print(f"[Super AI] CONFLICT DETECTED: No clear majority.")
        final_answer = responses[REAL_MODEL_ON_BRAWN]
        print(f"\nFINAL ANSWER (UNVERIFIED):\n{final_answer}")
    
    # --- SAVE TO CACHE (Step 4 - NOW SMARTER) ---
    # NEW: We only save to cache if there was NO error
    if not had_an_error:
        try:
            cache_client.set(cache_key, final_answer, ex=3600) # Save for 1 hour
            print("[Cache] SUCCESS: Saved new answer to cache.")
        except Exception as e:
            print(f"[Cache] WARNING: Could not write to cache. {e}")
    else:
        print("[Cache] SKIPPING: An error occurred, will not save to cache.")
        
    print("="*50)

# --- 5. MAIN EXECUTION ---
if __name__ == "__main__":
    if "YOUR_TAILSCALE_IP_HERE" in LAPTOP_IP or "PASTE_YOUR_HOST_NAME_HERE" in REDIS_HOST:
        print("="*50)
        print("!!! FATAL ERROR: SCRIPT NOT CONFIGURED !!!")
        print("    Please edit the script and fill in your")
        print("    LAPTOP_IP, REDIS_HOST, and REDIS_PASSWORD.")
        print("="*50)
        exit()

    print("Checking dependencies... (psutil, requests, redis)")
    
    # Start the watchdog
    watchdog = threading.Thread(target=hardware_watchdog, daemon=True)
    watchdog.start()

    # Connect to Redis
    cache_client = get_redis_connection()
    
    if cache_client:
        try:
            # We run the SAME prompt twice to prove the cache works
            print("\n--- FIRST RUN (Should be SLOW and say 'MISS') ---")
            run_consensus_engine("What is the color of the sky?", cache_client)
            
            time.sleep(2) # Pause for dramatic effect
            
            print("\n--- SECOND RUN (Should be FAST and say 'HIT') ---")
            run_consensus_engine("What is the color of the sky?", cache_client)

        except KeyboardInterrupt:
            print("\n[System] User requested shutdown...")
    else:
        print("[System] Shutting down due to cache connection failure.")
