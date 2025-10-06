# Comprehensive Testing Plan for API Integration Layer

**Date:** 2025-10-05
**Status:** API Routing Fixed - Ready for Full Testing
**Environment:** Cloud Run (bq-demos-469816)
**Revision:** capi-demo-00023-rx8

---

## ✅ Pre-Test Verification (COMPLETED)

### **Code Quality Checks**
- [x] Syntax validation: All Python files compile without errors
- [x] Import validation: All modules import correctly
- [x] Route registration: 8 provisioning routes + 2 existing routes = 10 total API routes
- [x] Cloud Run deployment: Service responding at https://capi-demo-549403515075.us-central1.run.app
- [x] Frontend build: Built successfully (9.39s)

### **API Endpoint Verification (After Routing Fix)**
- [x] GET /api/provision/history - Returns valid JSON `{"jobs": [], "total": 0}`
- [x] POST /api/provision/start - Creates job successfully, returns job_id
- [x] GET /api/provision/status/{job_id} - Returns job status with agents array
- [x] Jobs tracked in history correctly
- [x] No "Method Not Allowed" errors
- [x] No HTML returned for API routes

### **Known Issues (ORIGINAL)**
⚠️ **Minor Warning:** Pydantic warning about `schema` field name in `DemoAssetsResponse`
- **Impact:** Cosmetic only, does not affect functionality
- **Fix:** Rename field to `schema_data` (low priority)

### **Issues Found During Testing → FIXED**

**Issue 1: API Routing Problem** ✅ FIXED
- **Problem:** GET /api/provision/history returned HTML instead of JSON
- **Problem:** POST /api/provision/start returned "Method Not Allowed" (405)
- **Root Cause:** Catch-all route `@app.get("/{full_path:path}")` was intercepting API routes
- **Fix Applied:** Updated catch-all route to exclude paths starting with `api/`
- **File Changed:** `backend/api.py` (lines 346-354)
- **Deployed:** Revision capi-demo-00023-rx8
- **Status:** ✅ All API endpoints now working correctly
- **Details:** See `API_ROUTING_FIX.md`

**Issue 2: Environment Variable Missing** ⚠️ IN PROGRESS
- **Problem:** Jobs fail with "GEMINI_API_KEY environment variable not set"
- **Impact:** API endpoints work, but background workflows fail
- **Next Step:** Configure Cloud Run environment variables
- **Required Variables:** GEMINI_API_KEY, ANTHROPIC_API_KEY, others TBD

---

## 📋 Testing Plan Overview

### **Test Phases**

```
Phase 1: Unit Tests (Backend Components)
   ↓
Phase 2: API Endpoint Tests (REST API)
   ↓
Phase 3: SSE Streaming Tests (Real-time)
   ↓
Phase 4: Integration Tests (Full Pipeline)
   ↓
Phase 5: Frontend Integration Tests (UI)
   ↓
Phase 6: End-to-End Tests (Complete Workflow)
```

---

## 🧪 Phase 1: Unit Tests - Backend Components

### **1.1 Job State Manager Tests**

**Test File:** `test_job_state_manager.py`

```python
def test_create_job():
    """Test job creation with initial state."""
    manager = get_job_manager()
    job = manager.create_job(
        job_id="test-123",
        customer_url="https://test.com",
        mode="default"
    )

    assert job.job_id == "test-123"
    assert job.status == "pending"
    assert len(job.agents) == 7  # 7 agents initialized
    assert job.overall_progress == 0
    print("✓ Job creation works")

def test_update_agent_status():
    """Test updating individual agent status."""
    manager = get_job_manager()
    job = manager.create_job("test-456", "https://test.com")

    # Update agent 0 to running
    manager.update_agent_status("test-456", 0, "running", 50)

    updated_job = manager.get_job("test-456")
    assert updated_job.agents[0].status == "running"
    assert updated_job.agents[0].progress_percentage == 50
    print("✓ Agent status updates work")

def test_add_logs():
    """Test adding log entries."""
    manager = get_job_manager()
    job = manager.create_job("test-789", "https://test.com")

    manager.add_log("test-789", "research", "Starting research...", "INFO")

    updated_job = manager.get_job("test-789")
    assert len(updated_job.logs) == 1
    assert updated_job.logs[0].message == "Starting research..."
    print("✓ Logging works")

def test_sse_subscription():
    """Test SSE subscriber pattern."""
    import asyncio

    async def test():
        manager = get_job_manager()
        job = manager.create_job("test-sse", "https://test.com")

        # Subscribe
        queue = await manager.subscribe("test-sse")

        # Update job (should trigger notification)
        manager.update_job_status("test-sse", "running")

        # Check queue received update
        update = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert update['type'] == 'update'
        assert update['data']['status'] == 'running'
        print("✓ SSE subscription works")

    asyncio.run(test())
```

