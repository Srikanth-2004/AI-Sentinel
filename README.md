# AI Sentinel (A Hybrid-Cloud Prototype)

**Status:** Phase 4 (Smart Router Prototype) Complete

This is a proof-of-concept for the "Global AI Infrastructure Project," demonstrating a high-reliability, low-cost AI governance layer.

The system is built on a **zero-fund, multi-cloud model** and is designed to solve two core problems:

- **High Compute Cost:** A "Smart Router" analyzes prompt complexity. Simple prompts are routed to a single, fast model, while complex prompts are escalated to a full consensus check.
- **AI Hallucinations:** The system cross-references answers from a committee of AI models to find a verifiable consensus, rejecting "bad" answers.

## Core Features

- **Hybrid-Cloud Architecture:** The "Brain" (logic) runs on a 1GB Azure VM, and the "Brawn" (AI compute) runs on a local 8GB laptop.
- **Multi-Cloud Caching:** Uses a free **Redis.com (AWS-hosted)** L1 Cache. The Brain (Azure) and Cache (AWS) operate in different clouds but in the same geographic region (India) for low latency.
- **Zero-Trust Network:** Uses **Tailscale** for a secure, encrypted mTLS tunnel. The cloud VM has _zero_ open public ports, making it invisible to the internet.
- **"Super AI" Consensus:** The Brain queries multiple models (1 real, 2 mock) to detect and reject "hallucinations."
- **"Smart Router" (v0.5):** Analyzes prompts for keywords (analyze, compare, summarize) to decide whether to use the "cheap path" (1 model) or "expensive path" (3 models).

## Architecture Diagram (Phase 4)

This diagram shows the final, working logic flow. The "Smart Router" is the new entry point after a cache miss.

<img width="912" height="1233" alt="AI Sentinel (Phase 4)" src="https://github.com/user-attachments/assets/e1845eed-6f2a-46b9-83ac-074f126657e1" />


## Live Demo Log (SUCCESS!)

This log shows the complete system successfully routing two different prompts.

Test 1: Simple Prompt ("What is 2+2?")

The "Smart Router" detects a simple prompt and routes it to the "Cheap Path" (1 model).

\[Super AI\] New Prompt Received: 'What is 2+2?'  
\[Cache\] MISS! Proceeding to Smart Router...  
\[Router\] Analyzing prompt complexity...  
\[Router\] SIMPLE query detected.  
\[Super AI\] Executing Cheap Path (1 model)...  
\[Router\] Querying BRAWN Node (100.66.2.112) for: tinyllama  
<br/>FINAL ANSWER (Simple):  
Yes, I can provide you with the answer to your question: 2 + 2 = 4.  
\[Cache\] SUCCESS: Saved new answer to cache.  

Test 2: Complex Prompt ("analyze...")

The "Smart Router" detects a complex prompt ("analyze") and escalates to the full 3-model consensus.

\[Super AI\] New Prompt Received: 'Please analyze the pros and cons of this project.'  
\[Cache\] MISS! Proceeding to Smart Router...  
\[Router\] Analyzing prompt complexity...  
\[Router\] COMPLEX query detected (keyword: 'analyze')  
\[Super AI\] Executing 3-Model Consensus...  
\[Router\] Querying BRAWN Node (100.66.2.112) for: tinyllama  
\[Router\] Simulating MOCK request on BRAIN for: llama3:8b  
\[Router\] Simulating MOCK request on BRAIN for: mistral:7b  
<br/>\[Super AI\] --- VOTES RECEIVED ---  
\> tinyllama: Analysis: Pros and Cons of this Project...  
\> llama3:8b: Mock response from llama3:8b for a complex query....  
\> mistral:7b: Mock response from mistral:7b for a complex query....  
<br/>\[Super AI\] --- RESOLUTION ---  
\[Super AI\] CONFLICT DETECTED: No clear majority.  
FINAL ANSWER (UNVERIFIED):  
Analysis: Pros and Cons of this Project...  
\[Cache\] SUCCESS: Saved new answer to cache.  

Test 3: Cache Test (Fast Path)

The system correctly pulls the answer for "2+2?" from the cache, skipping all AI models.

\--- RUNNING SIMPLE PROMPT AGAIN TO TEST CACHE ---  
\[Super AI\] New Prompt Received: 'What is 2+2?'  
\[Cache\] HIT! Returning answer instantly.  
<br/>FINAL ANSWER (FROM CACHE):  
Yes, I can provide you with the answer to your question: 2 + 2 = 4.  

## How It Works

- **Brain (Azure VM Standard_B1s):** Runs the main brain_v0.5_cache_fix.py script. This lightweight server handles API requests, smart routing, consensus logic, and the cache connection. Runs on a free Azure for Students account.
- **Brawn (Local Laptop):** Runs ollama serve --host 0.0.0.0 to provide AI compute. This node is "dumb" and simply processes AI requests sent to it. Currently runs tinyllama due to 8GB RAM limit.
- **Network (Tailscale):** A zero-trust mesh network that creates a secure, encrypted mTLS tunnel between the Azure VM and the local laptop.
- **Cache (Redis.com on AWS):** A free-tier 30MB Redis instance (on AWS, ap-south-1) acts as an L1 cache to store results, reducing cost and latency. This makes the architecture **multi-cloud** (Azure + AWS).

## Roadmap / Next Steps

- **\[ \] Phase 5: Go "Mock-Free" (Hardware)**
  - Install **20GB RAM** upgrade on the "Brawn" node (laptop) after the Black Friday sale.
  - Pull full-size models (llama3:8b, mistral:7b) to the Brawn node.
  - Update brain_v0.5_cache_fix.py to make 3 _real_ API calls to the Brawn node, removing all mock logic.
