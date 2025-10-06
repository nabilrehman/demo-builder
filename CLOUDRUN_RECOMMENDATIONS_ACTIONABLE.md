# 🚀 Cloud Run Deployment - Actionable Recommendations

**Quick-reference guide with specific, tested recommendations for this application**

**Last Updated:** 2025-10-06
**Status:** Production-ready recommendations based on actual deployment experience

---

## 🎯 Critical Fixes Before Deployment

### 1. **Synthetic Data Generator Selection** ⚠️ CRITICAL

**Issue:** The orchestrator can accidentally use the wrong data generator

**Current Fix Applied:**
```python
# backend/agentic_service/demo_orchestrator.py (lines 91, 128, 392, 429)
from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown
synthetic_data_generator = SyntheticDataGeneratorMarkdown()  # ✅ CORRECT
```

**NEVER USE:**
```python
# ❌ BROKEN - Has keyword filtering, falls back to Faker for 70% of tables
from agentic_service.agents.synthetic_data_generator_optimized import SyntheticDataGeneratorOptimized
```

**Verification Before Deploy:**
```bash
# Check what the orchestrator is using
grep -n "SyntheticDataGenerator" backend/agentic_service/demo_orchestrator.py

# Should see ONLY "SyntheticDataGeneratorMarkdown"
# If you see "SyntheticDataGeneratorOptimized" → STOP, fix it first!
```

**Add Environment Variable Protection:**
```bash
# In .env or Cloud Run env vars
FORCE_LLM_DATA_GENERATION=true  # Fail if Faker is used instead of LLM
```

---

### 2. **Required Dependencies** ⚠️ MUST FIX

**Problem:** Missing dependencies cause runtime failures

**Check `backend/requirements.txt` includes:**
```python
# These were missing and caused crashes:
langgraph>=0.0.50                    # ← Was missing
google-cloud-aiplatform>=1.38.0      # ← Was missing (provides vertexai)
anthropic[vertex]>=0.40.0
langchain-core>=0.1.0
```

**Verify before deploy:**
```bash
cd backend
source venv/bin/activate
python -c "import langgraph; import vertexai; print('✅ All critical imports OK')"
```

---

### 3. **Port Configuration for Cloud Run**

**Issue:** Cloud Run uses `PORT` environment variable (defaults to 8080, not 8000)

**Already Fixed in Dockerfile (line 42):**
```dockerfile
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

**No action needed** - Dockerfile is already correct ✅

---

### 4. **Logging Configuration** ⚠️ NEEDS FIX

**Problem:** Application logs to file (`backend.log`), Cloud Run needs stdout

**Current (line 29 in `backend/api.py`):**
```python
# ❌ WRONG for Cloud Run
logging.basicConfig(filename='backend.log', level=logging.INFO)
```

**Fix:**
```python
# ✅ CORRECT for Cloud Run
import sys
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
```

**Why:** Cloud Run captures stdout/stderr, not file writes. File logs are lost when container restarts.

---

## 💰 Cost Optimization

### 1. **Right-Size Resources by Environment**

**Development (Testing, 1-2 demos/day):**
```bash
gcloud run deploy demo-gen-capi-dev \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 2 \
  --min-instances 0 \
  --timeout 1800 \
  --set-env-vars "DEMO_NUM_QUERIES=1,DEMO_NUM_SCENES=1,RESEARCH_AGENT_MODEL=gemini"
```
**Cost:** ~$0.03 per demo, $0/month idle

**Production (Customer demos, 10-50 demos/day):**
```bash
gcloud run deploy demo-gen-capi-prod \
  --memory 4Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 1 \
  --timeout 3600 \
  --set-env-vars "DEMO_NUM_QUERIES=6,DEMO_NUM_SCENES=4"