**Run:**
```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/backend
python test_job_state_manager.py
```

**Expected:** All tests pass ✅

---

### **1.2 Provisioning Router Tests**

**Test File:** `test_provisioning_router.py`

```python
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_start_provision_endpoint():
    """Test POST /api/provision/start."""
    response = client.post(
        "/api/provision/start",
        json={"customer_url": "https://test.com"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    print(f"✓ Start provision endpoint works: {data['job_id']}")

def test_get_status_endpoint():
    """Test GET /api/provision/status/{job_id}."""
    # First create a job
    create_response = client.post(
        "/api/provision/start",
        json={"customer_url": "https://test.com"}
    )
    job_id = create_response.json()["job_id"]

    # Then get status
    response = client.get(f"/api/provision/status/{job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "agents" in data
    assert len(data["agents"]) == 7
    print(f"✓ Get status endpoint works")

def test_get_history_endpoint():
    """Test GET /api/provision/history."""
    response = client.get("/api/provision/history")

    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    print(f"✓ Get history endpoint works: {data['total']} jobs")

def test_404_for_invalid_job():
    """Test 404 for non-existent job."""
    response = client.get("/api/provision/status/invalid-job-id")

    assert response.status_code == 404
    print("✓ 404 handling works")
```

**Run:**
```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/backend
python test_provisioning_router.py
```

**Expected:** All tests pass ✅

---

## 🌐 Phase 2: API Endpoint Tests (Live Cloud Run)

### **2.1 Basic Endpoint Tests**

**Test Script:** `test_live_api.sh`

```bash
#!/bin/bash

BASE_URL="https://capi-demo-549403515075.us-central1.run.app"

echo "🧪 Testing Live API Endpoints"
echo "================================"

# Test 1: Health check via history
echo -e "\n[Test 1] GET /api/provision/history"
curl -s -X GET "$BASE_URL/api/provision/history" | jq '.total'

# Test 2: Start provision
echo -e "\n[Test 2] POST /api/provision/start"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/provision/start" \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.test-demo.com"}')

JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Created job: $JOB_ID"

# Test 3: Get status
echo -e "\n[Test 3] GET /api/provision/status/{job_id}"
sleep 2
curl -s -X GET "$BASE_URL/api/provision/status/$JOB_ID" | jq '.current_phase, .overall_progress'

# Test 4: Get history (should include new job)
echo -e "\n[Test 4] Verify job in history"
curl -s -X GET "$BASE_URL/api/provision/history" | jq '.jobs[0].job_id'

# Test 5: Test 404
echo -e "\n[Test 5] Test 404 for invalid job"
curl -s -w "HTTP Status: %{http_code}\n" -X GET "$BASE_URL/api/provision/status/invalid-id-12345" | tail -1

echo -e "\n✅ Live API tests complete"
```

**Run:**
```bash
cd /home/admin_/final_demo/capi/demo-gen-capi
chmod +x test_live_api.sh
./test_live_api.sh
```

**Expected:**
- ✅ History returns total count
- ✅ Start provision returns job_id
- ✅ Status endpoint returns job data
- ✅ Job appears in history
- ✅ Invalid job returns 404

---

### **2.2 Crazy Frog Mode Test**

```bash
echo "🐸 Testing Crazy Frog Mode"

curl -s -X POST "$BASE_URL/api/provision/crazy-frog" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_url": "https://www.stripe.com",
    "use_case_context": "Test context for fintech fraud detection demo",
    "industry_hint": "Fintech",
    "target_persona": "CFO",
    "demo_complexity": "Advanced"
  }' | jq '.'
```

**Expected:**
- ✅ Returns job_id
- ✅ Mode set to "crazy_frog"
- ✅ Context stored in job state

---

## 📡 Phase 3: SSE Streaming Tests

### **3.1 Manual SSE Test (Browser)**

**Instructions:**
1. Open browser to: https://capi-demo-549403515075.us-central1.run.app/ce-dashboard
2. Start a test provision
3. Open browser DevTools → Network tab
4. Look for connection to `/api/provision/stream/{job_id}`
5. Click on the stream request
6. Go to "Response" or "EventStream" tab
7. Watch for real-time updates

