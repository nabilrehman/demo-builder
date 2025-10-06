# 🚀 CloudRun Deployment Plan - Service: "demo-generation"

**Created:** 2025-10-06
**Target Service:** demo-generation
**Project:** bq-demos-469816
**Region:** us-central1

---

## 📊 Current State Analysis

### ✅ Codebase Status: READY TO DEPLOY

**No code changes needed** - Everything is working perfectly!

#### Application Structure:
```
demo-gen-capi/
├── backend/                          # Python FastAPI backend
│   ├── api.py                        # Main API entry point
│   ├── requirements.txt              # All dependencies ✅
│   ├── agentic_service/
│   │   ├── demo_orchestrator.py      # LangGraph orchestration ✅
│   │   ├── agents/
│   │   │   ├── synthetic_data_generator_markdown.py  # ✅ CORRECT VERSION
│   │   │   ├── _deleted_do_not_use/  # ✅ Deprecated code isolated
│   │   │   └── ... (15 other agents)
│   │   └── config/
│   │       └── agent_config.py       # Model selection
│   └── routes/
│       └── provisioning.py           # API routes
├── newfrontend/                      # React/TypeScript/Vite frontend
│   └── conversational-api-demo-frontend/
│       ├── src/                      # React components
│       ├── dist/                     # Built frontend (created in Docker)
│       └── package.json
├── Dockerfile                        # Multi-stage build ✅
├── .dockerignore                     # Optimized ✅
└── scripts/
    └── pre-deploy-check.sh           # Safeguard checks ✅
```

### ✅ Safeguards Verification (All Passing)

Pre-deployment checks completed:

```
✅ Using correct SyntheticDataGeneratorMarkdown (8 occurrences)
✅ langgraph found
✅ google-cloud-aiplatform found
✅ anthropic found
✅ Dockerfile uses PORT env var correctly
✅ .dockerignore exists and excludes log files
✅ Deprecated code isolated in _deleted_do_not_use/
✅ Runtime safeguards active (lines 91-114, 421-434)

⚠️  WARNING: Logging to file (acceptable for now, CloudRun captures stdout)
⚠️  WARNING: CORS allows all origins (acceptable for demo)

RESULT: ✅ PASSED with 2 warnings (safe to deploy)
```

### 📦 Dependencies Status

**All critical dependencies present:**
- ✅ `langgraph>=0.0.50` (was missing, now fixed)
- ✅ `google-cloud-aiplatform>=1.38.0` (was missing, now fixed)
- ✅ `anthropic[vertex]==0.40.0`
- ✅ FastAPI, Uvicorn, Pydantic
- ✅ All Google Cloud libraries

### 🎯 Data Generator Configuration

**CONFIRMED: Using correct version**

Location: `backend/agentic_service/demo_orchestrator.py`
- Line 91: `from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown`
- Line 149: `synthetic_data_generator = SyntheticDataGeneratorMarkdown()`
- Line 421: Second occurrence in async method
- Line 469: Instantiation in async method

**Runtime safeguards:**
- Environment variable: `FORCE_LLM_DATA_GENERATION=true` (will be set)
- Auto-crash protection: App will refuse to start if wrong generator detected

---

## 🎯 Deployment Configuration

### Service Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Service Name** | `demo-generation` | As requested by user |
| **Project** | `bq-demos-469816` | Current GCP project |
| **Region** | `us-central1` | Same as existing services |
| **Memory** | `4Gi` | Handles LLM + data generation |
| **CPU** | `2` | Multi-agent pipeline |
| **Timeout** | `3600s` (1 hour) | Full demo provisioning |
| **Max Instances** | `10` | Concurrent demos |
| **Min Instances** | `0` | Cost optimization (cold start acceptable) |
| **Concurrency** | `1` | One demo per instance (resource intensive) |

### Environment Variables

**Production Configuration:**

```bash
# Core Configuration
PROJECT_ID=bq-demos-469816
LOCATION=us-central1
ENVIRONMENT=production

# 🛡️ CRITICAL SAFEGUARD
FORCE_LLM_DATA_GENERATION=true

# Agent Model Selection (Cost-optimized)
RESEARCH_AGENT_MODEL=gemini          # Fast, cheap, good quality
DEMO_STORY_AGENT_MODEL=gemini        # Fast, cheap, good quality
DATA_MODELING_AGENT_MODEL=claude     # Better schema design
CAPI_AGENT_MODEL=claude              # Required for YAML quality

# Demo Complexity (Standard)
DEMO_NUM_QUERIES=6
DEMO_NUM_SCENES=4
DEMO_NUM_ENTITIES=8

# Research Agent V2 Configuration
V2_MAX_PAGES=30
V2_MAX_DEPTH=2
V2_ENABLE_BLOG=false
V2_ENABLE_LINKEDIN=false
V2_ENABLE_YOUTUBE=false
```

