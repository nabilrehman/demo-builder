# Current Status - Provisioning Pipeline Investigation

**Last Updated:** 2025-10-05 05:00 UTC
**Active Revision:** `capi-demo-00037-vwh`
**Service URL:** https://capi-demo-cuxcxfhcya-uc.a.run.app

---

## 🎯 CRITICAL DISCOVERY

### ✅ The Orchestrator IS Working!

**Breakthrough Finding:** The 7-agent pipeline DOES execute successfully. The issue was a **misdiagnosis**.

**Evidence from job `0e1810fd-34aa-4118-b0d1-f2508f0768bb`:**
```json
{
  "status": "failed",
  "current_phase": "Research Agent",
  "agents": [
    {
      "name": "Research Agent",
      "status": "failed",
      "start_time": "2025-10-05T04:55:54.689698",
      "end_time": "2025-10-05T04:55:55.203369",
      "error_message": "Failed to scrape https://www.test.com/: SSL cert error"
    }
  ],
  "recent_logs": [
    "Starting default mode provisioning for https://www.test.com/",
    "Starting 7-agent pipeline...",
    "Starting Research Agent...",
    "❌ Research Agent failed: SSL error"
  ]
}
```

**Key Insights:**
1. ✅ Background tasks DO execute with `asyncio.create_task()`
2. ✅ Job state manager captures all logs and progress
3. ✅ Agents run sequentially as designed
4. ⚠️ Application logs NOT appearing in Cloud Logging (but stored in job state)
5. ⚠️ Service becomes unresponsive after long-running tasks start

---

## 📊 What We Tried

### Revision History:

| Revision | Changes | Result |
|----------|---------|--------|
| `00037-vwh` | Original code with `BackgroundTasks` | ✅ Works but logs not visible in Cloud Logging |
| `00038-4bl` | Replaced with `asyncio.create_task()` | ❌ Service timeouts |
| `00039-wf7` | Added event loop + debug logging | ❌ Service timeouts |
| `00040-zr9` | Added `await asyncio.sleep(0.1)` | ❌ BLOCKING - caused 30s+ timeouts |
| `00041-z2l` | Removed blocking sleep | ❌ Complete service failure (HTTP 000) |

### Rollback Status:
- **Currently on:** `00037-vwh` (original working version)
- **Traffic routing:** 100% to revision 00037

---

## ⚠️ Current Issues

### Issue #1: Service Becomes Unresponsive
**Symptom:** After starting a long-running provision job, the service becomes unresponsive (HTTP 000)

**Last Test:**
- Started job for `solarwinds.com`: `b57802b8-d59a-4a4a-a4d5-f97ff4e59a98`
- Service became unresponsive ~30 seconds later
- Could not retrieve job status

**Hypothesis:** Cloud Run container is overloaded or crashing during execution

### Issue #2: No Application Logs in Cloud Logging
**Symptom:** `logger.info()` statements from application code don't appear in Cloud Logging

**What Works:**
- HTTP access logs (uvicorn) ARE visible
- Job state manager logs ARE captured (accessible via `/api/provision/status/{job_id}`)

**What Doesn't Work:**
- Python application logs from orchestrator
- Agent execution logs
- Background task logs

**Impact:** Cannot debug using `gcloud logging read`, but frontend can see logs via SSE

---

## 🔧 Configuration Status

### Cloud Run Settings:
- **Min instances:** 1 (keeps container warm)
- **Timeout:** 600s (10 minutes)
- **Memory:** 2Gi
- **Concurrency:** Default (80)

### Background Task Implementation (Rev 00037):
```python
# In routes/provisioning.py
background_tasks = set()  # Global tracking set

task = asyncio.create_task(run_provisioning_workflow(...))
background_tasks.add(task)
task.add_done_callback(background_tasks.discard)
```

---

## 🎯 Next Steps to Continue

### Immediate Priorities:

1. **Investigate Service Unresponsiveness**
   - Check if container is crashing mid-execution
   - Review memory usage during agent execution
   - Consider if LLM API calls are blocking the event loop