**Expected Behavior:**
- Connection shows "pending" status
- Updates stream every 2-3 seconds
- See `data: {json}` events
- Events contain: status, current_phase, agents[], logs[]
- Connection closes when job completes/fails

---

### **3.2 SSE Test Script**

**Requires:** `pip install sseclient-py`

```python
# test_sse_stream.py
import requests
import json
import sseclient

BASE_URL = "https://capi-demo-549403515075.us-central1.run.app"

# Start a provision
response = requests.post(
    f"{BASE_URL}/api/provision/start",
    json={"customer_url": "https://test.com"}
)
job_id = response.json()["job_id"]
print(f"Started job: {job_id}")

# Connect to SSE stream
print(f"\nConnecting to SSE stream...")
url = f"{BASE_URL}/api/provision/stream/{job_id}"
response = requests.get(url, stream=True, headers={'Accept': 'text/event-stream'})
client = sseclient.SSEClient(response)

event_count = 0
for event in client.events():
    if event.data:
        try:
            data = json.loads(event.data)
            print(f"\n[Event {event_count + 1}]")
            print(f"  Status: {data.get('status')}")
            print(f"  Phase: {data.get('current_phase')}")
            print(f"  Progress: {data.get('overall_progress')}%")

            # Show agent statuses
            for i, agent in enumerate(data.get('agents', [])):
                if agent['status'] != 'pending':
                    print(f"    Agent {i+1}: {agent['name']} - {agent['status']}")

            event_count += 1

            if data.get('status') in ['completed', 'failed', 'cancelled']:
                print(f"\n✅ Job finished: {data.get('status')}")
                break

        except json.JSONDecodeError:
            print(f"Heartbeat: {event.data}")

print(f"\nReceived {event_count} events")
```

**Run:**
```bash
pip install sseclient-py
python test_sse_stream.py
```

**Expected:**
- ✅ Connects successfully
- ✅ Receives initial state immediately
- ✅ Updates stream every 2-3 seconds
- ✅ Shows agent progress
- ✅ Closes on completion

---

## 🔄 Phase 4: Integration Tests (Full Pipeline)

### **4.1 Short Mock Pipeline Test**

**Create:** `test_mock_pipeline.py`

```python
"""
Test the full pipeline with a mock/fast execution.
This doesn't run real agents, just tests the flow.
"""
import asyncio
from agentic_service.utils.job_state_manager import get_job_manager

async def mock_provision_workflow(job_id):
    """Mock the provisioning workflow."""
    manager = get_job_manager()

    # Simulate 7 agents executing
    agent_names = [
        "Research Agent", "Demo Story Agent", "Data Modeling Agent",
        "Synthetic Data Generator", "Infrastructure Agent",
        "CAPI Instruction Generator", "Demo Validator"
    ]

    for i, name in enumerate(agent_names):
        print(f"\n[Agent {i+1}/7] {name}")

        # Start agent
        manager.update_current_phase(job_id, name)
        manager.update_agent_status(job_id, i, "running", 0)
        manager.add_log(job_id, name.lower(), f"Starting {name}...", "INFO")

        # Simulate work
        await asyncio.sleep(2)

        # Complete agent
        manager.update_agent_status(job_id, i, "completed", 100)
        manager.add_log(job_id, name.lower(), f"✅ {name} completed", "INFO")

    # Set final results
    manager.set_results(
        job_id,
        dataset_id="test_dataset_20251005",
        demo_title="Test Demo Title",
        golden_queries=[{"id": "q1", "question": "Test query?"}],
        schema=[{"name": "test_table", "fields": []}],
        metadata={"totalRows": 1000}
    )

    manager.update_job_status(job_id, "completed")
    print(f"\n✅ Mock pipeline completed")

async def test_pipeline():
    manager = get_job_manager()

    # Create job
    job = manager.create_job(
        job_id="test-pipeline-123",
        customer_url="https://test.com"
    )
    print(f"Created job: {job.job_id}")

    # Run mock workflow
    await mock_provision_workflow(job.job_id)

    # Verify final state
    final_job = manager.get_job(job.job_id)
    assert final_job.status == "completed"
    assert all(a.status == "completed" for a in final_job.agents)
    assert final_job.overall_progress == 100
    assert final_job.dataset_id == "test_dataset_20251005"

    print("\n✅ All assertions passed")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
```

