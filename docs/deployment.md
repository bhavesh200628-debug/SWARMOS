# SWARMOS — Production Deployment & Operations Guide

> **Nebius x NVIDIA Global AI Hackathon 2026**  
> **Track:** Physical AI / Autonomous Robotics  
> **System:** SWARMOS — Distributed Physical AI Nervous System

---

## 1. Production Deployment Architecture

SWARMOS employs a cloud-native, decoupled edge/cloud architecture engineered for high availability, zero secret leakage, and real-time physical AI telemetry:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SWARMOS PRODUCTION TOPOLOGY                        │
│                                                                             │
│  ┌───────────────────────┐             ┌──────────────────────────────────┐ │
│  │   Vercel Edge Cloud   │             │ Nebius AI Cloud / Container Host │ │
│  │                       │             │                                  │ │
│  │  React 19 + Vite UI   │  HTTPS API  │  FastAPI Backend (Uvicorn)       │ │
│  │  - Tailwind CSS       ├────────────►│  - Deterministic Safety Guard    │ │
│  │  - Canvas Digital Twin│             │  - Dynamic Task Allocator        │ │
│  │  - Zero API Key Leak  │◄────────────┤  - 10Hz Simulation Engine        │ │
│  │  - Responsive Modals  │  WSS Stream │  - Failure Recovery State Machine│ │
│  └───────────────────────┘             └────────────────┬─────────────────┘ │
│                                                         │                   │
│                                              HTTPS API  │ (OpenAI-Compatible│
│                                              JSON-Schema│  Structured Spec) │
│                                                         ▼                   │
│                                        ┌──────────────────────────────────┐ │
│                                        │       Nebius Token Factory       │ │
│                                        │   nvidia/Llama-3.1-Nemotron-70B  │ │
│                                        │   nvidia/nemotron-mini-4b-inst   │ │
│                                        └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown
1. **Frontend (Vercel Edge Network)**:
   - Framework: React 19 + TypeScript + Vite.
   - Hosting: Vercel Single-Page Application (SPA) with edge caching.
   - Role: Real-time operator dashboard, interactive 2D digital twin canvas, telemetry visualizer, mission command console.
   - Security: Zero secrets baked into client bundle. Connects strictly to backend via configurable environment variables (`VITE_API_URL`, `VITE_WS_URL`).

2. **Backend (Docker Container / Nebius Cloud Compute / VM)**:
   - Framework: FastAPI + Uvicorn (ASGI).
   - Hosting: Nebius Cloud Compute VM, Docker Compose host, or cloud container services (Render, Railway, Fly.io, AWS ECS).
   - Role: Orchestrates robot fleet, runs 10Hz kinematic simulation, enforces 100% deterministic Safety Guard, and proxies reasoning requests to Nebius Token Factory.

3. **AI Inference (Nebius Token Factory)**:
   - Endpoint: `https://api.tokenfactory.nebius.com/v1` (or studio endpoint).
   - Flagship Model: `nvidia/Llama-3.1-Nemotron-70B-Instruct-HF`.
   - High-throughput Fallback: `nvidia/nemotron-mini-4b-instruct`.
   - Security: Authentication via Bearer token (`NEBIUS_API_KEY`) residing strictly in backend memory.

---

## 2. Frontend Deployment (Vercel)