**Why these values:**
- `FORCE_LLM_DATA_GENERATION=true`: **CRITICAL** - Ensures no Faker data
- `RESEARCH_AGENT_MODEL=gemini`: 2x faster than Claude, free tier available
- `DEMO_STORY_AGENT_MODEL=gemini`: No quality loss vs Claude, much faster
- `DATA_MODELING_AGENT_MODEL=claude`: Better at complex schema design
- `CAPI_AGENT_MODEL=claude`: MUST use Claude for YAML quality
- `DEMO_NUM_QUERIES=6`: Standard demo (6 golden queries)
- `V2_MAX_PAGES=30`: Good coverage without excessive cost

---

## 🚀 Deployment Steps

### Step 1: Pre-Deployment Verification (Already Done ✅)

```bash
bash scripts/pre-deploy-check.sh
# RESULT: ✅ PASSED
```

### Step 2: Deploy to CloudRun

**Command:**
```bash
gcloud run deploy demo-generation \
  --source . \
  --project bq-demos-469816 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 1 \
  --set-env-vars "\
PROJECT_ID=bq-demos-469816,\
LOCATION=us-central1,\
ENVIRONMENT=production,\
FORCE_LLM_DATA_GENERATION=true,\
RESEARCH_AGENT_MODEL=gemini,\
DEMO_STORY_AGENT_MODEL=gemini,\
DATA_MODELING_AGENT_MODEL=claude,\
CAPI_AGENT_MODEL=claude,\
DEMO_NUM_QUERIES=6,\
DEMO_NUM_SCENES=4,\
DEMO_NUM_ENTITIES=8,\
V2_MAX_PAGES=30,\
V2_MAX_DEPTH=2,\
V2_ENABLE_BLOG=false,\
V2_ENABLE_LINKEDIN=false,\
V2_ENABLE_YOUTUBE=false"
```

**What happens during deployment:**
1. Docker image built using multi-stage Dockerfile
2. Frontend built (Node.js stage)
3. Python dependencies installed
4. Frontend dist/ copied into backend
5. Image pushed to Google Container Registry
6. CloudRun service created/updated
7. Traffic routed to new revision

**Estimated time:** 5-8 minutes

### Step 3: Verification

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe demo-generation \
  --region us-central1 \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test health endpoint
curl -f $SERVICE_URL/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### Step 4: Check Logs for Safeguard Message

```bash
gcloud run services logs read demo-generation \
  --region us-central1 \
  --limit 30
```

**Look for:**
```
✅ Using correct data generator: SyntheticDataGeneratorMarkdown
🔒 FORCE_LLM_DATA_GENERATION=true - Faker fallback is DISABLED
```

**If you see this, STOP:**
```
❌ CRITICAL ERROR: Accidentally imported SyntheticDataGeneratorOptimized!
```

---

## 🧪 Post-Deployment Testing

### Test 1: Frontend Access

```bash
# Open in browser
open $SERVICE_URL
```

**Expected:**
- React frontend loads
- UI shows "CAPI Demo Generator"
- Can input customer URL

### Test 2: API Health Check

```bash
curl $SERVICE_URL/health
```

**Expected:**
```json
{"status": "healthy", "version": "1.0.0"}
```

### Test 3: Start Test Provisioning

```bash
curl -X POST $SERVICE_URL/api/provision/start \
  -H 'Content-Type: application/json' \
  -d '{"customer_url": "https://www.nike.com"}'
```

**Expected:**
```json
{
  "job_id": "uuid-here",
  "status": "started",
  "message": "Demo provisioning started"
}
```

### Test 4: Monitor Provisioning

```bash
JOB_ID="<job_id_from_above>"
curl $SERVICE_URL/api/provision/status/$JOB_ID
```

**Watch for in logs:**
```
🤖 Generating realistic data for products with Gemini 2.5 Pro...
🤖 Generating realistic data for customers with Gemini 2.5 Pro...
```

### Test 5: Verify Data Quality

After provisioning completes (15-20 minutes):

```bash
# Find the dataset
bq ls | grep nike_capi_demo

# Check data quality
bq head -n 3 nike_capi_demo_20251006.products
```

**GOOD data (success):**
```
title: "Nike Air Max 270 - Men's Running Shoes"
description: "Iconic sneaker featuring large Max Air unit..."
```

**BAD data (deployment failed):**
```
title: "new", "it", "option"
description: "relate", "past"
```

---

## 📊 Expected Costs

### Deployment Costs (One-time)
- Build time: ~5-8 minutes = **$0.00** (free tier)
- Storage: ~2GB image = **$0.05/month**

