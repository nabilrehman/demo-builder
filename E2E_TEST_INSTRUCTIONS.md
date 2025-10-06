# End-to-End Testing Instructions

## ⚠️ CURRENT STATUS (2025-10-05)

**Active Revision:** capi-demo-00037-vwh (rolled back)
**Service URL:** https://capi-demo-cuxcxfhcya-uc.a.run.app

**Known Issues:**
- ✅ Pipeline DOES work - agents execute successfully
- ⚠️ Service becomes unresponsive during long operations
- ⚠️ Application logs not visible in Cloud Logging (only job state)
- 📋 See `CURRENT_STATUS.md` for detailed investigation notes

**Original Deployed Version:** Revision capi-demo-00033-sb5
**Original Service URL:** https://capi-demo-549403515075.us-central1.run.app (deprecated)

---

## 🎯 What Was Implemented (Option 2: Automatic CAPI Agent Creation)

### Backend Changes:

1. **Infrastructure Agent** (`infrastructure_agent.py`)
   - ✅ Added automatic CAPI Data Agent creation
   - ✅ Uses YAML system instructions from CAPI Instructions Agent
   - ✅ Links agent to provisioned BigQuery dataset
   - ✅ Returns agent_id and stores in state

2. **Chat Endpoint** (`api.py`)
   - ✅ Updated `ChatRequest` model to accept optional `agent_id` and `dataset_id`
   - ✅ Dynamic routing: uses provided IDs or falls back to env vars
   - ✅ Logs which agent and dataset are being used

3. **Demo Orchestrator** (`demo_orchestrator.py`)
   - ✅ Added `agentId` to metadata sent to frontend
   - ✅ Metadata now includes: `datasetId`, `datasetFullName`, `projectId`, `agentId`

### Frontend Changes:

4. **Index.tsx** (Chat Interface)
   - ✅ Extracts `agent_id` and `dataset_id` from URL params
   - ✅ Passes them to chat API in request body
   - ✅ Supports both snake_case and camelCase param names

5. **ProvisionProgress.tsx**
   - ✅ "Launch Chat Interface" button now passes `agent_id` and `dataset_id` as URL params
   - ✅ Format: `/?agent_id={agentId}&dataset_id={datasetId}`

---

## 🧪 End-to-End Testing Steps

### **Step 1: Start Provisioning**

1. Open CE Dashboard:
   ```
   https://capi-demo-549403515075.us-central1.run.app/ce-dashboard
   ```

2. Enter a test URL (recommended):
   ```
   https://www.stripe.com
   ```
   Or any other company website

3. Click **"Start Provision"**
   - Should redirect to progress page
   - URL should include `jobId` parameter

---

### **Step 2: Monitor Progress**

Watch the progress page for 3-5 minutes:

**Expected Stages:**
1. ✅ Research (analyze website)
2. ✅ Demo Story (create narrative + golden queries)
3. ✅ Data Modeling (design BigQuery schema)
4. ✅ Synthetic Data (generate CSV data)
5. ✅ Infrastructure (create dataset + **CREATE CAPI AGENT**)
6. ✅ CAPI Instructions (generate YAML)
7. ✅ Validation (test SQL queries)

**Key Log to Watch For (Stage 5):**
```
Creating CAPI Data Agent...
✅ Created CAPI Data Agent: {agent_id}
   Display Name: Stripe CAPI Demo Agent {timestamp}
   Dataset: bq-demos-469816.stripe_capi_demo_{date}
```

---

### **Step 3: Verify Completion Metadata**

When provisioning completes, the metadata should include:
- ✅ `datasetId`: e.g., `stripe_capi_demo_20251005`
- ✅ `agentId`: e.g., `abc123def456` (the created CAPI agent ID)
- ✅ `projectId`: `bq-demos-469816`

Check the completion card shows all three buttons:
- "Open BigQuery Console"
- "View Demo Assets"
- "Launch Chat Interface" ← **This is the critical one**

---

### **Step 4: Launch Chat Interface**

1. Click **"Launch Chat Interface"** button

2. Verify URL includes parameters:
   ```
   https://capi-demo-549403515075.us-central1.run.app/?agent_id=abc123def456&dataset_id=stripe_capi_demo_20251005
   ```

3. The chat interface should load with the company branding

---

### **Step 5: Test Chat with Golden Queries**

1. **Get golden queries** from the demo story:
   - Go back to progress page
   - Or check `/tmp/demo_story_stripe.json` for golden queries

2. **Test a simple query first:**
   ```
   Show me total revenue by month
   ```

3. **Expected behavior:**
   - Chat should send request to `/api/chat` with:
     ```json
     {
       "message": "Show me total revenue by month",
       "agent_id": "abc123def456",
       "dataset_id": "stripe_capi_demo_20251005"
     }
     ```
   - Backend should use the **provisioned agent** (not default)
   - Backend should query the **provisioned dataset** (not leagueapps_demo)