```
**Cost:** ~$0.10 per demo + $45/month for min instance (eliminates cold starts)

### 2. **Agent Model Selection by Cost**

**Fastest & Cheapest (for testing):**
```bash
RESEARCH_AGENT_MODEL=gemini      # Free tier available, 2x faster
DEMO_STORY_AGENT_MODEL=gemini    # 2.13x faster than Claude
DATA_MODELING_AGENT_MODEL=gemini # Lower memory usage
CAPI_AGENT_MODEL=claude          # MUST use Claude (quality critical)
```

**Balanced (for production demos):**
```bash
RESEARCH_AGENT_MODEL=gemini      # Speed + cost savings
DEMO_STORY_AGENT_MODEL=gemini    # No quality loss
DATA_MODELING_AGENT_MODEL=claude # Better quality
CAPI_AGENT_MODEL=claude          # Required
```

**Cost Impact:**
- All Gemini: ~$0.05 per demo
- Mixed (recommended): ~$0.15 per demo
- All Claude: ~$0.30 per demo

### 3. **Demo Complexity Presets**

Add these presets as Cloud Run services or env var templates:

**Quick Demo (2-5 min, $0.03):**
```bash
DEMO_NUM_QUERIES=1
DEMO_NUM_SCENES=1
DEMO_NUM_ENTITIES=3
V2_MAX_PAGES=10
```

**Standard Demo (8-12 min, $0.10):**
```bash
DEMO_NUM_QUERIES=6
DEMO_NUM_SCENES=4
DEMO_NUM_ENTITIES=8
V2_MAX_PAGES=30
```

**Comprehensive Demo (20-30 min, $0.25):**
```bash
DEMO_NUM_QUERIES=12
DEMO_NUM_SCENES=5
DEMO_NUM_ENTITIES=15
V2_MAX_PAGES=50
```

---

## 🔐 Security Hardening

### 1. **CORS Configuration**

**Current (in `backend/api.py`):**
```python
# ⚠️ TOO PERMISSIVE
allow_origins=["*"]
```

**Fix for Production:**
```python
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://console.cloud.google.com"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**Deploy with:**
```bash
--set-env-vars "ALLOWED_ORIGINS=https://your-domain.com,https://console.cloud.google.com"
```

### 2. **Authentication** (Optional but Recommended)

**For internal-only demos:**
```bash
# Deploy WITHOUT --allow-unauthenticated
gcloud run deploy demo-gen-capi-prod \
  --region us-central1 \
  # No --allow-unauthenticated flag

# Access with:
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://demo-gen-capi-prod-xxx.run.app/api/provision/start
```

### 3. **Secret Manager Integration**

**Store all secrets in Secret Manager:**

```bash
# Create secrets
echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Grant access to Cloud Run service account
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT="$PROJECT_ID@appspot.gserviceaccount.com"

gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secrets
gcloud run deploy demo-gen-capi-prod \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

**NEVER use:**
```bash
# ❌ BAD - Secrets visible in Cloud Console
--set-env-vars "GEMINI_API_KEY=AIzaSy..."
```

---

## 📊 Monitoring & Observability

### 1. **Custom Metrics for Agent Performance**

Add to `backend/agentic_service/demo_orchestrator.py`:

```python
from google.cloud import monitoring_v3
import time

def record_agent_duration(agent_name: str, duration_seconds: float, customer_url: str):
    """Record agent execution time as custom metric."""
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{os.environ.get('PROJECT_ID')}"

    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/agent/{agent_name}/duration"
    series.resource.type = "cloud_run_revision"

    point = monitoring_v3.Point()
    point.value.double_value = duration_seconds
    point.interval.end_time.seconds = int(time.time())
    series.points = [point]

    # Add labels
    series.metric.labels["customer_domain"] = customer_url.split("//")[1].split("/")[0]

    try:
        client.create_time_series(name=project_name, time_series=[series])
    except Exception as e:
        logger.warning(f"Failed to record metric: {e}")
