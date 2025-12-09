# **AI Sentinel (A Hybrid-Cloud Prototype)**

**Status:** Phase 6 (Parallel & Cascading Consensus) Complete

AI Sentinel is a proof-of-concept for a high-reliability, low-cost "Super AI" infrastructure. It solves two critical problems in modern AI deployment: **Hallucinations** (AI making things up) and **High Cloud Costs**.

By combining a **"Brain" in the cloud** with a **"Brawn" node on a local laptop**, this system delivers enterprise-grade reliability on a student budget.

## **🚀 Key Features**

### **1. The "Super AI" Consensus Engine**

Instead of trusting a single AI model, AI Sentinel queries a **committee of 3 models** simultaneously:

* **TinyLlama:** The fast, lightweight "Scout."  
* **Llama-3:** The intelligent "Expert."  
* **Mistral:** The tie-breaking "Judge."  
  By cross-referencing their answers, the system detects and rejects hallucinations.

### **2. The Smart Router (Cost Control)**

Not every question needs a supercomputer.

* **Simple Question?** ("What is 2+2?") \-\> Routed to the cheap, fast model.  
* **Complex Question?** ("Analyze this geopolitical trend...") \-\> Escalated to the full 3-model consensus engine.  
* **Result:** Saves 90% of compute costs and time.

### **3. Hybrid-Cloud Architecture**

* **The Brain (Azure Cloud):** Handles the logic, routing, and caching. It's lightweight and free.  
* **The Brawn (Local Laptop):** Handles the heavy AI processing using your own GPU/RAM.  
* **The Network (Tailscale):** Connects them securely via an encrypted, zero-trust tunnel. No open ports, no security risks.

### **4. Multi-Cloud Caching**

Uses a **Redis Cache hosted on AWS** to store verified answers. If you ask the same question twice, the answer is returned instantly (\<50ms), bypassing the AI models entirely.

## **🏗️ Architecture Diagram**

<img width="1897" height="619" alt="image" src="https://github.com/user-attachments/assets/a46e593a-272f-4288-8e3a-c1764d2bd530" />


## **🛠️ How to Run AI Sentinel**

You can run this system in two ways: the **Standard Method** (great for development) or the **Docker Method** (great for deployment).

### **Prerequisites (For Both Methods)**

1. **Tailscale:** Installed and connected on both your Laptop and Azure VM.  
2. **Ollama:** Installed on your Laptop ("Brawn Node") with models pulled (tinyllama, llama3:8b, mistral:7b).  
3. **Redis:** A running Redis instance (e.g., free tier on Redis.com).

### **Option 1: Standard Method (Python Script)**

**1. Configure the Brawn Node (Laptop)**  
Open your terminal and start Ollama, ensuring it listens to the network:  
```
\# Linux/macOS  
export OLLAMA_HOST=0.0.0.0  
ollama serve
```

```
\# Windows PowerShell  
$env:OLLAMA_HOST="0.0.0.0"  
ollama serve
```

**2. Configure the Brain Node (Azure VM)**  
SSH into your VM and set your environment variables (or edit the script directly):  
```
export LAPTOP_IP="100.x.x.x"  \# Your Laptop's Tailscale IP  
export REDIS_HOST="your-redis-endpoint"  
export REDIS_PORT="12345"  
export REDIS_PASSWORD="your-password"
```

**3. Run the Sentinel**

```
python3 brain_v2.0_cascade.py
```
### **Option 2: Docker Method (Recommended)**

This method packages the entire "Brain" logic into a container, making it easy to run anywhere without installing Python manually.

**1. Set up your .env file**  
Create a file named .env in the project folder with your credentials:  
```
LAPTOP_IP=100.x.x.x  
REDIS_HOST=your-redis-endpoint  
REDIS_PORT=your-redis-port  
REDIS_PASSWORD=your-password
```

**2. Build and Run**  
Run this single command to start the system:  
```
docker compose up --build
```

**3. Interact with the Chatbot**
To use the interactive chat mode inside Docker, use this command instead:  
```
docker compose run --rm brain
```

This will launch the [You]: prompt where you can chat with your AI Sentinel directly.