4. **Check backend logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=capi-demo" \
     --project=bq-demos-469816 --limit=20 --format="value(textPayload)" --freshness=5m
   ```

   Look for:
   ```
   Received request: Show me total revenue by month
   Using agent: abc123def456, dataset: stripe_capi_demo_20251005
   ```

5. **Verify response:**
   - Should return data from the NEW dataset
   - Should include chart visualization (Vega-Lite spec)
   - Should show SQL query in developer mode

---

## 🔍 Debugging Steps

### If CAPI agent creation fails:

**Check logs for errors:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=capi-demo AND (textPayload=~'.*CAPI.*' OR textPayload=~'.*agent.*')" \
  --project=bq-demos-469816 --limit=30 --format="value(textPayload)" --freshness=10m
```

**Common issues:**
- ❌ Missing permissions for `geminidataanalytics` API
- ❌ YAML content not found in state
- ❌ Invalid dataset reference

**Fallback behavior:**
- If agent creation fails, it logs a warning and returns empty string
- Provisioning continues (doesn't fail entire pipeline)
- You'll need to create agent manually

---

### If chat doesn't use provisioned data:

**Check URL params:**
```javascript
// Open browser console on chat page:
const params = new URLSearchParams(window.location.search);
console.log('agent_id:', params.get('agent_id'));
console.log('dataset_id:', params.get('dataset_id'));
```

**Check API request:**
```javascript
// In Network tab, find /api/chat request
// Verify request body includes:
{
  "message": "...",
  "agent_id": "abc123def456",
  "dataset_id": "stripe_capi_demo_20251005"
}
```

**Check backend logs:**
```bash
# Should show dynamic values, not defaults:
Using agent: abc123def456, dataset: stripe_capi_demo_20251005

# NOT:
Using agent: default_agent, dataset: leagueapps_demo
```

---

## 🎯 Success Criteria

✅ **Provisioning succeeds** with all 7 stages complete

✅ **CAPI agent is created automatically**
   - Log shows: "Created CAPI Data Agent: {id}"
   - Agent ID is stored in metadata

✅ **Chat button passes IDs** via URL params

✅ **Chat interface receives IDs** and passes to API

✅ **Backend uses dynamic IDs** (logs confirm)

✅ **Queries return data** from provisioned dataset

✅ **Visualizations render** from CAPI response

---

## 📊 Expected Flow Diagram

```
CE Dashboard (enter URL)
    ↓
/api/provision/start (create job)
    ↓
Progress Page (SSE logs, 7 stages)
    ↓
Stage 5: Infrastructure Agent
    ├── Create BigQuery dataset
    ├── Load data into tables
    └── ✨ Create CAPI Data Agent ✨
    ↓
Completion (metadata with agentId)
    ↓
"Launch Chat Interface" button
    ↓
Navigate to: /?agent_id=X&dataset_id=Y
    ↓
Chat Interface extracts params
    ↓
Send to /api/chat with agent_id, dataset_id
    ↓
Backend uses provisioned agent & dataset
    ↓
✅ Chat returns data from NEW dataset!
```

---

## 🚀 Quick Test Commands

### 1. Start a test provision:
```bash
curl -X POST https://capi-demo-549403515075.us-central1.run.app/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.stripe.com"}'
```

### 2. Check job status:
```bash
curl -s https://capi-demo-549403515075.us-central1.run.app/api/provision/status/{job_id} | jq '.metadata'
```

### 3. Verify agent creation logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=capi-demo AND textPayload=~'.*Created CAPI.*'" \
  --project=bq-demos-469816 --limit=5 --format="value(textPayload)" --freshness=10m
```

### 4. Test chat with params:
```bash
curl -X POST https://capi-demo-549403515075.us-central1.run.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me total revenue",
    "agent_id": "YOUR_AGENT_ID",
    "dataset_id": "YOUR_DATASET_ID"
  }'
```

---

## 📋 What to Report

After testing, please provide:

1. **Job ID** of test provision
2. **Agent ID** that was created (from logs or metadata)
3. **Dataset ID** that was created
4. **Chat query test results**:
   - Did it use the right agent?
   - Did it query the right dataset?
   - Did it return data?
   - Did visualizations render?
5. **Any errors** encountered (with logs)

---

## 🎉 Expected Result

**Full E2E flow working:**

1. ✅ CE enters URL → provision starts
2. ✅ 7 agents run successfully
3. ✅ CAPI agent created automatically
4. ✅ Completion metadata includes agent_id
5. ✅ Chat button launches with correct params
6. ✅ Chat queries use provisioned agent & dataset
7. ✅ Responses show data from NEW dataset
8. ✅ No manual CAPI agent creation needed!

**Time saved:** ~10-15 minutes per demo (no manual agent setup)

---

## Next Steps After Testing

If E2E works:
- ✅ Document the flow for CEs
- ✅ Add error handling improvements
- ✅ Consider adding agent cleanup/deletion
- ✅ Add multi-tenancy support (multiple concurrent demos)

If issues found:
- 🔍 Review logs and identify failure point
- 🐛 Fix specific issue
- 🔄 Redeploy and retest
