# AI Sentinel (A Hybrid-Cloud Prototype)

## **Status:** Phase 1 (Complete)

This is a proof-of-concept for the "Global AI Infrastructure Project," demonstrating a high-reliability, low-cost AI governance layer.

The system is designed to solve two core problems:

1.  **AI Hallucinations:** It cross-references answers from a committee of AI models to find a verifiable consensus, rejecting "bad" answers.
2.  **High Compute Cost:** It uses a hybrid-cloud model, running a fast, local "Brawn" node (on a laptop) and a lightweight "Brain" node (on a free Azure VM) to manage logic and caching.

The system is built on a **zero-fund "hybrid-cloud" model**. The "Brain" (a 1GB VM on Azure Free Tier) securely commands a "Brawn" (a local laptop) over a zero-trust network (Tailscale) to run multiple AI models, detect hallucinations, and form a consensus.

---
## Core Features

*   **Hybrid-Cloud Architecture:** The "Brain" (logic) and "Brawn" (compute) run on separate machines in different locations (public cloud + home).
*   **Zero-Trust Network:** Uses **Tailscale** for a secure, encrypted mTLS tunnel. The cloud VM has *zero* open public ports, making it invisible to the internet.
*   **"Super AI" Consensus:** The Brain queries 3 models (1 real, 2 mock) to detect and reject "hallucinations" (bad answers).
*   **Hardware-Gated Kill Switch:** A `watchdog.py` script monitors system RAM and will terminate the process to prevent a crash from a "bad update" or memory leak.

---

## Architecture Diagram

This diagram shows the live prototype. The Azure VM (Brain) acts as the router and aggregator, while the Home Laptop (Brawn) acts as the firewalled AI compute node.

### Phase 1:
<img width="612" height="797" alt="AI Sentinel (Request Flow)" src="https://github.com/user-attachments/assets/a164ab23-6adf-412a-9c8b-b3a6b9d62ba2" />

### Phase 2:
<img width="916" height="1084" alt="AI Sentinel (Phase 2)" src="https://github.com/user-attachments/assets/d797d47f-5dd6-4415-8c0f-47425225cce8" />

## Live Demo Output

This log shows the system successfully running on an 8GB laptop and a 1GB Azure VM.

### Test 1: Hallucination Detected & Rejected

```

\[Super AI\] New Prompt Received: 'What is the color of the sky?'
\[Super AI\] Querying model committee...
\[Router\] Querying BRAWN Node (100.x.x.x) for: phi3:mini
\[Router\] Simulating MOCK request on BRAIN for: llama3:8b
\[Router\] Simulating MOCK request on BRAIN for: mistral:7b

\[Super AI\] --- VOTES RECEIVED ---

> phi3:mini: The sky is blue.
> llama3:8b: The sky is green due to atmospheric composition.
> mistral:7b: The sky is blue.

\[Super AI\] --- RESOLUTION ---
\[Super AI\] Consensus Reached (Vote: 2/3)

FINAL VERIFIED ANSWER:
The sky is blue.

``` 

### Test 2: Conflict Detected & Handled

```

\[Super AI\] New Prompt Received: 'Write a 3-day travel plan for Tokyo.'
\[Super AI\] Querying model committee...
\[Router\] Querying BRAWN Node (100.x.x.x) for: phi3:mini
\[Router\] Simulating MOCK request on BRAIN for: llama3:8b
\[Router\] Simulating MOCK request on BRAIN for: mistral:7b

\[Super AI\] --- VOTES RECEIVED ---

> phi3:mini: (A mock response for a Tokyo plan)
> llama3:8b: (A different mock response)
> mistral:7b: (A third different mock response)

\[Super AI\] --- RESOLUTION ---
\[Super AI\] CONFLICT DETECTED: No clear majority.
\[Super AI\] Defaulting to primary node (phi3:mini).

FINAL ANSWER (UNVERIFIED):
(A mock response for a Tokyo plan)

``` 
---
## How to Run