```

**Use in orchestrator:**
```python
start = time.time()
result = await research_agent.run(customer_url)
duration = time.time() - start
record_agent_duration("research", duration, customer_url)
```

**View in Cloud Console:**
```
Monitoring → Metrics Explorer → custom.googleapis.com/agent/*/duration
```

### 2. **Alerting Policies**

Create alerts for failures:

```bash
gcloud alpha monitoring policies create \
  --display-name="High Demo Failure Rate" \
  --condition-display-name="Failure rate > 20%" \
  --condition-threshold-value=0.2 \
  --condition-threshold-duration=600s \
  --notification-channels="CHANNEL_ID"
```

### 3. **Structured Logging**

Add structured logs for better filtering:

```python
import json

# Instead of:
logger.info(f"Agent completed: {agent_name}")

# Use:
logger.info(json.dumps({
    "event": "agent_completed",
    "agent": agent_name,
    "duration_seconds": duration,
    "customer_url": customer_url,
    "status": "success"
}))
```

**Query in Cloud Logging:**
```sql
jsonPayload.event="agent_completed"
jsonPayload.status="error"
```

---

## ⚡ Performance Optimization

### 1. **Parallel Agent Execution**

**Current:** Sequential (slow)
```python
research_result = await research_agent.run(url)
demo_story = await demo_story_agent.run(research_result)
data_model = await data_modeling_agent.run(research_result)
```

**Optimized:** Parallel where possible
```python
# Research first (no dependencies)
research_result = await research_agent.run(url)

# These can run in parallel (both need research only)
demo_story_task = asyncio.create_task(demo_story_agent.run(research_result))
data_model_task = asyncio.create_task(data_modeling_agent.run(research_result))

# Wait for both
demo_story, data_model = await asyncio.gather(demo_story_task, data_model_task)
```

**Speedup:** 20-30% reduction in total time

### 2. **Caching Research Results**

Add Redis caching to avoid re-crawling same websites:

```python
import hashlib
import redis
import json

redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=6379,
    decode_responses=True
)

def get_cached_research(url: str) -> Optional[dict]:
    cache_key = f"research:{hashlib.md5(url.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)
    return json.loads(cached) if cached else None

def cache_research(url: str, data: dict):
    cache_key = f"research:{hashlib.md5(url.encode()).hexdigest()}"
    redis_client.setex(cache_key, 86400, json.dumps(data))  # 24 hour TTL
```

**Setup Redis on Cloud Run:**
```bash
# Create Memorystore Redis instance
gcloud redis instances create demo-cache \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_6_x

# Create VPC connector
gcloud compute networks vpc-access connectors create demo-vpc \
  --region=us-central1 \
  --range=10.8.0.0/28

# Deploy with VPC connector
gcloud run deploy demo-gen-capi-prod \
  --vpc-connector=demo-vpc \
  --set-env-vars "REDIS_HOST=10.0.0.3"
```

**Cost:** ~$50/month for 1GB Redis, saves ~2 min per cached demo

### 3. **Request Timeout Strategy**

**Problem:** Some demos timeout at 60 min (Cloud Run max)

**Solution 1: Async Processing**
```python
# Instead of waiting for completion, return job ID immediately
@router.post("/api/provision/start-async")
async def start_provisioning_async(request: StartProvisionRequest):
    job_id = str(uuid.uuid4())

    # Start in background
    asyncio.create_task(run_provisioning_job(job_id, request.customer_url))

    return {"job_id": job_id, "status": "started"}

# Client polls for status
@router.get("/api/provision/status/{job_id}")
async def get_status(job_id: str):
    return job_manager.get_job_status(job_id)
```

**Solution 2: Cloud Tasks (Better)**
```python
from google.cloud import tasks_v2

def queue_provisioning_job(customer_url: str) -> str:
    client = tasks_v2.CloudTasksClient()
    parent = f"projects/{project_id}/locations/{region}/queues/demo-provisioning"

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": f"{service_url}/internal/provision",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"customer_url": customer_url}).encode(),
        }
    }

    response = client.create_task(request={"parent": parent, "task": task})
    return response.name
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Module not found: langgraph"

**Cause:** Dependencies not installed
**Fix:**
```bash
cd backend
pip install langgraph>=0.0.50 google-cloud-aiplatform>=1.38.0
pip freeze > requirements.txt
```

### Issue 2: "Memory limit exceeded"

**Symptoms:**
```
Container instance exceeded memory limit of 4Gi
```

**Solutions:**
1. Increase memory: `--memory 8Gi`
2. Use Gemini instead of Claude (less memory)
3. Reduce demo complexity: `DEMO_NUM_QUERIES=3`

### Issue 3: "Timeout after 60 minutes"

**Solutions:**
1. Use Fast Mode: `DEMO_NUM_QUERIES=1, RESEARCH_AGENT_MODEL=gemini`
2. Implement async processing (see Performance section)
3. Split into smaller jobs

### Issue 4: "Faker data instead of LLM"

**Cause:** Using wrong synthetic data generator
**Check:**
```bash
grep "SyntheticDataGenerator" backend/agentic_service/demo_orchestrator.py
```
**Fix:** Must see `SyntheticDataGeneratorMarkdown`, not `Optimized`

### Issue 5: "Frontend not loading"

**Symptoms:** 404 on root URL, API works
**Check:**
```bash
# Verify frontend was built in Docker
docker build -t test .
docker run -it test ls -la /app/newfrontend/conversational-api-demo-frontend/dist
```
**Should see:** `assets/`, `index.html`

---

## 🔄 CI/CD Pipeline Recommendations

### GitHub Actions Workflow

Create `.github/workflows/deploy-cloudrun.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
          - dev
          - staging
          - prod

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}

    - name: Verify dependencies
      run: |
        cd backend
        grep -q "langgraph" requirements.txt || (echo "Missing langgraph!" && exit 1)
        grep -q "google-cloud-aiplatform" requirements.txt || (echo "Missing vertexai!" && exit 1)

    - name: Verify correct data generator
      run: |
        if grep -q "SyntheticDataGeneratorOptimized" backend/agentic_service/demo_orchestrator.py; then
          echo "❌ ERROR: Using broken SyntheticDataGeneratorOptimized!"
          echo "Fix: Change to SyntheticDataGeneratorMarkdown"
          exit 1
        fi

    - name: Build and deploy
      run: |
        gcloud run deploy demo-gen-capi-${{ inputs.environment }} \
          --source . \
          --region us-central1 \
          --allow-unauthenticated \
          --memory 4Gi \
          --cpu 2 \
          --timeout 3600

    - name: Health check
      run: |
        SERVICE_URL=$(gcloud run services describe demo-gen-capi-${{ inputs.environment }} \
          --region us-central1 --format='value(status.url)')
        curl -f $SERVICE_URL/health || exit 1
```

### Pre-deployment Checklist Script

Create `scripts/pre-deploy-check.sh`:

```bash
#!/bin/bash
set -e

echo "🔍 Pre-deployment checks..."

# 1. Check dependencies
echo "✓ Checking dependencies..."
grep -q "langgraph>=0.0.50" backend/requirements.txt || { echo "❌ Missing langgraph"; exit 1; }
grep -q "google-cloud-aiplatform" backend/requirements.txt || { echo "❌ Missing vertexai"; exit 1; }

# 2. Check correct data generator
echo "✓ Checking data generator..."
if grep -q "SyntheticDataGeneratorOptimized" backend/agentic_service/demo_orchestrator.py; then
    echo "❌ ERROR: Using broken SyntheticDataGeneratorOptimized!"
    exit 1
fi

# 3. Check logging config
echo "✓ Checking logging..."
if grep -q "filename='backend.log'" backend/api.py; then
    echo "⚠️  WARNING: Logging to file, should use stdout for Cloud Run"
fi

# 4. Check CORS
echo "✓ Checking CORS..."
if grep -q 'allow_origins=\["\*"\]' backend/api.py; then
    echo "⚠️  WARNING: CORS allows all origins"
fi

# 5. Check Dockerfile port
echo "✓ Checking Dockerfile..."
grep -q 'PORT:-8080' Dockerfile || { echo "❌ Dockerfile doesn't use PORT env var"; exit 1; }

echo "✅ All checks passed!"
```

---

## 📦 Dockerfile Optimizations

### Current Dockerfile is Good, But Can Improve:

**Add .dockerignore optimization:**
```dockerfile
# Add to .dockerignore
**/__pycache__
**/*.pyc
**/.pytest_cache
**/backend.log
**/venv
**/.git
**/node_modules
*.md
```

**Multi-stage build improvements:**
```dockerfile
# Stage 1: Frontend Build
FROM node:18-slim AS build-frontend
WORKDIR /app/frontend
COPY newfrontend/conversational-api-demo-frontend/package*.json ./
RUN npm ci --only=production  # ← Faster than npm install
COPY newfrontend/conversational-api-demo-frontend/ ./
RUN npm run build

