# AI Sentinel (A Hybrid-Cloud Prototype)

This is a proof-of-concept for the "Global AI Infrastructure Project," demonstrating a high-reliability, low-cost AI governance layer.

The system is built on a **zero-fund "hybrid-cloud" model**. The "Brain" (a 1GB VM on Azure Free Tier) securely commands a "Brawn" (a local laptop) over a zero-trust network (Tailscale) to run multiple AI models, detect hallucinations, and form a consensus.

## Core Features

*   **Hybrid-Cloud Architecture:** The "Brain" (logic) and "Brawn" (compute) run on separate machines in different locations (public cloud + home).
*   **Zero-Trust Network:** Uses **Tailscale** for a secure, encrypted mTLS tunnel. The cloud VM has *zero* open public ports, making it invisible to the internet.
*   **"Super AI" Consensus:** The Brain queries 3 models (1 real, 2 mock) to detect and reject "hallucinations" (bad answers).
*   **Hardware-Gated Kill Switch:** A `watchdog.py` script monitors system RAM and will terminate the process to prevent a crash from a "bad update" or memory leak.

## Architecture Diagram

This diagram shows the live prototype. The Azure VM (Brain) acts as the router and aggregator, while the Home Laptop (Brawn) acts as the firewalled AI compute node.

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

## How to Run

1.  **Cloud ("Brain"):** `brain_v0.1.py` runs on a 1GB Azure VM.
2.  **Local ("Brawn"):** `ollama serve` runs on a local machine (8GB+ RAM).
3.  **Network:** Both machines are connected via **Tailscale**.