**Run:**
```bash
python test_mock_pipeline.py
```

**Expected:**
- ✅ All 7 agents execute sequentially
- ✅ Job manager updates at each step
- ✅ Final status is "completed"
- ✅ Results are set correctly

---

### **4.2 Real Pipeline Test (FULL - Takes ~10 minutes)**

**⚠️ Warning:** This will actually provision a demo in BigQuery

```bash
echo "🚀 Testing Real Pipeline with Shopify"

# Start provision
RESPONSE=$(curl -s -X POST "$BASE_URL/api/provision/start" \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.shopify.com", "project_id": "bq-demos-469816"}')

JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Started job: $JOB_ID"

# Poll status every 30 seconds
for i in {1..30}; do
  echo -e "\n[Poll $i] Checking status..."
  STATUS=$(curl -s "$BASE_URL/api/provision/status/$JOB_ID" | jq -r '.status')
  PROGRESS=$(curl -s "$BASE_URL/api/provision/status/$JOB_ID" | jq -r '.overall_progress')
  PHASE=$(curl -s "$BASE_URL/api/provision/status/$JOB_ID" | jq -r '.current_phase')

  echo "  Status: $STATUS | Progress: $PROGRESS% | Phase: $PHASE"

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi

  sleep 30
done

# Get final assets
if [ "$STATUS" = "completed" ]; then
  echo -e "\n✅ Pipeline completed! Getting assets..."
  curl -s "$BASE_URL/api/provision/assets/$JOB_ID" | jq '.demo_title, .metadata.datasetId'
else
  echo -e "\n❌ Pipeline failed or timed out"
  curl -s "$BASE_URL/api/provision/status/$JOB_ID" | jq '.errors'
fi
```

**Expected (if successful):**
- ✅ Job starts (pending → running)
- ✅ Progress increases through 7 stages
- ✅ Status becomes "completed"
- ✅ Assets endpoint returns demo data
- ✅ BigQuery dataset created

---

## 🖥️ Phase 5: Frontend Integration Tests

### **5.1 CE Dashboard Tests**

**Manual Test:**
1. Navigate to: https://capi-demo-549403515075.us-central1.run.app/ce-dashboard
2. Verify UI loads correctly
3. Click "DEFAULT MODE" card
4. Enter URL: `test.com`
5. Click "Start Provision"
6. Verify redirect to progress page

**Expected:**
- ✅ Dashboard loads
- ✅ Two mode cards visible
- ✅ URL validation works
- ✅ Start provision creates job
- ✅ Redirects to /provision-progress?jobId={id}

---

### **5.2 Progress Tracker Tests**

**Manual Test:**
1. After starting provision, land on progress page
2. Verify 7 agent cards display
3. Watch for real-time updates
4. Check logs viewer shows messages
5. Verify progress bar animates

**Automated Test (Browser Console):**
```javascript
// Run in browser console on progress page

// Check SSE connection
const events = performance.getEntriesByType("resource")
  .filter(e => e.name.includes("/api/provision/stream"));
console.log("SSE connections:", events.length);

// Verify updates
let updateCount = 0;
const checkUpdates = setInterval(() => {
  const progress = document.querySelector('[data-progress]')?.textContent;
  console.log(`Update ${++updateCount}: Progress = ${progress}`);

  if (updateCount >= 5) clearInterval(checkUpdates);
}, 3000);
```

**Expected:**
- ✅ SSE connection established
- ✅ Updates received every 2-3 seconds
- ✅ Agent statuses change visually
- ✅ Logs stream in real-time
- ✅ Progress bar updates

---

### **5.3 Demo Assets Tests**

**Manual Test:**
1. After pipeline completes, view assets page
2. Verify all tabs load (Demo Title, Queries, Schema, Metadata)
3. Test search in queries tab
4. Test expand/collapse in schema
5. Click "Launch Chat Interface" button

**Expected:**
- ✅ All 4 tabs display data
- ✅ Search filters queries
- ✅ Schema tables expand
- ✅ Metadata shows stats
- ✅ Launch button redirects to chat

---

## 🎯 Phase 6: End-to-End Tests

### **6.1 Complete Workflow Test**

**Scenario:** CE provisions Shopify demo and uses it

1. **CE Dashboard:**
   - Navigate to /ce-dashboard
   - Select DEFAULT MODE
   - Enter: shopify.com
   - Click "Start Provision"

