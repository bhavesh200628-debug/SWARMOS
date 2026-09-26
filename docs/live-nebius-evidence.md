# Live Nebius Token Factory Evidence & Audit

**Generated**: 2026-09-26T10:28:29.327681+00:00  
**Status**: `LIVE BENCHMARK: NOT VERIFIED`  
**Reason**: `NEBIUS_API_KEY` is not configured in the execution environment.

---

## 1. Verified Target Endpoints & Models

In accordance with official Nebius documentation (March 2026):
- **Primary Endpoint**: `https://api.tokenfactory.nebius.com/v1` (Token Factory)
- **Secondary / Legacy Endpoint**: `https://api.studio.nebius.ai/v1` (AI Studio)
- **Target Flagship Model**: `nvidia/Llama-3.1-Nemotron-70B-Instruct-HF`
- **Fallback / Edge Model**: `nvidia/nemotron-mini-4b-instruct`

## 2. Why Live Inference is Unverified on this Host
No live API key was set in the environment during this run.
In adherence to strict hackathon honesty rules, **no synthetic or fabricated live inference latencies are reported**.

## 3. How Judges Can Verify Live Inference
1. Set your Nebius API Key:
   ```bash
   export NEBIUS_API_KEY="your-token-factory-key"
   ```
2. Execute the live test runner:
   ```bash
   python3 scripts/test_live_nebius.py
   ```
This will automatically execute Tests A through D, generate `docs/live-nebius-evidence.md`, and record `evaluation/live_results.json`.
