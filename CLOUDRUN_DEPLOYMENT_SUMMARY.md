# ☁️ Cloud Run Deployment Summary

**Date:** 2025-10-06
**Status:** ✅ DEPLOYED & WORKING

---

## 🎯 Current Deployment

### Production Service
- **Service Name:** `demo-gen-capi`
- **Region:** **us-east5** (IMPORTANT: Claude Sonnet 4.5 only available here!)
- **URL:** https://demo-gen-capi-549403515075.us-east5.run.app
- **Resources:** 4Gi memory, 2 CPU, 60min timeout
- **Status:** ✅ Running

### Environment Variables
```bash
PROJECT_ID=bq-demos-469816
LOCATION=us-east5          # ⚠️ MUST match deployment region!
ENVIRONMENT=prod
RESEARCH_AGENT_MODEL=gemini
DEMO_STORY_AGENT_MODEL=gemini
DATA_MODELING_AGENT_MODEL=claude    # Requires us-east5
CAPI_AGENT_MODEL=claude             # Requires us-east5
DEMO_NUM_QUERIES=6
DEMO_NUM_SCENES=4
DEMO_NUM_ENTITIES=8
V2_MAX_PAGES=30
V2_MAX_DEPTH=2
```

---

## ⚠️ Common Issues

### Issue 1: "Claude model not servable in us-central1"

**Error:**
```
Publisher Model `claude-sonnet-4-5@20250929` is not servable in region us-central1
```

**Cause:** Claude Sonnet 4.5 is only available in specific regions:
- ✅ us-east5
- ❌ us-central1
- ❌ us-west1

**Solution:** Always deploy to `us-east5`:
```bash
gcloud run deploy demo-gen-capi \
  --region=us-east5 \          # ← Region here
  --set-env-vars "LOCATION=us-east5"  # ← Must match!
```

### Issue 2: Wrong URL being used

**Symptom:** Provisioning fails with region error even after deploying to us-east5

**Cause:** Old service in us-central1 still exists, users hitting wrong URL

**Solution:**
```bash
# Delete old service
gcloud run services delete demo-gen-capi --region=us-central1

# Use correct URL
https://demo-gen-capi-549403515075.us-east5.run.app
```

---

## 🚀 Deployment Commands

### Full Deployment
```bash
cd /home/admin_/final_demo/capi/demo-gen-capi

gcloud run deploy demo-gen-capi \
  --source . \
  --region=us-east5 \
  --memory=4Gi \
  --cpu=2 \
  --timeout=3600 \
  --max-instances=10 \
  --allow-unauthenticated \
  --set-env-vars="\
PROJECT_ID=bq-demos-469816,\
LOCATION=us-east5,\
ENVIRONMENT=prod,\
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

### Quick Update (env vars only)
```bash
gcloud run services update demo-gen-capi \
  --region=us-east5 \
  --update-env-vars="DEMO_NUM_QUERIES=3"
```

### Check Current Config
```bash
gcloud run services describe demo-gen-capi \
  --region=us-east5 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

---

## 📊 Monitoring

### View Logs
```bash
# Stream logs
gcloud run logs tail demo-gen-capi --region=us-east5

# Filter for errors
gcloud run logs read demo-gen-capi \
  --region=us-east5 \
  --log-filter="severity>=ERROR" \
  --limit=50
```

### Check Service Status
```bash
# Health check
curl https://demo-gen-capi-549403515075.us-east5.run.app/health

# Start provisioning
curl -X POST https://demo-gen-capi-549403515075.us-east5.run.app/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.nike.com"}'
```

---

## 🔧 Fixes Applied

### 1. Dependencies
- ✅ Added `google-cloud-aiplatform>=1.38.0` (vertexai module)
- ✅ Pinned `anthropic[vertex]==0.40.0` (version conflict)

### 2. Docker Build
- ✅ Fixed PORT configuration (8000 → $PORT for Cloud Run)
- ✅ Excluded `backend/newfrontend` symlink from build
- ✅ Fixed `.dockerignore` to allow frontend source files

### 3. Data Generator
- ✅ Using `SyntheticDataGeneratorMarkdown` (LLM data, not Faker)
- ✅ Built-in safeguards prevent wrong generator import

### 4. Region Configuration
- ✅ Deployed to us-east5 (Claude available)
- ✅ LOCATION env var matches deployment region
- ✅ Deleted old us-central1 service

---

## 📦 Build Artifacts

- **Docker Image:** Built via Cloud Build in us-east5
- **Frontend:** React + Vite (built in multi-stage Dockerfile)
- **Backend:** FastAPI + Uvicorn on Python 3.11

---

## 🎯 Test Commands

### 1. Health Check
```bash
curl https://demo-gen-capi-549403515075.us-east5.run.app/health
```

**Expected:**
```json
{"status":"healthy","environment":"prod","timestamp":"2025-10-06T..."}
```

### 2. Start Provisioning
```bash
curl -X POST https://demo-gen-capi-549403515075.us-east5.run.app/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.nike.com"}' | jq
```

**Expected:**
```json
{
  "job_id": "...",
  "status": "pending",
  "message": "Provisioning workflow started",
  "customer_url": "https://www.nike.com/"
}
```

### 3. Check Status
```bash
curl https://demo-gen-capi-549403515075.us-east5.run.app/api/provision/status/JOB_ID | jq
```

---

## 📚 Related Documentation

- `CLOUDRUN_DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `CLOUDRUN_RECOMMENDATIONS_ACTIONABLE.md` - Best practices & optimizations
- `DATA_CORRUPTION_ROOT_CAUSE_ANALYSIS.md` - Data generator fix documentation
- `TIMESTAMP_FIX_APPLIED.md` - BigQuery timestamp formatting fix

---

**Last Updated:** 2025-10-06
**Maintained By:** Demo Gen CAPI Team
