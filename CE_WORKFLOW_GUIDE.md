# CE Dashboard Workflow Guide

## ✅ What Works Now (Deployed to capi-demo-00032-npk)

### 1. **CE Dashboard** → `/ce-dashboard`
- ✅ Enter customer URL
- ✅ Click "Start Provision"
- ✅ Calls `/api/provision/start`
- ✅ Redirects to progress page

### 2. **Provision Progress** → `/provision-progress?jobId=xxx`
- ✅ Real-time SSE logs (not mock)
- ✅ Shows all 7 stages:
  1. Research (analyze website)
  2. Demo Story (create narrative & golden queries)
  3. Data Modeling (design BigQuery schema)
  4. Synthetic Data (generate realistic data)
  5. Infrastructure (create dataset & load data)
  6. CAPI Instructions (generate YAML config)
  7. Validation (test SQL queries)
- ✅ Progress percentage updates
- ✅ Elapsed time tracking
- ✅ Live technical logs for CEs

### 3. **Completion Buttons** (NEW - just deployed)
- ✅ "Open BigQuery Console" → Opens BigQuery with provisioned dataset
- ✅ "View Demo Assets" → Navigate to `/demo-assets?jobId=xxx`
- ✅ "Launch Chat Interface" → Navigate to `/` (main chat page)

---

## ⚠️ Chat Interface Connection Gap

### **Current Chat Endpoint**: `/api/chat`

**How it works:**
```python
# backend/api.py (line 313-344)
@app.post("/api/chat")
def chat_endpoint(chat_request: ChatRequest):
    # Uses HARDCODED environment variables:
    data_agent_id = os.environ.get('DATA_AGENT_ID', 'default_agent')
    dataset_id = os.environ.get('DATASET_ID', 'leagueapps_demo')

    # Creates conversation with fixed agent
    conversation.agents = [f'projects/{billing_project}/locations/global/dataAgents/{data_agent_id}']
```

**The Problem:**
- After provisioning creates a new dataset (e.g., `shopify_capi_demo_20251005`)
- Chat interface still talks to the OLD `leagueapps_demo` dataset
- No CAPI Data Agent is created for the new dataset
- No dynamic routing to connect chat → provisioned data

---

## 🔧 Solutions to Connect Chat Interface

### **Option 1: Manual Testing** (Quick Validation)

1. **After provisioning completes**, note these values:
   - Dataset ID: `{company}_capi_demo_{date}`
   - YAML file location: `/tmp/capi_instructions_{company}.yaml`
   - BigQuery dataset: `bq-demos-469816.{dataset_id}`

2. **Manually create CAPI Data Agent:**
   ```bash
   # In Google Cloud Console:
   # 1. Go to Conversational Analytics API
   # 2. Create new Data Agent
   # 3. Upload the YAML file from /tmp/
   # 4. Note the agent ID
   ```

3. **Update environment and redeploy:**
   ```bash
   # Update backend/.env
   DATA_AGENT_ID=your_new_agent_id
   DATASET_ID=shopify_capi_demo_20251005

   # Rebuild and deploy
   gcloud builds submit --tag us-central1-docker.pkg.dev/bq-demos-469816/capi-demo/capi-demo
   gcloud run deploy capi-demo --image ...
   ```

4. **Test chat interface:**
   - Go to `/`
   - Enter a question from golden queries
   - Verify it queries the NEW dataset

---

### **Option 2: Automatic Agent Creation** (Proper Solution)

Add agent creation to the Infrastructure Agent:

```python
# In infrastructure_agent.py

from google.cloud import geminidataanalytics

async def _create_capi_agent(self, dataset_id: str, yaml_file: str, state: Dict) -> str:
    """Create CAPI Data Agent programmatically."""
    client = geminidataanalytics.DataAgentServiceClient()

    # Read YAML config
    with open(yaml_file, 'r') as f:
        yaml_content = f.read()

    # Create agent
    agent = geminidataanalytics.DataAgent()
    agent.display_name = f"{state['customer_info']['company_name']} Demo Agent"
    agent.published_context.system_instruction = yaml_content

    # Add dataset reference
    agent.published_context.data_sources = [
        geminidataanalytics.DataSource(
            bigquery_dataset=f"projects/{self.project_id}/datasets/{dataset_id}"
        )
    ]

    request = geminidataanalytics.CreateDataAgentRequest(
        parent=f"projects/{self.project_id}/locations/global",
        data_agent=agent
    )

    created_agent = client.create_data_agent(request=request)
    agent_id = created_agent.name.split('/')[-1]

    logger.info(f"✅ Created CAPI agent: {agent_id}")
    return agent_id

# In execute() method:
async def execute(self, state: Dict) -> Dict:
    # ... existing code ...

    # CREATE CAPI AGENT
    yaml_file = state.get("capi_yaml_file")
    agent_id = await self._create_capi_agent(dataset_id, yaml_file, state)

    # Update state
    state["capi_agent_id"] = agent_id
    state["capi_agent_created"] = True

    return state
```

---

### **Option 3: Dynamic Chat Routing** (Best UX)

Modify chat endpoint to accept dynamic parameters:

```python
# backend/api.py

class ChatRequest(BaseModel):
    message: str
    dataset_id: Optional[str] = None  # Optional: use provisioned dataset
    agent_id: Optional[str] = None    # Optional: use provisioned agent

@app.post("/api/chat")
def chat_endpoint(chat_request: ChatRequest):
    # Use provided values or fall back to env vars
    data_agent_id = chat_request.agent_id or os.environ.get('DATA_AGENT_ID', 'default_agent')
    dataset_id = chat_request.dataset_id or os.environ.get('DATASET_ID', 'leagueapps_demo')

    # Rest of the code uses these dynamic values
    conversation.agents = [f'projects/{billing_project}/locations/global/dataAgents/{data_agent_id}']
```

**Frontend changes:**
```typescript
// In Index.tsx

const handleSendMessage = async (content: string) => {
  // Get provisioned IDs from URL params or localStorage
  const urlParams = new URLSearchParams(window.location.search);
  const datasetId = urlParams.get('dataset_id') || localStorage.getItem('dataset_id');
  const agentId = urlParams.get('agent_id') || localStorage.getItem('agent_id');

  const response = await fetch(API_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: content,
      dataset_id: datasetId,  // Pass provisioned dataset
      agent_id: agentId       // Pass provisioned agent
    })
  });
```

**Then update ProvisionProgress completion button:**
```typescript
// Pass agent_id and dataset_id to chat interface
onClick={() => {
  const agentId = state.metadata?.agentId || '';
  const datasetId = state.metadata?.datasetId || '';
  navigate(`/?agent_id=${agentId}&dataset_id=${datasetId}`);
}}
```

---

## 🧪 Testing Plan

### **Test 1: Verify Provisioning Works**
```bash
# 1. Open CE Dashboard
open https://capi-demo-549403515075.us-central1.run.app/ce-dashboard

# 2. Enter URL: https://www.shopify.com
# 3. Click "Start Provision"
# 4. Verify redirect to progress page
# 5. Watch real-time logs (not mock)
# 6. Wait for completion (~3-5 minutes)
```

### **Test 2: Verify BigQuery Data**
```bash
# After provisioning completes:
# 1. Click "Open BigQuery Console"
# 2. Verify dataset exists: shopify_capi_demo_20251005
# 3. Check tables have data
# 4. Run a golden query manually
```

### **Test 3: Check Generated Files**
```bash
# SSH into Cloud Run container (or check /tmp/ locally)
ls -la /tmp/capi_instructions_*.yaml
ls -la /tmp/demo_story_*.json
ls -la /tmp/DEMO_REPORT_*.md

# View YAML config
cat /tmp/capi_instructions_shopify.yaml
```

### **Test 4: Manual Chat Test** (Option 1)
```bash
# 1. Create CAPI agent manually in Console
# 2. Upload YAML file
# 3. Update backend/.env with agent ID
# 4. Redeploy
# 5. Test chat at /
```

---

## 📋 What Needs to Be Built for Full E2E

1. ✅ **CE Dashboard** - DONE
2. ✅ **Provisioning API** - DONE (7 agents working)
3. ✅ **SSE Streaming** - DONE (real-time logs)
4. ✅ **Progress UI** - DONE (all stages tracked)
5. ✅ **Completion Buttons** - DONE (just deployed)
6. ❌ **CAPI Agent Creation** - NOT IMPLEMENTED
7. ❌ **Dynamic Chat Routing** - NOT IMPLEMENTED
8. ❌ **Session Management** - NOT IMPLEMENTED (link jobId → agentId)

---

## 🚀 Recommended Next Steps

### **Immediate (Manual Test)**
1. Run a provision from CE Dashboard
2. Wait for completion
3. Note the dataset ID from logs
4. Manually create CAPI agent
5. Test one golden query

### **Short Term (Option 2)**
1. Implement automatic CAPI agent creation
2. Store agent_id in job state
3. Update completion metadata
4. Test E2E flow

### **Long Term (Option 3)**
1. Implement dynamic chat routing
2. Add session management
3. Support multiple concurrent demos
4. Add agent lifecycle management (create/delete)

---

## 📊 Current System Status

| Component | Status | Notes |
|-----------|--------|-------|
| CE Dashboard UI | ✅ Working | URL input, provision button |
| API /provision/start | ✅ Working | Creates job, starts orchestrator |
| 7 Agents Pipeline | ✅ Working | Research → Validation |
| SSE Streaming | ✅ Working | Real-time logs to frontend |
| Progress UI | ✅ Working | All stages, percentage, time |
| BigQuery Provisioning | ✅ Working | Dataset + tables created |
| YAML Generation | ✅ Working | System instructions file |
| SQL Validation | ✅ Working | Tests queries |
| CAPI Agent Creation | ❌ Missing | Must be manual or implemented |
| Chat → Provisioned Data | ❌ Missing | No dynamic routing |
| Completion Flow | ⚠️ Partial | Buttons work, but no agent_id |

---

## 🎯 Summary

**What works perfectly:**
- CE can input URL → see progress → view BigQuery results
- All 7 agents execute successfully
- Real-time technical logs for debugging
- Dataset and data are created correctly

**What's missing:**
- Automatic CAPI Data Agent creation
- Connection between provisioned data and chat interface
- Dynamic routing to use different agents/datasets

**To test chat NOW:**
- Must manually create CAPI agent using generated YAML
- Update environment variables
- Redeploy service

**To make it fully automated:**
- Implement Option 2 or Option 3 above
- Should take ~2-4 hours to implement
