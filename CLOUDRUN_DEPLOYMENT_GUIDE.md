# ☁️ Cloud Run Deployment Guide - Demo Generation CAPI

**Comprehensive guide for deploying the Demo Generation CAPI application to Google Cloud Run**

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Variables Reference](#environment-variables-reference)
4. [Deployment Methods](#deployment-methods)
5. [Resource Configuration](#resource-configuration)
6. [Secrets Management](#secrets-management)
7. [Networking & CORS](#networking--cors)
8. [Monitoring & Logging](#monitoring--logging)
9. [Troubleshooting](#troubleshooting)
10. [Performance Optimization](#performance-optimization)

---

## 🏗️ Architecture Overview

### Application Stack

**Multi-stage Build:**
```
┌─────────────────────────────────────┐
│  Stage 1: Frontend Build (Node 18)  │
│  ├── React + Vite + TypeScript      │
│  ├── Tailwind CSS + shadcn/ui       │
│  └── Build output → /dist           │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│  Stage 2: Backend (Python 3.11)     │
│  ├── FastAPI + Uvicorn              │
│  ├── LangGraph Orchestration        │
│  ├── Anthropic Claude (Vertex AI)   │
│  ├── Google Gemini API              │
│  └── Static frontend from Stage 1   │
└─────────────────────────────────────┘
```

### Key Components

1. **Frontend (React/Vite)**
   - Path: `newfrontend/conversational-api-demo-frontend/`
   - Build: Vite → static assets in `/dist`
   - Port: 8080 (dev only, served by backend in prod)

2. **Backend (FastAPI)**
   - Path: `backend/`
   - Framework: FastAPI + Uvicorn
   - Port: 8000 (exposed to Cloud Run)
   - Entry: `backend/api.py`

3. **Agentic Orchestration**
   - Path: `backend/agentic_service/`
   - Orchestrator: `demo_orchestrator.py` (LangGraph)
   - Agents:
     - Research Agent (Gemini/Claude)
     - Demo Story Agent (Gemini/Claude)
     - Data Modeling Agent (Gemini/Claude)
     - Synthetic Data Generator
     - Infrastructure Agent (BigQuery)
     - CAPI Instruction Generator (Gemini/Claude)
     - Demo Validator

---

## ✅ Prerequisites

### 1. Google Cloud Setup

```bash
# Set project
export PROJECT_ID="bq-demos-469816"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### 2. Authentication

**For Claude (Anthropic on Vertex AI):**
```bash
# Service account needs these roles:
# - Vertex AI User (roles/aiplatform.user)
# - BigQuery Data Editor (roles/bigquery.dataEditor)
# - BigQuery Job User (roles/bigquery.jobUser)

gcloud auth application-default login
```

**For Gemini API:**
- Obtain API key from Google AI Studio: https://aistudio.google.com/app/apikey
- Store securely (see Secrets Management section)

### 3. Required Permissions

**Service Account Permissions:**
```yaml
roles:
  - roles/aiplatform.user          # Claude/Gemini on Vertex AI
  - roles/bigquery.dataEditor      # Create datasets/tables
  - roles/bigquery.jobUser         # Run queries
  - roles/secretmanager.secretAccessor  # Access secrets (if using Secret Manager)
```

---

## 🔑 Environment Variables Reference

### **CRITICAL - Required for All Environments**

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `PROJECT_ID` | String | GCP Project ID | `bq-demos-469816` |
| `LOCATION` | String | GCP Region | `us-central1`, `us-east5` |
| `ENVIRONMENT` | String | Deployment env | `dev`, `staging`, `prod` |
| `GEMINI_API_KEY` | Secret | Gemini API key | `AIzaSy...` |

### **Agent Model Selection (Gemini vs Claude)**

**Based on benchmarks in `benchmarks/AGENT_SELECTOR_GUIDE.md`**

| Variable | Options | Default | Recommendation |
|----------|---------|---------|----------------|
| `RESEARCH_AGENT_MODEL` | `gemini`, `claude` | `gemini` | **Gemini** - 2x faster (131s vs 263s) |
| `DEMO_STORY_AGENT_MODEL` | `gemini`, `claude` | `gemini` | **Gemini** - 2.13x faster, same quality |
| `DATA_MODELING_AGENT_MODEL` | `gemini`, `claude` | `claude` | **Claude** - User preference, quality |
| `CAPI_AGENT_MODEL` | `gemini`, `claude` | `claude` | **Claude** - Quality critical ⚠️ |

**⚠️ IMPORTANT:** Never use Gemini for CAPI Agent - it generates incomplete YAML (49% smaller, missing tables/queries)

### **Demo Complexity Configuration**

Control generation speed vs. comprehensiveness:

| Variable | Range | Quick Test | Full Demo | Max |
|----------|-------|-----------|-----------|-----|
| `DEMO_NUM_QUERIES` | 1-20 | `1-3` | `6-10` | `15-18` |
| `DEMO_NUM_SCENES` | 1-7 | `1-2` | `3-4` | `5-7` |
| `DEMO_NUM_ENTITIES` | 3-20 | `3-5` | `8-10` | `12-15` |

**Recommended Presets:**

```bash
# FAST MODE (for testing, ~2-5 min)
DEMO_NUM_QUERIES=1
DEMO_NUM_SCENES=1
DEMO_NUM_ENTITIES=4

# BALANCED MODE (for demos, ~8-15 min)
DEMO_NUM_QUERIES=6
DEMO_NUM_SCENES=4
DEMO_NUM_ENTITIES=8

# COMPREHENSIVE MODE (for production, ~20-30 min)
DEMO_NUM_QUERIES=12
DEMO_NUM_SCENES=5
DEMO_NUM_ENTITIES=15
```

### **Research Agent V2 Configuration**

For advanced web crawling (slower but richer):

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `V2_MAX_PAGES` | Integer | `50` | Max pages to crawl (recommend `20-30`) |
| `V2_MAX_DEPTH` | Integer | `3` | Crawl depth (recommend `2`) |
| `V2_ENABLE_BLOG` | Boolean | `false` | Scrape blog for tech stack |
| `V2_ENABLE_LINKEDIN` | Boolean | `false` | Find LinkedIn company page |
| `V2_ENABLE_YOUTUBE` | Boolean | `false` | Find YouTube channel |

### **Optional Configuration**

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug logging |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `PYTHONUNBUFFERED` | `1` | Force unbuffered Python output (for Cloud Run logs) |

---

## 🚀 Deployment Methods

### **Method 1: Using Existing Script (RECOMMENDED)**

The project includes a deployment script with environment presets:

```bash
cd /home/admin_/final_demo/capi/demo-gen-capi

# Deploy to PRODUCTION (Balanced Mode)
./deploy-to-cloudrun.sh prod

# Deploy to STAGING
./deploy-to-cloudrun.sh staging

# Deploy to DEV (Fast Mode)
./deploy-to-cloudrun.sh dev
```

**What the script does:**
- ✅ Sets environment-specific resources (memory, CPU)
- ✅ Configures agent models based on environment
- ✅ Sets demo complexity parameters
- ✅ Deploys using Cloud Run source deployment
- ✅ Returns service URL for testing

### **Method 2: Manual gcloud Deployment**

For custom configurations:

```bash
# Build and deploy in one command
gcloud run deploy demo-gen-capi-prod \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --set-env-vars "PROJECT_ID=bq-demos-469816,LOCATION=us-central1,ENVIRONMENT=prod" \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

### **Method 3: Docker Build + Deploy**

For full control over the build:

```bash
# Build Docker image
docker build -t gcr.io/$PROJECT_ID/demo-gen-capi:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/demo-gen-capi:latest

# Deploy from image
gcloud run deploy demo-gen-capi-prod \
  --image gcr.io/$PROJECT_ID/demo-gen-capi:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10
```

### **Method 4: CI/CD with Cloud Build**

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/demo-gen-capi:$SHORT_SHA', '.']

  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/demo-gen-capi:$SHORT_SHA']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'demo-gen-capi-prod'
      - '--image=gcr.io/$PROJECT_ID/demo-gen-capi:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/demo-gen-capi:$SHORT_SHA'

timeout: 1800s  # 30 minutes
```

Deploy with:
```bash
gcloud builds submit --config cloudbuild.yaml
```

---

## 💾 Resource Configuration

### **Development Environment**

**Use Case:** Testing, quick iterations, single demo at a time

```bash
--memory 2Gi
--cpu 1
--timeout 1800        # 30 minutes
--max-instances 3
--concurrency 1       # Process one request at a time
--min-instances 0     # Scale to zero when idle
```

**Cost:** ~$0.05 per demo (2 min runtime)

### **Staging Environment**

**Use Case:** Pre-production testing, multiple demos

```bash
--memory 4Gi
--cpu 2
--timeout 3600        # 60 minutes
--max-instances 5
--concurrency 1       # Still single-threaded processing
--min-instances 0
```

**Cost:** ~$0.10 per demo (8 min runtime)

### **Production Environment (RECOMMENDED)**

**Use Case:** Customer-facing, high reliability

```bash
--memory 4Gi          # Required for Claude + BigQuery
--cpu 2               # Parallel agent execution
--timeout 3600        # 60 min (max for Cloud Run)
--max-instances 10    # Handle multiple concurrent demos
--concurrency 1       # Each instance processes one demo at a time
--min-instances 1     # Always warm (faster response)
```

**Cost:** ~$0.10 per demo + $0.05/day for min instance

### **Memory Sizing Guide**

| Memory | Use Case | Agent Models | Demo Complexity |
|--------|----------|--------------|-----------------|
| **2Gi** | Quick testing | Gemini-only | 1-3 queries |
| **4Gi** | Full demos ✅ | Gemini + Claude | 6-10 queries |
| **8Gi** | Large/complex | Claude-heavy | 15+ queries |

**Why 4Gi is recommended:**
- Claude models require ~2Gi base memory
- LangGraph state management: ~500MB
- BigQuery client: ~300MB
- FastAPI + Uvicorn: ~200MB
- Buffer for peak usage: ~1Gi

### **Timeout Recommendations**

**Based on demo complexity:**

| Complexity | Typical Duration | Recommended Timeout |
|------------|------------------|---------------------|
| Fast (1 query) | 2-5 min | `--timeout 900` (15 min) |
| Balanced (6 queries) | 8-15 min | `--timeout 1800` (30 min) |
| Comprehensive (12+ queries) | 20-40 min | `--timeout 3600` (60 min) |

**⚠️ Cloud Run Max:** 60 minutes (3600 seconds)

---

## 🔐 Secrets Management

### **Option 1: Google Secret Manager (RECOMMENDED)**

**1. Create secret:**
```bash
echo -n "AIzaSyCo3lMlWXexEQW45mS3nH9J-C6Cf9XZmZk" | \
  gcloud secrets create gemini-api-key --data-file=-
```

**2. Grant access to Cloud Run service account:**
```bash
# Get the service account email
SERVICE_ACCOUNT=$(gcloud run services describe demo-gen-capi-prod \
  --region us-central1 \
  --format 'value(spec.template.spec.serviceAccountName)')

# Grant access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
```

**3. Deploy with secret:**
```bash
gcloud run deploy demo-gen-capi-prod \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

### **Option 2: Environment Variables (NOT RECOMMENDED for production)**

Only use for testing:

```bash
gcloud run deploy demo-gen-capi-dev \
  --set-env-vars "GEMINI_API_KEY=AIzaSy..."
```

**⚠️ WARNING:** Secrets in env vars are visible in Cloud Console and logs!

### **Required Secrets**

| Secret | Source | Required For |
|--------|--------|-------------|
| `GEMINI_API_KEY` | Google AI Studio | Gemini agents, Gemini Data Analytics |
| (Optional) `ANTHROPIC_API_KEY` | Anthropic Console | Direct Anthropic API (not needed for Vertex AI) |

---

## 🌐 Networking & CORS

### **Current CORS Configuration**

In `backend/api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ WIDE OPEN
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Production CORS (RECOMMENDED CHANGE)**

```python
# Get allowed origins from environment
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://your-frontend-domain.com,https://console.cloud.google.com"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

Deploy with:
```bash
gcloud run deploy demo-gen-capi-prod \
  --set-env-vars "ALLOWED_ORIGINS=https://your-domain.com"
```

### **Ingress Control**

**Internal traffic only (VPC):**
```bash
gcloud run deploy demo-gen-capi-prod \
  --ingress internal
```

**All traffic (public):**
```bash
gcloud run deploy demo-gen-capi-prod \
  --ingress all
```

---

## 📊 Monitoring & Logging

### **View Logs**

```bash
# Stream logs
gcloud run logs tail demo-gen-capi-prod --region us-central1

# View recent logs
gcloud run logs read demo-gen-capi-prod \
  --region us-central1 \
  --limit 100

# Filter by severity
gcloud run logs read demo-gen-capi-prod \
  --region us-central1 \
  --log-filter "severity>=ERROR"

# Filter by timestamp
gcloud run logs read demo-gen-capi-prod \
  --region us-central1 \
  --log-filter 'timestamp>="2025-10-06T14:00:00Z"'
```

### **Structured Logging**

The application logs to `backend.log` file, but Cloud Run captures stdout/stderr.

**To improve logging for Cloud Run:**

**Change `backend/api.py` line 29:**
```python
# OLD (file-based):
logging.basicConfig(filename='backend.log', level=logging.INFO)

# NEW (stdout for Cloud Run):
import sys
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
```

### **Application Metrics**

**View in Cloud Console:**
```
Navigation → Cloud Run → [service] → METRICS
```

**Key metrics to monitor:**
- Request count
- Request latency (p50, p95, p99)
- Container CPU utilization
- Container memory utilization
- Billable container time

### **Custom Metrics with Cloud Monitoring**

Add to `backend/api.py`:
```python
from google.cloud import monitoring_v3
import time

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{os.environ['PROJECT_ID']}"

def record_provisioning_duration(customer_url: str, duration_seconds: float):
    """Record provisioning duration as custom metric."""
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/provisioning/duration"
    series.resource.type = "cloud_run_revision"

    point = monitoring_v3.Point()
    point.value.double_value = duration_seconds
    point.interval.end_time.seconds = int(time.time())
    series.points = [point]

    client.create_time_series(name=project_name, time_series=[series])
```

### **Alerting**

Create alert policy:
```bash
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 10%" \
  --condition-threshold-value=0.1 \
  --condition-threshold-duration=300s
```

---

## 🐛 Troubleshooting

### **Issue 1: Module Not Found (langgraph, vertexai)**

**Symptom:**
```
ModuleNotFoundError: No module named 'langgraph'
ModuleNotFoundError: No module named 'vertexai'
```

**Root Cause:** Missing dependencies in `requirements.txt`

**Fix:**
```bash
# Add to backend/requirements.txt:
langgraph>=0.0.50
google-cloud-aiplatform>=1.38.0
```

**Verify before deployment:**
```bash
cd backend
python -c "import langgraph; import vertexai; print('✅ All imports OK')"
```

### **Issue 2: Memory Limit Exceeded**

**Symptom:**
```
Container instance exceeded memory limit
```

**Diagnosis:**
```bash
# Check memory usage in logs
gcloud run logs read demo-gen-capi-prod \
  --log-filter "jsonPayload.message=~'memory'"
```

**Solutions:**
1. Increase memory:
   ```bash
   gcloud run services update demo-gen-capi-prod \
     --memory 8Gi --region us-central1
   ```

2. Use Gemini instead of Claude (uses less memory):
   ```bash
   --set-env-vars "DATA_MODELING_AGENT_MODEL=gemini"
   ```

3. Reduce demo complexity:
   ```bash
   --set-env-vars "DEMO_NUM_QUERIES=3,DEMO_NUM_ENTITIES=5"
   ```

### **Issue 3: Timeout Errors**

**Symptom:**
```
Request deadline exceeded (60 seconds)
```

**Fix:**
```bash
# Increase timeout to max (60 min)
gcloud run services update demo-gen-capi-prod \
  --timeout 3600 --region us-central1
```

**Alternative:** Use Fast Mode:
```bash
--set-env-vars "DEMO_NUM_QUERIES=1,DEMO_NUM_SCENES=1,RESEARCH_AGENT_MODEL=gemini"
```

### **Issue 4: BigQuery Permission Denied**

**Symptom:**
```
403 Forbidden: User does not have permission to create datasets
```

**Fix:**
```bash
# Get service account
SERVICE_ACCOUNT=$(gcloud run services describe demo-gen-capi-prod \
  --region us-central1 \
  --format 'value(spec.template.spec.serviceAccountName)')

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.jobUser"
```

### **Issue 5: Vertex AI Authentication Failed**

**Symptom:**
```
google.auth.exceptions.DefaultCredentialsError
```

**Fix:**
```bash
# Ensure service account has Vertex AI permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```

### **Issue 6: Frontend Not Loading**

**Symptom:** Cloud Run serves backend but frontend shows 404

**Diagnosis:**
```bash
# Check if frontend built correctly
gcloud run logs read demo-gen-capi-prod \
  --log-filter "frontend"
```

**Common causes:**

1. **Frontend build failed:**
   - Check `Dockerfile` COPY paths
   - Verify `newfrontend/conversational-api-demo-frontend/dist` exists after build

2. **Static file serving issue:**
   - Check `backend/api.py` lines 41-47 (frontend path detection)
   - Ensure `FRONTEND_DIST_DIR` is set correctly in container

**Test locally:**
```bash
# Build Docker image locally
docker build -t test-image .

# Run and check files
docker run -it test-image ls -la /app/newfrontend/conversational-api-demo-frontend/dist

# Should show:
# drwxr-xr-x 3 root root  4096 Oct  6 14:00 .
# drwxr-xr-x 4 root root  4096 Oct  6 14:00 ..
# drwxr-xr-x 2 root root  4096 Oct  6 14:00 assets
# -rw-r--r-- 1 root root   123 Oct  6 14:00 index.html
```

---

## ⚡ Performance Optimization

### **1. Cold Start Optimization**

**Problem:** First request takes 10-30 seconds (container cold start)

**Solutions:**

**a) Minimum Instances (RECOMMENDED for prod):**
```bash
gcloud run services update demo-gen-capi-prod \
  --min-instances 1 \
  --region us-central1
```
- Keeps 1 instance always warm
- Cost: ~$0.05/day
- Response time: <2s instead of 10-30s

**b) Cloud Scheduler Warmup (Alternative):**
```bash
# Create warmup job that hits /health every 5 minutes
gcloud scheduler jobs create http demo-gen-warmup \
  --schedule "*/5 * * * *" \
  --uri "https://demo-gen-capi-prod-xxx.run.app/health" \
  --http-method GET
```
- Free tier: 3 jobs
- Keeps container warm during business hours

### **2. Concurrency Tuning**

**Current:** `--concurrency 1` (each instance handles 1 request)

**Why?** Demo provisioning is:
- CPU-intensive (LLM inference)
- Memory-intensive (multiple agents)
- Long-running (8-40 minutes)

**DO NOT CHANGE** unless you:
- Have 8Gi+ memory
- Test with concurrent requests
- Monitor memory usage closely

### **3. Agent Model Selection for Speed**

**Fastest Configuration (2-5 min for 1 query):**
```bash
RESEARCH_AGENT_MODEL=gemini      # 2x faster than Claude
DEMO_STORY_AGENT_MODEL=gemini    # 2.13x faster than Claude
DATA_MODELING_AGENT_MODEL=gemini # ~same speed, less memory
CAPI_AGENT_MODEL=claude          # MUST use Claude (quality critical)
```

**Balanced Configuration (8-15 min for 6 queries):**
```bash
RESEARCH_AGENT_MODEL=gemini
DEMO_STORY_AGENT_MODEL=gemini
DATA_MODELING_AGENT_MODEL=claude  # Better quality
CAPI_AGENT_MODEL=claude
```

### **4. Caching Research Results**

**Add to `backend/agentic_service/agents/research_agent_v2_optimized.py`:**

```python
import redis
import hashlib
import json

# Connect to Cloud Memorystore (Redis)
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST'),
    port=6379,
    decode_responses=True
)

def get_cached_research(url: str) -> Optional[dict]:
    cache_key = f"research:{hashlib.md5(url.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

def cache_research(url: str, data: dict, ttl: int = 86400):
    cache_key = f"research:{hashlib.md5(url.encode()).hexdigest()}"
    redis_client.setex(cache_key, ttl, json.dumps(data))
```

**Deploy with Memorystore:**
```bash
# Create Redis instance
gcloud redis instances create demo-gen-cache \
  --size=1 \
  --region=us-central1

# Connect Cloud Run to VPC
gcloud run services update demo-gen-capi-prod \
  --vpc-connector=demo-gen-vpc \
  --set-env-vars "REDIS_HOST=10.0.0.3"
```

### **5. Parallel Agent Execution**

**Current:** Sequential execution (one agent after another)

**Optimization:** Run independent agents in parallel

**Edit `backend/agentic_service/demo_orchestrator.py`:**
```python
import asyncio

async def run_parallel_agents(customer_url):
    # Research doesn't depend on anything - start it
    research_task = asyncio.create_task(research_agent.run(customer_url))

    # Wait for research to complete
    customer_info = await research_task

    # Demo story and data modeling can run in parallel (both need research)
    demo_story_task = asyncio.create_task(demo_story_agent.run(customer_info))
    data_model_task = asyncio.create_task(data_modeling_agent.run(customer_info))

    # Wait for both
    demo_story, data_model = await asyncio.gather(demo_story_task, data_model_task)

    # Continue with rest of pipeline...
```

**Estimated speedup:** 20-30% reduction in total time

---

## 🎯 Deployment Checklist

### **Pre-Deployment**

- [ ] Secrets stored in Secret Manager (not env vars)
- [ ] Service account has all required permissions
- [ ] `requirements.txt` includes all dependencies (`langgraph`, `google-cloud-aiplatform`)
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Docker builds successfully locally (`docker build -t test .`)
- [ ] CORS origins restricted (not `allow_origins=["*"]`)
- [ ] Logging configured for Cloud Run (stdout, not file)

### **Post-Deployment**

- [ ] Health check passes: `curl https://[SERVICE-URL]/health`
- [ ] Frontend loads: Visit `https://[SERVICE-URL]/`
- [ ] API docs accessible: `https://[SERVICE-URL]/docs`
- [ ] Test provisioning: `curl -X POST https://[SERVICE-URL]/api/provision/start -H "Content-Type: application/json" -d '{"customer_url": "https://www.nike.com"}'`
- [ ] Logs streaming correctly: `gcloud run logs tail ...`
- [ ] Metrics showing in Cloud Console
- [ ] Alerts configured for errors/timeouts

### **Production Readiness**

- [ ] Min instances set to 1 (avoid cold starts)
- [ ] Memory set to 4Gi minimum
- [ ] Timeout set to 3600 (60 min)
- [ ] Custom domain configured (optional)
- [ ] Cloud Armor WAF configured (optional)
- [ ] Load testing completed
- [ ] Disaster recovery plan documented
- [ ] Cost alerts configured

---

## 💰 Cost Estimation

### **Cloud Run Pricing (us-central1)**

**Resources per request (Balanced Mode):**
- Memory: 4Gi
- CPU: 2 vCPU
- Duration: ~8 minutes (6 queries)

**Cost per demo:**
```
CPU:    2 vCPU × 8 min × $0.00002400/vCPU-second = $0.023
Memory: 4 GiB × 8 min × $0.00000250/GiB-second  = $0.005
Total:                                            $0.028
```

**Monthly estimates:**

| Usage | Demos/Month | Cost |
|-------|-------------|------|
| Low (testing) | 10 | $0.28 |
| Medium (demos) | 100 | $2.80 |
| High (production) | 1000 | $28.00 |

**Add minimum instances:**
- 1 min instance: ~$1.50/day = $45/month
- **Total for medium usage:** ~$48/month

### **Additional Costs**

- **Gemini API:** $0.00075 per 1K characters (input), $0.00300 per 1K characters (output)
  - Estimate: ~$0.05 per demo
- **Claude (Vertex AI):** $3.00 per million input tokens, $15.00 per million output tokens
  - Estimate: ~$0.15 per demo (if using Claude for all agents)
- **BigQuery Storage:** ~$0.02/GB/month (demo datasets are small, <1GB)
- **BigQuery Queries:** First 1TB/month free

**Total estimated cost per demo: $0.20 - $0.35**

---

## 📞 Support & Resources

### **Official Documentation**

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

### **Internal Resources**

- Benchmark Guide: `benchmarks/AGENT_SELECTOR_GUIDE.md`
- Testing Framework: `TESTING_FRAMEWORK_SUMMARY.md`
- Research Agent V2: `RESEARCH_AGENT_V2_README.md`
- Timestamp Fix Notes: `TIMESTAMP_FIX_APPLIED.md`
- V2 Data Generation Plan: `SYNTHETIC_DATA_V2_PLAN.md`

### **Quick Commands Reference**

```bash
# Deploy
./deploy-to-cloudrun.sh prod

# View logs
gcloud run logs tail demo-gen-capi-prod --region us-central1

# Update env vars
gcloud run services update demo-gen-capi-prod \
  --set-env-vars "DEMO_NUM_QUERIES=3" \
  --region us-central1

# Scale resources
gcloud run services update demo-gen-capi-prod \
  --memory 8Gi --cpu 4 \
  --region us-central1

# View service details
gcloud run services describe demo-gen-capi-prod \
  --region us-central1

# Delete service
gcloud run services delete demo-gen-capi-prod \
  --region us-central1
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-06
**Author:** Generated from codebase analysis
**Status:** Production-ready

---

## 🔄 Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-06 | 1.0 | Initial comprehensive guide |

---

**END OF DEPLOYMENT GUIDE**