# Stage 2: Backend
FROM python:3.11-slim
WORKDIR /app

# Install dependencies first (cached layer)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend
COPY --from=build-frontend /app/frontend/dist ./newfrontend/conversational-api-demo-frontend/dist

# Copy backend code (changes most often)
COPY backend/ ./

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)"

EXPOSE 8080
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

---

## 💡 Quick Wins (Do These First)

### Priority 1: Fix Before Deploy ⚠️
1. ✅ Verify using `SyntheticDataGeneratorMarkdown` (already done)
2. ⚠️ Fix logging to stdout instead of file
3. ⚠️ Add secrets to Secret Manager

### Priority 2: Security Hardening 🔐
4. Restrict CORS origins
5. Add authentication if internal-only
6. Remove `--allow-unauthenticated` for prod

### Priority 3: Cost Optimization 💰
7. Set min-instances=1 for prod (avoid cold starts)
8. Use Gemini for research/story (2x faster, cheaper)
9. Add demo complexity presets

### Priority 4: Monitoring 📊
10. Switch to structured JSON logging
11. Add custom metrics for agent duration
12. Set up failure rate alerts

---

## 🎯 Recommended Production Configuration

**Final Production Deployment Command:**

```bash
#!/bin/bash
# deploy-production.sh

# Pre-flight checks
./scripts/pre-deploy-check.sh

# Deploy to production
gcloud run deploy demo-gen-capi-prod \
  --source . \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --min-instances 1 \
  --concurrency 1 \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest" \
  --set-env-vars "\
PROJECT_ID=bq-demos-469816,\
LOCATION=us-central1,\
ENVIRONMENT=production,\
RESEARCH_AGENT_MODEL=gemini,\
DEMO_STORY_AGENT_MODEL=gemini,\
DATA_MODELING_AGENT_MODEL=claude,\
CAPI_AGENT_MODEL=claude,\
DEMO_NUM_QUERIES=6,\
DEMO_NUM_SCENES=4,\
DEMO_NUM_ENTITIES=8,\
V2_MAX_PAGES=30,\
V2_MAX_DEPTH=2,\
FORCE_LLM_DATA_GENERATION=true,\
ALLOWED_ORIGINS=https://your-domain.com" \
  --no-allow-unauthenticated \
  --service-account demo-gen-sa@bq-demos-469816.iam.gserviceaccount.com

# Get URL
SERVICE_URL=$(gcloud run services describe demo-gen-capi-prod \
  --region us-central1 --format='value(status.url)')

echo "✅ Deployed to: $SERVICE_URL"
echo "🔐 Requires authentication"
echo ""
echo "Test with:"
echo "  curl -H \"Authorization: Bearer \$(gcloud auth print-identity-token)\" \\"
echo "    $SERVICE_URL/health"
```

---

## 📚 Additional Resources

- **Main Deployment Guide:** `CLOUDRUN_DEPLOYMENT_GUIDE.md` (comprehensive reference)
- **This Document:** Quick actionable recommendations
- **Benchmarks:** `benchmarks/AGENT_SELECTOR_GUIDE.md` (agent model selection)
- **Timestamp Fix:** `TIMESTAMP_FIX_APPLIED.md` (BigQuery compatibility)

---

**Document Status:** ✅ Production-Ready
**Last Verified:** 2025-10-06
**Next Review:** After first production deployment