2. **Test with Healthier Endpoint**
   - The `/api/provision/status/{job_id}` endpoint times out
   - May need separate health check endpoint
   - Consider read-only endpoints vs. write operations

3. **Fix Logging Visibility**
   - Application logs not appearing in Cloud Logging
   - Need to configure Python logging to write to stdout/stderr
   - Or accept that logs are only in job state manager

### Architecture Options:

**Option A: Keep Current Architecture + Fix Issues**
- ✅ Orchestrator already works
- ✅ Job state manager captures everything
- ❌ Service becomes unresponsive
- ❌ No Cloud Logging visibility

**Option B: Move to Cloud Tasks**
- ✅ Proper background job queue
- ✅ Retry logic built-in
- ✅ Better observability
- ❌ Requires significant refactoring

**Option C: Cloud Run Jobs**
- ✅ Designed for long-running tasks
- ✅ Better resource isolation
- ❌ Cannot respond to HTTP immediately
- ❌ Need webhook for status updates

---

## 📝 Code State

### Files Modified:
- `backend/routes/provisioning.py` - Background task implementation
- No syntax errors
- Deployed image: `us-central1-docker.pkg.dev/bq-demos-469816/capi-demo/capi-demo:latest`

### Key Functions:
- `start_default_provision()` - Creates job, starts background task
- `run_provisioning_workflow()` - Executes 7-agent pipeline
- Job state manager - Tracks progress, logs, errors

---

## 🧪 Testing Checklist

When resuming:

- [ ] Test root endpoint: `curl https://capi-demo-cuxcxfhcya-uc.a.run.app/`
- [ ] Start provision job: `/api/provision/start` with real URL
- [ ] Monitor job status: `/api/provision/status/{job_id}`
- [ ] Check if service stays responsive during execution
- [ ] Verify all 7 agents complete for valid URL
- [ ] Check BigQuery for created dataset
- [ ] Test chat interface with provisioned data

---

## 🔍 Debug Commands

```bash
# Check current revision
gcloud run services describe capi-demo --region=us-central1 --format="value(status.latestReadyRevisionName)"

# Test provision endpoint
curl -X POST https://capi-demo-cuxcxfhcya-uc.a.run.app/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.solarwinds.com"}'

# Check job status
curl https://capi-demo-cuxcxfhcya-uc.a.run.app/api/provision/status/{job_id} | jq

# View job history
curl https://capi-demo-cuxcxfhcya-uc.a.run.app/api/provision/history | jq

# Check Cloud Logging (limited - app logs missing)
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=capi-demo' \
  --limit=20 --format="value(textPayload)" --freshness=10m

# Check datasets in BigQuery
bq ls --project_id=bq-demos-469816
```

---

## 💡 Key Learnings

1. **Background tasks work in Cloud Run** when using `asyncio.create_task()` with strong references
2. **Don't block the event loop** - `await asyncio.sleep()` in endpoint causes timeouts
3. **Job state manager is the source of truth** - not Cloud Logging
4. **Service can crash/hang during long operations** - needs investigation
5. **Testing with fake URLs (`test.com`) gives SSL errors** - use real URLs

---

## 🚀 Recommended Next Session Plan

1. **Morning warmup (5 min):**
   - Verify service is responsive
   - Check if previous job (`b57802b8...`) completed or failed

2. **Investigation (30 min):**
   - Start fresh provision job with `solarwinds.com`
   - Monitor service health during execution
   - Identify exact point where service becomes unresponsive

3. **Fix (60 min):**
   - If memory issue → increase memory allocation
   - If event loop blocking → refactor LLM calls to use run_in_executor
   - If container crash → add exception handling
   - If Cloud Run limitation → consider Cloud Tasks migration

4. **Testing (30 min):**
   - Complete E2E test with real company URL
   - Verify dataset creation in BigQuery
   - Test chat interface with provisioned agent

---

**Status:** Service is functional but becomes unresponsive during long operations. Core pipeline works. Needs stability fixes.