2. **Progress Tracking:**
   - Watch 7 agents execute
   - Verify logs stream
   - Wait ~10 minutes for completion

3. **View Assets:**
   - Redirect to /demo-assets
   - Browse golden queries
   - View schema (15 tables)
   - Check metadata

4. **Launch Chat:**
   - Click "Launch Chat Interface"
   - Test with golden query: "What is our total GMV this month?"
   - Verify response with chart
   - Enable Developer Mode to see SQL

**Expected:** Full workflow completes without errors

---

### **6.2 Crazy Frog Mode E2E Test**

**Scenario:** CE creates custom fintech demo

1. **CE Dashboard:**
   - Select CRAZY FROG MODE 🐸
   - Enter URL: stripe.com
   - Fill context:
     ```
     Leading payment processing company. Demo for CFO focused on
     fraud detection and transaction monitoring. Need real-time
     anomaly detection queries and revenue analytics.
     ```
   - Set: Persona=CFO, Complexity=Advanced, Focus=Fraud Detection
   - Click "Unleash the Frog"

2. **Progress:** Watch pipeline with enhanced context

3. **Assets:** Verify queries are CFO-focused and fraud-related

4. **Chat:** Test advanced fraud detection queries

**Expected:** Demo tailored to context provided

---

## 📊 Success Criteria

### **Must Pass**

- [ ] All unit tests pass
- [ ] All API endpoints return 200 (except 404 tests)
- [ ] SSE streaming works continuously for 5+ minutes
- [ ] At least 1 full pipeline completes successfully
- [ ] Frontend loads all 3 CE pages
- [ ] End-to-end workflow (dashboard → provision → assets → chat) works

### **Should Pass**

- [ ] Default mode provision completes in <12 minutes
- [ ] Crazy Frog mode provision completes in <15 minutes
- [ ] SSE delivers updates within 3 seconds of backend changes
- [ ] No memory leaks (job count doesn't grow unbounded)
- [ ] Error handling works (test invalid URLs, network failures)

### **Nice to Have**

- [ ] Multiple concurrent provisions don't interfere
- [ ] Cancel job works mid-execution
- [ ] Assets download YAML works
- [ ] Job history persists across page refreshes (until Cloud Run restarts)

---

## 🐛 Known Issues to Test For

### **Potential Problems**

1. **SSE Connection Drops**
   - **Test:** Keep stream open for 10+ minutes
   - **Expected:** Heartbeats keep connection alive

2. **Job State Lost on Restart**
   - **Test:** Restart Cloud Run, check if jobs still exist
   - **Expected:** Jobs lost (in-memory only) - KNOWN LIMITATION

3. **Concurrent Jobs**
   - **Test:** Start 3 provisions simultaneously
   - **Expected:** All should work (thread-safe)

4. **Large Responses**
   - **Test:** Provision with 20+ golden queries
   - **Expected:** Assets endpoint handles large payloads

5. **CORS Issues**
   - **Test:** Call API from different origin
   - **Expected:** CORS headers allow it

---

## 📝 Test Execution Checklist

### **Quick Tests (5 minutes)**
```bash
# Run these first
cd /home/admin_/final_demo/capi/demo-gen-capi/backend

# 1. Import tests
python -c "from routes.provisioning import router; print('✓ Imports work')"

# 2. History test
curl -s https://capi-demo-549403515075.us-central1.run.app/api/provision/history | jq '.'

# 3. Start provision test
curl -X POST https://capi-demo-549403515075.us-central1.run.app/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://test.com"}' | jq '.'
```

### **Medium Tests (30 minutes)**
- [ ] Run all unit tests
- [ ] Test all API endpoints
- [ ] Test SSE stream (3-5 minute sample)
- [ ] Test frontend pages load
- [ ] Run mock pipeline test

### **Full Tests (2-3 hours)**
- [ ] Complete E2E default provision (Shopify)
- [ ] Complete E2E Crazy Frog provision (Stripe)
- [ ] Test concurrent provisions
- [ ] Stress test with multiple clients

---

## 📧 Reporting Issues

**If tests fail, collect:**

1. **Error messages** from console/logs
2. **Job ID** if applicable
3. **HTTP status codes**
4. **Cloud Run logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=capi-demo AND severity=ERROR" \
     --project=bq-demos-469816 --limit=20 --freshness=1h
   ```
5. **Screenshots** if UI issue

---

**Status:** 📋 Test plan ready for execution
**Next Step:** Run Phase 1 unit tests
