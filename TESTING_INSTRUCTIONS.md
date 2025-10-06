# Testing Instructions - CE Workflow

## Quick Test: CE Dashboard → Provision → Chat Demo

### **Test 1: Start a Provision Job**

```bash
# Start provisioning for Shopify
curl -s -X POST https://capi-demo-549403515075.us-central1.run.app/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.shopify.com"}' | jq '.'
```

**Expected Response:**
```json
{
  "job_id": "some-uuid-here",
  "status": "pending",
  "message": "Provisioning workflow started",
  "customer_url": "https://www.shopify.com/"
}
```

**Save the job_id** for next steps!

---

### **Test 2: Monitor Progress (Run Every 30s)**

```bash
# Replace JOB_ID with your actual job_id
JOB_ID="your-job-id-here"

curl -s https://capi-demo-549403515075.us-central1.run.app/api/provision/status/$JOB_ID | jq '{
  status,
  current_phase,
  overall_progress,
  agents: [.agents[] | {name, status, progress: .progress_percentage}],
  recent_logs: [.recent_logs[-3:][].message]
}'
```

**Expected Output (running):**
```json
{
  "status": "running",
  "current_phase": "Demo Story Agent",
  "overall_progress": 28,
  "agents": [
    {"name": "Research Agent", "status": "completed", "progress": 100},
    {"name": "Demo Story Agent", "status": "running", "progress": 50},
    ...
  ],
  "recent_logs": [
    "Starting Demo Story Agent...",
    "Generating 12 golden queries..."
  ]
}
```

---

### **Test 3: Check When Complete (~10 minutes)**

```bash
# When status shows "completed", get the demo assets
curl -s https://capi-demo-549403515075.us-central1.run.app/api/provision/assets/$JOB_ID | jq '{
  status,
  demo_title,
  queries: [.golden_queries[] | {question, complexity}],
  schema: [.schema[] | {name, fieldCount}],
  dataset: .metadata.datasetId
}'
```

**Expected Output:**
```json
{
  "status": "completed",
  "demo_title": "Shopify Merchant Performance Analytics",
  "queries": [
    {"question": "What is our total GMV this month?", "complexity": "SIMPLE"},
    {"question": "Show top 10 merchants by revenue", "complexity": "MODERATE"}
  ],
  "schema": [
    {"name": "merchants", "fieldCount": 8},
    {"name": "orders", "fieldCount": 12}
  ],
  "dataset": "shopify_capi_demo_20251005"
}
```

---

### **Test 4: Access Chat Demo**

Once completed, the dataset is automatically configured as the active dataset.

**Option A: Browser**
1. Go to: https://capi-demo-549403515075.us-central1.run.app/
2. Try a golden query: "What is our total GMV this month?"
3. Should see chart and SQL

**Option B: API**
```bash
curl -s -X POST https://capi-demo-549403515075.us-central1.run.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is our total GMV this month?"}' | jq '.'
```

---

## Full CE Dashboard Workflow (Frontend)

### **Step 1: Open CE Dashboard**
```
https://capi-demo-549403515075.us-central1.run.app/ce-dashboard
```

### **Step 2: Choose Mode**
- **DEFAULT MODE**: Just enter `shopify.com` and click "Start Provision"
- **CRAZY FROG MODE**:
  - Enter URL
  - Add context: "Need CFO-focused fraud detection demo with transaction monitoring"
  - Select: Persona=CFO, Complexity=Advanced, Focus=Fraud
  - Click "Unleash the Frog"

### **Step 3: Watch Progress**
- Automatically redirects to `/provision-progress?jobId=xxx`
- See 7 agents execute in real-time
- Logs stream live
- Progress bar animates 0% → 100%

### **Step 4: View Demo Assets**
- Redirects to `/demo-assets?jobId=xxx`
- Browse golden queries
- View schema (tables and fields)
- See metadata
- Click "Launch Chat Interface"

### **Step 5: Present Demo**
- Chat interface opens with customer branding
- Test golden queries
- Show SQL in Developer Mode
- Demo complete!

---

## Monitoring & Debugging

### **Check Cloud Run Logs**
```bash
# All recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=capi-demo" \
  --project=bq-demos-469816 --limit=50 --format="value(textPayload,jsonPayload.message)" --freshness=10m

# Errors only
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=capi-demo AND severity=ERROR" \
  --project=bq-demos-469816 --limit=20 --format=json --freshness=10m
```

### **Check Job History**
```bash
curl -s https://capi-demo-549403515075.us-central1.run.app/api/provision/history | jq '{
  total,
  recent: [.jobs[0:3][] | {job_id: .job_id[0:8], status, customer_url, total_time}]
}'
```

---

## Troubleshooting

### **Job Fails Immediately**
Check errors:
```bash
curl -s https://capi-demo-549403515075.us-central1.run.app/api/provision/status/$JOB_ID | jq '.errors'
```

Common issues:
- Missing API key: Check Cloud Run env vars have `GEMINI_API_KEY`
- Network error: Website unreachable
- Quota exceeded: GCP API limits hit

### **Job Hangs on One Agent**
```bash
# Check which agent is stuck
curl -s https://capi-demo-549403515075.us-central1.run.app/api/provision/status/$JOB_ID | jq '.agents[] | select(.status=="running")'
```

### **SSE Stream Not Working**
Test SSE directly:
```bash
curl -N https://capi-demo-549403515075.us-central1.run.app/api/provision/stream/$JOB_ID
```
Should see `data: {...}` events streaming every 2-3 seconds

---

## Current Status

**Service URL:** https://capi-demo-549403515075.us-central1.run.app

**Latest Fixes Applied:**
1. ✅ API routing fixed (no more HTML for JSON endpoints)
2. ✅ LangGraph node naming conflict fixed
3. ✅ crazy_frog_context default added
4. ✅ GEMINI_API_KEY configured in Cloud Run

**Build Status:** Check with:
```bash
gcloud builds list --limit=1 --project=bq-demos-469816 --format="value(id,status,duration)"
```

**Current Revision:** Will be `capi-demo-00026-xxx` after next deployment

---

## Expected Timeline

**Full Shopify Provision:**
- Research Agent: ~30s
- Demo Story Agent: ~1-2 min (generates golden queries)
- Data Modeling Agent: ~1 min (designs schema)
- Synthetic Data Generator: ~2-3 min (creates realistic data)
- Infrastructure Agent: ~2-3 min (provisions BigQuery)
- CAPI Instruction Generator: ~30s (creates YAML)
- Demo Validator: ~1-2 min (tests queries)

**Total:** ~8-12 minutes

---

## Quick Reference

```bash
# Environment
SERVICE_URL="https://capi-demo-549403515075.us-central1.run.app"

# Start provision
JOB_ID=$(curl -s -X POST $SERVICE_URL/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.shopify.com"}' | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# Monitor (run in loop)
watch -n 10 "curl -s $SERVICE_URL/api/provision/status/$JOB_ID | jq '.status, .current_phase, .overall_progress'"

# Get assets when done
curl -s $SERVICE_URL/api/provision/assets/$JOB_ID | jq '.'
```

Happy Testing! 🚀
