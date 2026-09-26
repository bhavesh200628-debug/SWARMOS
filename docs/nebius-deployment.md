# SWARMOS — Nebius AI Cloud Deployment Guide

This guide details how to deploy and operate SWARMOS on **Nebius AI Cloud Compute** or any containerized host connected to the **Nebius Token Factory**.

---

## 1. Architecture Overview on Nebius Cloud

```
┌────────────────────────────────────────────────────────┐
│                   Nebius AI Cloud                      │
│                                                        │
│  ┌──────────────────────┐    ┌──────────────────────┐  │
│  │ Nebius Token Factory │    │ Nebius Cloud Compute │  │
│  │ (LLM Inference API)  │◄───┤ (Container / VM)     │  │
│  │ - Nemotron-70B       │    │                      │  │
│  │ - Nemotron-Mini-4B   │    │ ┌──────────────────┐ │  │
│  └──────────────────────┘    │ │ Docker Container │ │  │
│                              │ │ - FastAPI Backend│ │  │
│                              │ │ - React Web UI   │ │  │
│                              │ │ - Safety Guard   │ │  │
│                              │ │ - 10Hz Sim Engine│ │  │
│                              │ └──────────────────┘ │  │
│                              └──────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites

1. **Nebius AI Studio Account**: [https://studio.nebius.ai](https://studio.nebius.ai)
2. **Nebius API Key**: Generated under API Keys in Nebius AI Studio.
3. **Compute Host**: Nebius Compute VM or any Linux/Mac server with Docker and `git` installed.

---

## 3. Quickstart Deployment via Docker Compose

### Step 1: Clone Repository
```bash
git clone https://github.com/bhavesh200628-debug/SWARMOS.git
cd SWARMOS
```

### Step 2: Configure Environment
Copy `.env.example` to `.env` and insert your Nebius Token Factory API key:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
NEBIUS_BASE_URL=https://api.studio.nebius.ai/v1
NEBIUS_API_KEY=your_actual_nebius_api_key_here
NEBIUS_MODEL=nvidia/Llama-3.1-Nemotron-70B-Instruct-HF
NEBIUS_FALLBACK_MODEL=nvidia/nemotron-mini-4b-instruct
MOCK_AI=false
```

### Step 3: Build & Launch Container
```bash
docker compose up -d --build
```

### Step 4: Verify Deployment Health
```bash
# Check container status
docker compose ps

# Test SWARMOS health endpoint
curl http://localhost:8000/api/health

# Test AI Engine status (Verifies Nebius Token Factory connectivity)
curl http://localhost:8000/api/health/ai
```

Expected output when live Nebius key is configured:
```json
{
  "status": "healthy",
  "provider": "Nebius Token Factory",
  "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
  "mode": "LIVE — NEBIUS TOKEN FACTORY",
  "configured": true
}
```

---

## 4. Manual Deployment on Nebius Cloud VM (Native Python)

If deploying directly onto a Nebius VM without Docker:

```bash
# 1. Install dependencies
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv nodejs npm

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Build Frontend
cd frontend
npm install
npm run build
cd ..

# 4. Run Live Nebius Verification Script
python3 scripts/test_live_nebius.py

# 5. Start SWARMOS Server
python3 -m backend.app
```

---

## 5. Security & Isolation Invariants
* **Zero Secret Leakage**: The Docker build does **not** bake API keys into the image layer. Keys are injected strictly via runtime environment variables.
* **Deterministic Fail-Safe**: If Nebius Token Factory network times out or the quota is exhausted, SWARMOS automatically fails over to the local deterministic model profile with an explicit badge in the UI.
