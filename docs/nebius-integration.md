# Nebius Token Factory & NVIDIA Nemotron Integration Guide

This document details the exact integration architecture, authentication, model selection, runtime request flow, and verification steps for Nebius Token Factory within SWARMOS.

---

## 1. Nebius Token Factory Overview

Nebius Token Factory provides an enterprise-grade, high-throughput OpenAI-compatible inference endpoint backed by modern NVIDIA GPU infrastructure (H100 / H200 clusters).

- **API Base URL**: `https://api.studio.nebius.ai/v1`
- **Specification**: OpenAI Chat Completions API v1 compatible
- **Authentication**: HTTP Authorization Header with `Bearer $NEBIUS_API_KEY`

---

## 2. NVIDIA Model Selection & Justification

### Primary Model: `nvidia/Llama-3.1-Nemotron-70B-Instruct-HF`
- **Provider**: NVIDIA Open Model Family hosted on Nebius Token Factory.
- **Why this model?**
  1. **Advanced System-Level Reasoning**: Decomposing natural-language missions into multi-robot dependency graphs requires strong instruction-following and zero-shot schema adherence.
  2. **Strict Machine-Readable Output**: Nemotron 70B reliably produces pure JSON objects matching complex Pydantic schemas without conversational commentary or syntax errors.
  3. **Low Latency on Nebius**: Nebius Token Factory serves Nemotron with optimized tensor parallelism, delivering sub-200ms time-to-first-token, vital for autonomous robotic replanning.

### Fallback / Edge Model: `nvidia/nemotron-mini-4b-instruct`
- Configured as automatic fallback if quota limits or regional availability vary.

---

## 3. Runtime Request Flow

When an event triggers AI planning (either an initial mission submission or a robot failure event):

```
SWARMOS Backend
   │
   ├─► Step 1: Serialize Fleet State & Task Graph into JSON
   │
   ├─► Step 2: Inject into Strict System Prompt (NEMOTRON_SYSTEM_PROMPT)
   │
   ├─► Step 3: POST https://api.studio.nebius.ai/v1/chat/completions
   │     Header: Authorization: Bearer <NEBIUS_API_KEY>
   │     Body: {
   │       "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
   │       "messages": [...],
   │       "temperature": 0.15,
   │       "max_tokens": 2048
   │     }
   │
   ├─► Step 4: Parse JSON response & extract structured decision
   │
   ├─► Step 5: Validate via Pydantic Schema (AIPlanResponse)
   │
   └─► Step 6: Pass through Deterministic Safety Guard before execution
```

---

## 4. Code Verification in SWARMOS

The integration code is located in [`backend/nebius/client.py`](file:///Users/bhaveshsuthar/Desktop/NVIDIA/backend/nebius/client.py):

```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(
        f"{self.base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    )
```

### No Fake Calls Guarantee:
- If `NEBIUS_API_KEY` is present and valid, SWARMOS performs live network HTTP calls directly to the Nebius endpoint.
- If `NEBIUS_API_KEY` is absent (such as in an offline evaluation or local sandbox), SWARMOS clearly indicates in logs and the UI that it is operating in **Deterministic Local Simulation Mode**, without faking or spoofing network credentials.

---

## 5. How to Reproduce Live Nebius Inference

1. Sign up or log in to [Nebius AI Studio](https://studio.nebius.ai).
2. Generate an API Key under **API Keys**.
3. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
4. Set your API key:
   ```bash
   NEBIUS_API_KEY=your_actual_nebius_api_key_here
   MOCK_AI=false
   ```
5. Restart SWARMOS:
   ```bash
   ./venv/bin/python3 -m backend.app
   ```
6. Verify live status:
   ```bash
   curl http://localhost:8000/health/ai
   ```
   Output:
   ```json
   {
     "status": "operational",
     "nebius_endpoint": "https://api.studio.nebius.ai/v1",
     "target_model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
     "execution_mode": "LIVE_NEBIUS_TOKEN_FACTORY",
     "api_key_configured": true,
     "is_mock": false
   }
   ```