### Runtime Costs (Pay-per-use)

**Scenario 1: Low Usage (1-2 demos/week)**
- 8 demos/month × 20 min average × 4Gi memory = **~$3/month**
- Min instances = 0, so no idle costs

**Scenario 2: Medium Usage (1-2 demos/day)**
- 40 demos/month × 20 min average × 4Gi memory = **~$15/month**
- Still no idle costs with min instances = 0

**Scenario 3: High Usage (10+ demos/day)**
- 300 demos/month × 20 min average × 4Gi memory = **~$110/month**
- Consider min instances = 1 for cold start elimination (+$35/month)

**LLM Costs (Gemini + Claude):**
- Per demo: ~$0.10-0.15 (mostly Gemini which is cheaper)
- 40 demos/month: ~$6/month

**Total estimated cost (medium usage):**
- CloudRun: $15/month
- LLM: $6/month
- **Total: ~$21/month**

---

## 🔄 Comparison with Existing Service

| Aspect | `demo-gen-capi-prod` (existing) | `demo-generation` (new) |
|--------|--------------------------------|-------------------------|
| **Status** | Deployed | Will deploy |
| **Code** | Same codebase | Same codebase |
| **Safeguards** | ✅ Yes (just added) | ✅ Yes (same) |
| **Environment** | Production | Production |
| **Config** | Standard | Standard (identical) |

**Why deploy a new service?**
- User requested service named "demo-generation"
- Keeps existing service intact as backup
- Can A/B test if needed
- Easy rollback if issues

---

## 🛡️ Rollback Plan

If deployment fails or has issues:

### Option 1: Keep existing service

```bash
# demo-gen-capi-prod is already running
# Just don't route traffic to demo-generation
```

### Option 2: Delete new service

```bash
gcloud run services delete demo-generation \
  --region us-central1
```

### Option 3: Redeploy with fixes

```bash
# Fix issues in code
bash scripts/pre-deploy-check.sh
./deploy-to-cloudrun.sh
```

---

## ⚠️ Important Notes

### 1. **NO CODE CHANGES WILL BE MADE**

This deployment uses the **exact current code** which is working perfectly:
- ✅ All safeguards in place
- ✅ Correct data generator selected
- ✅ Dependencies complete
- ✅ Pre-deployment checks passing

### 2. **Multi-Stage Docker Build**

Dockerfile builds:
1. **Stage 1 (Node):** Builds React frontend → dist/
2. **Stage 2 (Python):** Installs backend, copies dist/

This ensures frontend is served by FastAPI.

### 3. **Port Configuration**

Dockerfile CMD:
```dockerfile
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

CloudRun sets `PORT` env var (usually 8080), app adapts automatically.

### 4. **Cold Start Time**

With `min-instances=0`:
- First request: ~30-45 seconds (image pull + container start)
- Subsequent requests: instant (container warm)

To eliminate cold starts: Set `--min-instances 1` (+$35/month)

---

## ✅ Deployment Checklist

Before deployment:

- [x] Pre-deployment checks passed
- [x] Correct data generator verified (SyntheticDataGeneratorMarkdown)
- [x] Runtime safeguards active (FORCE_LLM_DATA_GENERATION)
- [x] Dependencies complete (langgraph, google-cloud-aiplatform)
- [x] Dockerfile correct (PORT env var, multi-stage)
- [x] Environment variables defined
- [x] Deployment command prepared
- [x] Testing plan ready
- [x] Rollback plan documented

**Status: ✅ READY TO DEPLOY**

---

## 🎯 Deployment Plan Summary

**What we'll do:**
1. Deploy current code (no changes) to new CloudRun service "demo-generation"
2. Use same configuration as existing service
3. Set `FORCE_LLM_DATA_GENERATION=true` for safety
4. Test deployment with health check
5. Run test provisioning to verify data quality

**What we WON'T do:**
- ❌ Modify any code (it's working great!)
- ❌ Change existing services
- ❌ Remove safeguards
- ❌ Use deprecated code

**Expected outcome:**
- New service `demo-generation` running in 5-8 minutes
- Identical functionality to existing service
- All safeguards protecting against Faker data
- Ready for production use

---

## 📞 Next Steps

**Waiting for user approval to proceed with deployment.**

Once approved, I will:
1. Execute deployment command
2. Monitor build progress
3. Verify deployment
4. Test endpoints
5. Check logs for safeguard confirmation
6. Provide service URL and testing instructions

**Estimated total time: 10-15 minutes**

---

**Document Status:** ✅ COMPLETE - Ready for User Review
**Created:** 2025-10-06
**Author:** Claude Code Analysis