1.  **Cloud ("Brain"):** `brain_v0.1.py` runs on a 1GB Azure VM.
2.  **Local ("Brawn"):** `ollama serve` runs on a local machine (8GB+ RAM).
3.  **Network:** Both machines are connected via **Tailscale**.

---

## **Status:** Phase 2 (Working Prototype) Complete

## Core Architecture (Phase 2)

This system runs a "Brain" (the logic) in the cloud, which commands a "Brawn" (the AI model) running on a local machine. An L1 cache (Redis) is used to store common answers and reduce latency.

## Demo Log (SUCCESS!)

This log shows the system in action.

1.  **Run 1 (Cache MISS):** The system queries the Brawn node, detects a 3-way conflict, and saves the final answer to the cache.
2.  **Run 2 (Cache HIT):** The system retrieves the answer instantly from the L1 Cache, skipping the AI models entirely.

````

Checking dependencies... (psutil, requests, redis)
\[Watchdog\] MONITORING VM RAM: \< 85.0%
\[Watchdog\] Status: VM RAM 48.5%
\[Cache\] SUCCESS: Connected to Redis at ai-brain-vm-01.redis.cache.windows.net

# \--- FIRST RUN (Should be SLOW and say 'MISS') ---

\[Super AI\] New Prompt Received: 'What is the color of the sky?'
\[Cache\] MISS\! Running full consensus check...
\[Super AI\] Querying model committee...
\[Router\] Querying BRAWN Node (100.66.2.112) for: tinyllama
\[Watchdog\] Status: VM RAM 48.5%
\[Router\] Simulating MOCK request on BRAIN for: llama3:8b
\[Router\] Simulating MOCK request on BRAIN for: mistral:7b

\[Super AI\] --- VOTES RECEIVED ---

> tinyllama: The answer depends on your location and time of day...
> llama3:8b: The sky is green....
> mistral:7b: The sky is blue....

\[Super AI\] --- RESOLUTION ---
\[Super AI\] CONFLICT DETECTED: No clear majority.

# FINAL ANSWER (UNVERIFIED): The answer depends on your location and time of day... \[Cache\] SUCCESS: Saved new answer to cache.

# \--- SECOND RUN (Should be FAST and say 'HIT') ---

\[Super AI\] New Prompt Received: 'What is the color of the sky?'
\[Cache\] HIT\! Returning answer instantly.

# FINAL VERIFIED ANSWER (FROM CACHE): The answer depends on your location and time of day...

````
---

## How It Works

*   **Brain (Azure VM Standard\_B1s):** Runs the main `brain_v0.3_cache.py` script. This lightweight server handles API requests, consensus logic, and the cache connection. It runs on a free Azure for Students account.
*   **Brawn (Local Laptop):** Runs `ollama serve` to provide AI compute. This node is "dumb" and simply processes AI requests sent to it.
*   **Network (Tailscale):** A zero-trust mesh network that creates a secure, encrypted mTLS tunnel between the Azure VM and the local laptop, allowing them to communicate privately without opening public firewall ports.
*   **Cache (Azure Cache for Redis):** A free-tier Redis instance (30MB) that acts as an L1 cache to store results from the consensus engine, reducing cost and latency on repeat queries.

---

## Roadmap / Next Steps

*   **[ ] Phase 3: Go "Mock-Free" (Hardware)**
    *   Install RAM upgrade on the "Brawn" node (laptop).
    *   Pull full-size models (`llama3:8b`, `mistral:7b`) to the Brawn node.
    *   Update `brain_v0.3_cache.py` to make 3 *real* API calls to the Brawn node, removing all mock logic.
*   **[ ] Phase 4: Build the "Smart Router" (Logic)**
    *   Implement a lightweight classifier (e.g., DistilBERT) on the "Brain" VM.
    *   This router will analyze the prompt's complexity *before* running the consensus.
    *   **Simple prompts** (e.g., "What is 2+2?") will only be sent to `tinyllama` (fast, cheap).
    *   **Complex prompts** (e.g., "Analyze this report...") will trigger the full 3-model consensus (slow, expensive).