### Live Verified Vercel Deployment
* **Production Alias URL**: [https://swarmos-alpha.vercel.app](https://swarmos-alpha.vercel.app)
* **Direct Deployment URL**: [https://swarmos-hggbvhi4b-bhavesh200628-debugs-projects.vercel.app](https://swarmos-hggbvhi4b-bhavesh200628-debugs-projects.vercel.app)
* **Project Name**: `swarmos`
* **Vercel Scope/Team**: `bhavesh200628-debugs-projects`
* **Status**: `DEPLOYED & OPERATIONAL (HTTP 200)`

### Step 1: Configure Vercel Project
1. Push repository to GitHub or GitLab.
2. In the Vercel Dashboard, select **Add New Project** and import the repository.
3. In Project Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (or `./` with Build Command `cd frontend && npm install && npm run build`)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Step 2: Environment Variables on Vercel
Set the following environment variables in **Project Settings → Environment Variables**:

| Variable Name | Required | Example Production Value | Purpose |
|:---|:---:|:---|:---|
| `VITE_API_URL` | **Yes** | `https://api.swarmos.yourdomain.com` | Base URL for REST API calls |
| `VITE_WS_URL` | **Yes** | `wss://api.swarmos.yourdomain.com/ws/telemetry` | Secure WebSocket telemetry URL |

> [!CAUTION]
> **CRITICAL SECURITY REQUIREMENT**:  
> **NEVER** expose `NEBIUS_API_KEY`, `TAVILY_API_KEY`, or any private credential in Vercel environment variables or with a `VITE_` prefix. Vercel client environment variables are embedded into client-side JavaScript bundles and are publicly readable.

### Step 3: Single-Page Application (SPA) Routing
The repository includes `frontend/vercel.json` (and root `vercel.json`) to handle client-side routing and prevent 404s on browser reloads:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

---

## 3. Backend Deployment (Docker & Cloud Compute)

### Option A: Docker Container Deployment (Recommended)

SWARMOS ships with an optimized multi-stage `Dockerfile` and `docker-compose.yml`.

#### Step 1: Clone and Configure Environment
On your server (Nebius Compute VM, Ubuntu 22.04+, Debian, or cloud host):
```bash
git clone https://github.com/bhavesh200628-debug/SWARMOS.git
cd SWARMOS
cp .env.example .env
```

Edit `.env` with production values:
```ini
# Production Nebius AI Settings
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1
NEBIUS_API_KEY=your_actual_nebius_api_key_here
NEBIUS_MODEL=nvidia/Llama-3.1-Nemotron-70B-Instruct-HF
NEBIUS_FALLBACK_MODEL=nvidia/nemotron-mini-4b-instruct

# Production CORS Security (Set to your Vercel domain)
CORS_ORIGINS=https://swarmos.vercel.app,https://your-custom-domain.com

# Server Settings
SWARMOS_HOST=0.0.0.0
SWARMOS_PORT=8000
MOCK_AI=false
```

#### Step 2: Build & Start Container
```bash
docker compose up -d --build
```

#### Step 3: Verify Container Health
```bash
# Check running status and health check
docker compose ps

# Inspect container logs
docker compose logs -f swarmos
```

---

### Option B: Bare-Metal / Native Systemd Service (Nebius Cloud VM)

If deploying directly onto a Nebius Linux VM without Docker:

```bash
# 1. System packages
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv curl

# 2. Virtual environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Create systemd service unit
sudo tee /etc/systemd/system/swarmos.service > /dev/null <<EOF
[Unit]
Description=SWARMOS Physical AI Fleet Orchestrator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/SWARMOS
EnvironmentFile=/home/ubuntu/SWARMOS/.env
ExecStart=/home/ubuntu/SWARMOS/venv/bin/python3 -m backend.app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 4. Start and enable service
sudo systemctl daemon-reload
sudo systemctl enable --now swarmos
sudo systemctl status swarmos
```

---

## 4. Reverse Proxy, CORS & WebSocket Configuration

To support SSL/TLS termination and WebSocket bidirectional streaming, place NGINX, Caddy, or Cloudflare in front of port 8000.

### Production NGINX Configuration
```nginx
server {
    server_name api.swarmos.yourdomain.com;

    # REST API endpoints
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket Real-Time Telemetry Stream
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

### CORS Verification
When `CORS_ORIGINS` is configured:
- The backend verifies every incoming HTTP `Origin` header against the whitelist.
- Preflight `OPTIONS` requests receive appropriate `Access-Control-Allow-Origin` and `Access-Control-Allow-Methods` headers.
- Setting `CORS_ORIGINS=*` is acceptable for public hackathon demonstration evaluations.

---

## 5. End-to-End Smoke Test Checklist

Execute these 6 verification steps sequentially after deployment to guarantee 100% operational readiness:

### 1. General System Health
```bash
curl -s -f https://<BACKEND_HOST>/health | jq .
```
**Expected Response:**
```json
{
  "status": "ok",
  "service": "SWARMOS",
  "tagline": "One nervous system for an entire robot fleet.",
  "version": "1.0.0",
  "uptime_sec": 42.1
}
```

### 2. AI Inference Engine & Nebius Connection Status
```bash
curl -s -f https://<BACKEND_HOST>/health/ai | jq .
```
**Expected Response (when NEBIUS_API_KEY is configured):**
```json
{
  "status": "operational",
  "provider": "Nebius Token Factory",
  "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
  "mode": "LIVE NEBIUS — NVIDIA NEMOTRON",
  "configured": true,
  "execution_mode": "LIVE_NEBIUS_TOKEN_FACTORY",
  "is_mock": false
}
```

### 3. Simulation Engine Status
```bash
curl -s -f https://<BACKEND_HOST>/health/simulation | jq .
```
**Expected Response:**
```json
{
  "status": "running",
  "tick_count": 420,
  "active_robots": 3,
  "active_packages": 2,
  "speed_multiplier": 1.0
}
```

### 4. Mission Submission Test
```bash
curl -s -X POST https://<BACKEND_HOST>/api/missions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Deliver emergency medical kit to ICU Zone C immediately"}' | jq .
```
**Expected Response:**
- Returns mission UUID, `status: "planning"` or `"in_progress"`.
- Validates that the Task Allocator mapped the action to a robot with `lift_heavy` or `deliver_medical` capability.

### 5. Automated Demo Execution Test
```bash
curl -s -X POST https://<BACKEND_HOST>/api/demo/run | jq .
```
**Expected Response:**
```json
{
  "status": "started",
  "message": "Hero demo scenario initiated"
}
```

### 6. WebSocket Live Telemetry Stream Test
Using `wscat` or browser console:
```bash
# Install wscat if needed: npm install -g wscat
wscat -c wss://<BACKEND_HOST>/ws/telemetry
```
**Expected Output:** Continuous JSON telemetry frames at 10Hz containing:
- `timestamp`: Unix millisecond float.
- `robots`: Array of 3 robots with kinematic coordinates (`x`, `y`, `heading`, `battery`, `status`).
- `packages`: Array of physical payload states (`id`, `x`, `y`, `carrier_id`).
- `decisions`: Recent AI reasoning and Safety Guard decisions.

---

## 6. Rollback & Disaster Recovery Procedures

### Scenario A: Broken Frontend Deployment on Vercel
1. Navigate to **Vercel Dashboard → Deployments**.
2. Locate the previous successful deployment SHA.
3. Click the three dots `...` → **Instant Rollback**.
4. Traffic instantly shifts to the prior immutable build with zero downtime.

### Scenario B: Backend Container Crash or Bad Deployment
If updating the backend container causes an unhandled error:
```bash
# Revert to previous Docker image tag
docker stop swarmos-app
docker run -d --name swarmos-app \
  -p 8000:8000 \
  --env-file .env \
  swarmos:stable-backup

# Or using git rollback:
git checkout HEAD~1
docker compose up -d --build
```

### Scenario C: Nebius Token Factory API Outage / Network Latency Spike
SWARMOS contains a **Dual-Layer Fail-Safe**:
1. **Model Fallback**: If `nvidia/Llama-3.1-Nemotron-70B-Instruct-HF` times out (>12s), the system retries against the lightweight `nvidia/nemotron-mini-4b-instruct`.
2. **Deterministic Local Fallback**: If Nebius network connectivity is completely severed or quota is exhausted, SWARMOS automatically engages its local deterministic task planner.
3. **No Fleet Stoppage**: The 10Hz kinematic simulation and Safety Guard **never crash**. The UI displays an amber badge: `LOCAL SIMULATION` instead of `LIVE NEBIUS`, keeping the physical fleet operational and safe.

### Scenario D: Physical Safety Emergency
To instantly halt all physical robots and simulation movements:
```bash
# Emergency Stop endpoint (triggers emergency brake on all robots)
curl -X POST https://<BACKEND_HOST>/api/demo/reset
```
The Safety Guard drops all active trajectories and broadcasts `status: "idle"` / `emergency_stop: true` to all actuators.
