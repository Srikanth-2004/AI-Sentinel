import redis

# --- 1. CONFIGURATION ---
# PASTE YOUR AZURE REDIS CREDENTIALS HERE
REDIS_HOST = "PASTE_YOUR_HOST_NAME_HERE"
REDIS_PORT = 6380
REDIS_PASSWORD = "PASTE_YOUR_ACCESS_KEY_HERE"
# --- END OF CONFIGURATION ---

print(f"Connecting to cache at {REDIS_HOST}...")

try:
    CONNECTION_STRING = f"rediss://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
    r = redis.from_url(CONNECTION_STRING, decode_responses=True)
    r.ping()
    print("[Cache] SUCCESS: Connected.")
    
    # --- THIS IS THE COMMAND THAT CLEARS EVERYTHING ---
    r.flushdb()
    
    print("✅✅✅ SUCCESS: Your cache has been cleared. ✅✅✅")
    print("The old 'Error: Brawn Node is offline' message is gone.")
    print("You can now run the main 'brain_v0.3_cache.py' script.")

except Exception as e:
    print(f"!!! FATAL CACHE ERROR: {e}")