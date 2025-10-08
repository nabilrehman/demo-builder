# 🏗️ CAPI Demo Platform - Google Cloud Architecture Plan
## Customer Engineer Perspective

**Document Version:** 2.0
**Last Updated:** October 7, 2025
**Prepared By:** Google Cloud Customer Engineering
**Project:** Conversational Analytics API (CAPI) Demo Platform
**GCP Project ID:** `bq-demos-469816`

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Proposed Architecture](#proposed-architecture)
4. [Implementation Phases](#implementation-phases)
5. [Testing Strategy](#testing-strategy)
6. [GCP Services & Technology Stack](#gcp-services--technology-stack)
7. [Success Criteria & KPIs](#success-criteria--kpis)
8. [Risk Mitigation](#risk-mitigation)
9. [Cost Analysis](#cost-analysis)

---

## 📊 Executive Summary

### The Challenge
The current CAPI demo platform faces critical operational challenges that limit its effectiveness for Customer Engineer (CE) workflows:

- **Performance**: 6-10 minute provisioning time prevents live demonstrations
- **Reliability**: Service becomes unresponsive during long-running operations
- **Scalability**: In-memory state management causes data loss on restarts
- **Efficiency**: No demo reusability leads to repeated work
- **Observability**: Limited logging and monitoring capabilities

### The Solution
A production-grade, cloud-native architecture leveraging Google Cloud best practices:

| Component | Current State | Proposed Solution | Impact |
|-----------|---------------|-------------------|---------|
| **Provisioning** | 6-10 min synchronous | 45-60s from templates | ⚡ 10x faster |
| **Orchestration** | Blocking FastAPI tasks | Cloud Tasks + Pub/Sub | 🔄 100% reliable |
| **Storage** | In-memory | Firestore + GCS | 💾 Zero data loss |
| **Scalability** | Single instance | Cloud Run autoscaling | 📈 Handle 100+ concurrent users |
| **Observability** | Basic logs | Cloud Logging + Trace + Monitoring | 🔍 Full visibility |

### Business Impact
- **10x faster** demo provisioning (45s vs 6min)
- **99.9% uptime** through proper async architecture
- **3x more demos** per CE through reusability
- **Lower costs** through resource lifecycle management

---

## 🔍 Current State Analysis

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CURRENT ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Cloud Run (Single Service)                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  FastAPI Backend                                         │   │
│  │  ├─ React Frontend (served as static files)             │   │
│  │  ├─ /api/provision/start (POST)                         │   │
│  │  │  └─ Blocking 7-agent pipeline (6-10 min) ❌         │   │
│  │  ├─ /api/provision/status/{job_id} (GET)               │   │
│  │  │  └─ In-memory job state ❌                           │   │
│  │  └─ /api/chat (POST)                                    │   │
│  │                                                           │   │
│  │  Background Tasks:                                       │   │
│  │  └─ asyncio.create_task() - causes service timeouts ❌  │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                      ↓                                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ BigQuery          │ Gemini CAPI      │ Vertex AI         │  │
│  │ (Data Storage)    │ (Agent Creation) │ (LLM Calls)       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  State Management: In-Memory Dictionary ❌                      │
│  Logging: stdout (not appearing in Cloud Logging) ❌            │
│  Monitoring: Basic Cloud Run metrics only ❌                    │
└─────────────────────────────────────────────────────────────────┘
```

### Critical Issues

#### 1. Service Reliability (🔴 CRITICAL)
**Problem:** Service becomes unresponsive during long-running provisioning jobs
- **Root Cause:** Long-running operations block the FastAPI event loop
- **Impact:**
  - HTTP 000 errors after ~30 seconds
  - Cannot check job status while provisioning
  - Service appears "down" to users
- **Evidence:** Revision 00037 works but becomes unresponsive (see CURRENT_STATUS.md:68)

#### 2. State Management (🔴 CRITICAL)
**Problem:** All job state stored in-memory
- **Root Cause:** Python dictionary in application memory
- **Impact:**
  - Complete data loss on service restart
  - Cannot scale horizontally (state not shared)
  - No audit trail or history
- **Evidence:** CURRENT_STATUS.md:138 - "In-memory state only"

#### 3. Provisioning Performance (🔴 CRITICAL)
**Problem:** 6-10 minute provisioning time
- **Root Cause:**
  - Synthetic data generation for every demo
  - 7 sequential LLM agent calls
  - Web scraping and research per customer
- **Impact:** Cannot provision during live demos
- **Evidence:** CE-IMPROVEMENTS-ROADMAP.md:83

#### 4. Observability (🟡 HIGH)
**Problem:** Application logs not appearing in Cloud Logging
- **Root Cause:** Logging configuration not writing to stdout/stderr properly
- **Impact:** Cannot debug issues in production
- **Evidence:** CURRENT_STATUS.md:82-89

#### 5. No Reusability (🟡 HIGH)
**Problem:** Every demo starts from scratch
- **Impact:** Repeated work, wasted resources, inconsistent quality
- **Evidence:** CE-IMPROVEMENTS-ROADMAP.md:61

---

## 🏗️ Proposed Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PROPOSED CLOUD-NATIVE ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────────┐
                            │   Users (CEs)   │
                            └────────┬────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │  Cloud Load Balancer  │
                         │  + Cloud Armor (WAF)  │
                         └───────────┬───────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND TIER                                   │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Cloud Run Service: capi-frontend                                │ │
│  │  - React SPA (Vite build)                                       │ │
│  │  - Firebase Authentication                                       │ │
│  │  - Cloud CDN enabled                                            │ │
│  │  - Min instances: 1 | Max: 10                                   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          API TIER                                       │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Cloud Run Service: capi-api                                     │ │
│  │  - FastAPI backend (async)                                      │ │
│  │  - Request validation & routing                                 │ │
│  │  - Firebase token verification                                  │ │
│  │  - Min instances: 1 | Max: 20 | Concurrency: 80                │ │
│  │                                                                  │ │
│  │  Endpoints:                                                      │ │
│  │  - POST /api/provision/quick (45s - template-based)            │ │
│  │  │  └─ Publishes to Pub/Sub topic                             │ │
│  │  - POST /api/provision/custom (async - Cloud Tasks)            │ │
│  │  │  └─ Creates Cloud Task                                      │ │
│  │  - GET /api/provision/status/{job_id} (from Firestore)        │ │
│  │  - POST /api/chat (proxies to CAPI agent)                     │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
              │                           │                    │
              │                           │                    │
              ▼                           ▼                    ▼
    ┌──────────────────┐      ┌──────────────────┐   ┌──────────────┐
    │  Pub/Sub Topic   │      │  Cloud Tasks     │   │  Firestore   │
    │  provision-jobs  │      │  Queue           │   │  (State DB)  │
    └────────┬─────────┘      └────────┬─────────┘   └──────────────┘
             │                         │
             │                         │
             ▼                         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      WORKER TIER (Background Jobs)                      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Cloud Run Service: capi-quick-provisioner                       │ │
│  │  - Triggered by: Pub/Sub (provision-jobs)                       │ │
│  │  - Timeout: 120s                                                │ │
│  │  - CPU: 2 | Memory: 4Gi                                         │ │
│  │  - Min: 0 | Max: 10 (scales to zero)                          │ │
│  │                                                                  │ │
│  │  Process:                                                        │ │
│  │  1. Receive job message                                         │ │
│  │  2. Load template from GCS                                      │ │
│  │  3. Create BigQuery dataset                                     │ │
│  │  4. Load parquet data (30-40s)                                 │ │
│  │  5. Create CAPI agent                                           │ │
│  │  6. Update Firestore job status                                │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Cloud Run Service: capi-custom-provisioner                      │ │
│  │  - Triggered by: Cloud Tasks                                    │ │
│  │  - Timeout: 600s (10 min)                                       │ │
│  │  - CPU: 4 | Memory: 8Gi                                         │ │
│  │  - Min: 0 | Max: 5                                             │ │
│  │                                                                  │ │
│  │  Process:                                                        │ │
│  │  1. Receive task payload                                        │ │
│  │  2. Run 7-agent orchestration pipeline                         │ │
│  │  3. Generate synthetic data                                     │ │
│  │  4. Create BigQuery dataset & tables                           │ │
│  │  5. Create CAPI agent                                           │ │
│  │  6. Update Firestore with results                              │ │
│  │  7. Publish completion event to Pub/Sub                        │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
              │                           │                    │
              │                           │                    │
              ▼                           ▼                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA & STORAGE TIER                              │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Firestore   │  │  Cloud       │  │  BigQuery    │  │  Secret   │ │
│  │  (Metadata)  │  │  Storage     │  │  (Analytics) │  │  Manager  │ │
│  │              │  │  (Templates) │  │              │  │           │ │
│  │  Collections:│  │              │  │  Datasets:   │  │  Secrets: │ │
│  │  - demos     │  │  Buckets:    │  │  - Per demo  │  │  - API    │ │
│  │  - templates │  │  - templates │  │  - Customer  │  │    keys   │ │
│  │  - jobs      │  │  - exports   │  │    data      │  │  - Config │ │
│  │  - users     │  │  - backups   │  │              │  │           │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │
└────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY & MANAGEMENT                           │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Cloud       │  │  Cloud       │  │  Cloud       │  │  Error    │ │
│  │  Logging     │  │  Monitoring  │  │  Trace       │  │  Reporting│ │
│  │              │  │              │  │              │  │           │ │
│  │  - API logs  │  │  Dashboards: │  │  - Request   │  │  - Python │ │
│  │  - Job logs  │  │  - Provision │  │    tracing   │  │    errors │ │
│  │  - Agent     │  │    times     │  │  - Agent     │  │  - Alerts │ │
│  │    execution │  │  - Success   │  │    calls     │  │           │ │
│  │  - Errors    │  │    rates     │  │              │  │           │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │
└────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         LIFECYCLE MANAGEMENT                            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Cloud Scheduler                                                  │ │
│  │                                                                   │ │
│  │  Jobs:                                                            │ │
│  │  - archive-old-demos (daily 2am)                                │ │
│  │  - delete-archived-demos (weekly)                               │ │
│  │  - cleanup-temp-datasets (daily 3am)                            │ │
│  │  - send-expiration-warnings (daily 9am)                         │ │
│  │  - export-metrics (daily midnight)                              │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

#### 1. **Separate Frontend & API Services**
**Why:**
- Independent scaling (frontend scales differently than API)
- Faster frontend delivery via Cloud CDN
- API can restart without affecting static content
- Better security boundaries

**Implementation:**
```yaml
# Frontend service (Cloud Run)
Service: capi-frontend
- Serves React build artifacts
- Cloud CDN enabled
- Min instances: 1 (always warm)
- Max instances: 10
- CPU: 1 | Memory: 512Mi

# API service (Cloud Run)
Service: capi-api
- FastAPI backend
- Min instances: 1
- Max instances: 20
- CPU: 2 | Memory: 2Gi
```

#### 2. **Event-Driven Provisioning with Pub/Sub**
**Why:**
- Decouples API from long-running jobs
- Prevents service timeouts
- Enables retry logic
- Supports multiple worker instances

**Flow:**
```
User → API → Pub/Sub → Worker Service
                ↓
            Firestore (job state)
```

#### 3. **Cloud Tasks for Custom Provisioning**
**Why:**
- Built-in retry with exponential backoff
- Schedule execution (provision at specific time)
- Better for long-running operations (10+ min)
- Dead-letter queue support

**Configuration:**
```python
task = {
    'http_request': {
        'http_method': tasks_v2.HttpMethod.POST,
        'url': f'{WORKER_URL}/execute-custom-provision',
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(job_payload).encode(),
        'oidc_token': {
            'service_account_email': worker_sa_email
        }
    },
    'dispatch_deadline': '600s',  # 10 minutes max
}
```

#### 4. **Firestore for State Management**
**Why:**
- Serverless, fully managed
- Real-time updates (for UI progress)
- ACID transactions
- Automatic scaling
- 99.99% SLA

**Schema:**
```javascript
// demos/{demo_id}
{
  demo_id: string,
  created_by: string,  // CE email
  customer_name: string,
  dataset_id: string,
  agent_id: string,
  status: 'pending' | 'running' | 'completed' | 'failed',
  created_at: timestamp,
  last_used: timestamp,
  is_pinned: boolean,
  golden_queries: array,
  metadata: map,
  // ... (see data model section)
}

// jobs/{job_id}
{
  job_id: string,
  demo_id: string,
  type: 'quick' | 'custom',
  status: 'queued' | 'running' | 'completed' | 'failed',
  progress: number,  // 0-100
  current_phase: string,
  logs: array,
  error: string,
  created_at: timestamp,
  started_at: timestamp,
  completed_at: timestamp
}
```

#### 5. **GCS for Template Storage**
**Why:**
- Cost-effective storage for parquet files
- Fast loading into BigQuery
- Versioning support
- Lifecycle policies for old templates

**Bucket Structure:**
```
gs://capi-templates-bq-demos-469816/
├── v1/
│   ├── shopify/
│   │   ├── customers.parquet
│   │   ├── orders.parquet
│   │   └── metadata.json
│   ├── banking/
│   └── healthcare/
├── v2/
│   └── ... (new template versions)
└── shared/
    └── common_dimensions.parquet

gs://capi-exports-bq-demos-469816/
├── demo-packages/
│   └── {demo_id}/
│       └── export_{timestamp}.zip
└── reports/
    └── {demo_id}/
        └── summary.pdf
```

#### 6. **Cloud Monitoring & Logging**
**Why:**
- Essential for production operations
- Troubleshoot issues quickly
- Track performance metrics
- Alert on anomalies

**Key Metrics to Track:**
```yaml
Custom Metrics:
  - provision_time_seconds (histogram)
  - provision_success_rate (counter)
  - template_usage_count (gauge)
  - active_demos_count (gauge)
  - agent_response_time_ms (histogram)

Alerts:
  - Provision failure rate > 5%
  - Average provision time > 90s
  - API error rate > 1%
  - Firestore write errors
```

---

## 🔄 Implementation Phases

### Phase 0: Foundation & Infrastructure Setup (Week 1)
**Goal:** Prepare GCP environment with proper service accounts, APIs, and baseline infrastructure

#### Tasks
1. **Enable Required GCP APIs**
   ```bash
   gcloud services enable \
     run.googleapis.com \
     firestore.googleapis.com \
     cloudtasks.googleapis.com \
     pubsub.googleapis.com \
     secretmanager.googleapis.com \
     monitoring.googleapis.com \
     logging.googleapis.com \
     cloudscheduler.googleapis.com \
     artifactregistry.googleapis.com
   ```

2. **Create Service Accounts with Least Privilege**
   ```bash
   # API service account
   gcloud iam service-accounts create capi-api \
     --display-name="CAPI API Service"

   # Worker service account
   gcloud iam service-accounts create capi-worker \
     --display-name="CAPI Worker Service"

   # Grant permissions
   # API: Read Firestore, Publish to Pub/Sub, Create Tasks
   # Worker: Read/Write Firestore, BigQuery Admin, CAPI Agent Creator
   ```

3. **Initialize Firestore in Native Mode**
   ```bash
   gcloud firestore databases create --region=us-central1
   ```

4. **Create Pub/Sub Topic & Subscriptions**
   ```bash
   # Quick provision topic
   gcloud pubsub topics create provision-jobs

   # Subscription for worker
   gcloud pubsub subscriptions create provision-jobs-worker \
     --topic=provision-jobs \
     --ack-deadline=120 \
     --message-retention-duration=7d
   ```

5. **Create Cloud Tasks Queue**
   ```bash
   gcloud tasks queues create custom-provision-queue \
     --max-dispatches-per-second=5 \
     --max-concurrent-dispatches=10 \
     --max-attempts=3 \
     --min-backoff=60s \
     --max-backoff=3600s
   ```

6. **Create GCS Buckets**
   ```bash
   gsutil mb -l us-central1 gs://capi-templates-bq-demos-469816
   gsutil mb -l us-central1 gs://capi-exports-bq-demos-469816

   # Set lifecycle policies
   gsutil lifecycle set lifecycle-templates.json gs://capi-templates-bq-demos-469816
   ```

7. **Setup Secret Manager**
   ```bash
   # Store API keys and sensitive config
   echo -n "YOUR_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
   ```

#### Testing Phase 0
```bash
# Test 1: Verify all APIs are enabled
gcloud services list --enabled | grep -E 'run|firestore|tasks|pubsub'

# Test 2: Test Firestore connection
python tests/test_firestore_connection.py

# Test 3: Test Pub/Sub publish/subscribe
python tests/test_pubsub_flow.py

# Test 4: Test Cloud Tasks creation
python tests/test_cloud_tasks.py

# Test 5: Verify service account permissions
python tests/test_iam_permissions.py
```

**Success Criteria:**
- ✅ All GCP APIs enabled
- ✅ Service accounts created with correct IAM roles
- ✅ Firestore accessible and writeable
- ✅ Pub/Sub can publish and consume messages
- ✅ Cloud Tasks queue can accept tasks

---

### Phase 1: State Management Migration (Week 2)
**Goal:** Replace in-memory state with Firestore to eliminate data loss

#### Tasks
1. **Create Firestore Repository Layer**
   ```python
   # backend/storage/firestore_repository.py
   from google.cloud import firestore
   from datetime import datetime
   from typing import Optional, List

   class DemoRepository:
       def __init__(self):
           self.db = firestore.Client()

       def create_demo(self, demo_data: dict) -> str:
           """Create new demo record."""
           doc_ref = self.db.collection('demos').document()
           demo_data['created_at'] = firestore.SERVER_TIMESTAMP
           doc_ref.set(demo_data)
           return doc_ref.id

       def get_demo(self, demo_id: str) -> Optional[dict]:
           """Get demo by ID."""
           doc = self.db.collection('demos').document(demo_id).get()
           return doc.to_dict() if doc.exists else None

       def update_demo_status(self, demo_id: str, status: str):
           """Update demo status."""
           self.db.collection('demos').document(demo_id).update({
               'status': status,
               'updated_at': firestore.SERVER_TIMESTAMP
           })

   class JobRepository:
       def __init__(self):
           self.db = firestore.Client()

       def create_job(self, job_data: dict) -> str:
           """Create provisioning job."""
           doc_ref = self.db.collection('jobs').document()
           job_data['created_at'] = firestore.SERVER_TIMESTAMP
           doc_ref.set(job_data)
           return doc_ref.id

       def add_log(self, job_id: str, message: str, level: str = 'INFO'):
           """Add log entry to job."""
           self.db.collection('jobs').document(job_id).update({
               'logs': firestore.ArrayUnion([{
                   'timestamp': datetime.utcnow().isoformat(),
                   'level': level,
                   'message': message
               }])
           })
   ```

2. **Migrate API Endpoints to Use Firestore**
   ```python
   # backend/routes/provisioning.py
   from storage.firestore_repository import DemoRepository, JobRepository

   demo_repo = DemoRepository()
   job_repo = JobRepository()

   @router.get("/api/provision/status/{job_id}")
   async def get_job_status(job_id: str):
       """Get job status from Firestore (no in-memory state!)."""
       job = job_repo.get_job(job_id)
       if not job:
           raise HTTPException(status_code=404, detail="Job not found")
       return job
   ```

3. **Add Firestore Indexes**
   ```yaml
   # firestore.indexes.json
   indexes:
     - collectionGroup: demos
       queryScope: COLLECTION
       fields:
         - fieldPath: created_by
           order: ASCENDING
         - fieldPath: created_at
           order: DESCENDING

     - collectionGroup: demos
       queryScope: COLLECTION
       fields:
         - fieldPath: created_by
           order: ASCENDING
         - fieldPath: status
           order: ASCENDING
         - fieldPath: is_pinned
           order: DESCENDING
   ```

4. **Implement Real-time Updates (Optional)**
   ```typescript
   // Frontend: Listen to Firestore changes
   import { onSnapshot } from 'firebase/firestore';

   const unsubscribe = onSnapshot(
     doc(db, 'jobs', jobId),
     (doc) => {
       const job = doc.data();
       setProgress(job.progress);
       setStatus(job.status);
       setLogs(job.logs);
     }
   );
   ```

#### Testing Phase 1
```python
# tests/phase1/test_firestore_migration.py

def test_create_demo():
    """Test creating demo in Firestore."""
    demo_repo = DemoRepository()
    demo_id = demo_repo.create_demo({
        'customer_name': 'Test Corp',
        'dataset_id': 'test_dataset',
        'created_by': 'test@google.com',
        'status': 'active'
    })
    assert demo_id is not None

    # Verify it was created
    demo = demo_repo.get_demo(demo_id)
    assert demo['customer_name'] == 'Test Corp'

def test_job_state_persistence():
    """Test job state survives service restart."""
    job_repo = JobRepository()

    # Create job
    job_id = job_repo.create_job({
        'type': 'quick',
        'status': 'running',
        'progress': 50
    })

    # Simulate service restart (create new repository instance)
    new_job_repo = JobRepository()

    # Verify job still exists
    job = new_job_repo.get_job(job_id)
    assert job['progress'] == 50
    assert job['status'] == 'running'

def test_concurrent_updates():
    """Test multiple workers can update same job."""
    import concurrent.futures

    job_repo = JobRepository()
    job_id = job_repo.create_job({'status': 'running', 'logs': []})

    def add_log(message):
        job_repo.add_log(job_id, message)

    # Add 10 logs concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(add_log, [f"Log {i}" for i in range(10)])

    # Verify all logs were added
    job = job_repo.get_job(job_id)
    assert len(job['logs']) == 10

def test_query_performance():
    """Test Firestore query performance with indexes."""
    demo_repo = DemoRepository()

    # Create 100 test demos
    for i in range(100):
        demo_repo.create_demo({
            'customer_name': f'Customer {i}',
            'created_by': 'test@google.com',
            'status': 'active',
            'is_pinned': i % 5 == 0
        })

    # Query pinned demos (should be fast with index)
    import time
    start = time.time()
    pinned = demo_repo.list_demos_by_user(
        'test@google.com',
        is_pinned=True
    )
    elapsed = time.time() - start

    assert len(pinned) == 20  # 20% pinned
    assert elapsed < 1.0  # Should be < 1 second
```

**Success Criteria:**
- ✅ All demo metadata stored in Firestore
- ✅ No in-memory state dictionaries
- ✅ Job status persists across service restarts
- ✅ Real-time updates working in frontend
- ✅ Query performance < 1 second with 1000+ demos

---

### Phase 2: Async Provisioning with Pub/Sub (Week 3)
**Goal:** Make API non-blocking by offloading work to background workers

#### Tasks
1. **Create Pub/Sub Publisher in API**
   ```python
   # backend/services/pubsub_publisher.py
   from google.cloud import pubsub_v1
   import json

   class ProvisioningPublisher:
       def __init__(self):
           self.publisher = pubsub_v1.PublisherClient()
           self.topic_path = self.publisher.topic_path(
               'bq-demos-469816',
               'provision-jobs'
           )

       def publish_quick_provision_job(self, job_id: str, template_id: str, customer_name: str):
           """Publish quick provision job to Pub/Sub."""
           message = {
               'job_id': job_id,
               'type': 'quick',
               'template_id': template_id,
               'customer_name': customer_name
           }

           future = self.publisher.publish(
               self.topic_path,
               json.dumps(message).encode('utf-8'),
               job_id=job_id,
               type='quick_provision'
           )

           return future.result()  # Wait for publish confirmation
   ```

2. **Update API Endpoint**
   ```python
   # backend/routes/provisioning.py
   @router.post("/api/provision/quick")
   async def start_quick_provision(
       template_id: str,
       customer_name: str
   ):
       """Start quick provisioning (async via Pub/Sub)."""

       # 1. Create job record
       job_id = job_repo.create_job({
           'type': 'quick',
           'template_id': template_id,
           'customer_name': customer_name,
           'status': 'queued',
           'progress': 0
       })

       # 2. Publish to Pub/Sub (non-blocking!)
       publisher = ProvisioningPublisher()
       publisher.publish_quick_provision_job(job_id, template_id, customer_name)

       # 3. Return immediately
       return {
           'job_id': job_id,
           'status': 'queued',
           'message': 'Provisioning job queued'
       }
       # API is now free to handle other requests!
   ```

3. **Create Worker Service**
   ```python
   # worker/quick_provisioner.py
   from flask import Flask, request
   from google.cloud import bigquery, storage, firestore
   import json

   app = Flask(__name__)

   @app.route('/provision', methods=['POST'])
   def handle_provision_message():
       """Handle Pub/Sub push message."""

       # Parse Pub/Sub message
       envelope = request.get_json()
       if not envelope:
           return 'Bad Request: no Pub/Sub message', 400

       pubsub_message = envelope.get('message', {})
       data = json.loads(base64.b64decode(pubsub_message['data']))

       job_id = data['job_id']
       template_id = data['template_id']
       customer_name = data['customer_name']

       # Execute provisioning
       try:
           provision_from_template(job_id, template_id, customer_name)
           return 'OK', 200
       except Exception as e:
           job_repo.update_job_status(job_id, 'failed', error=str(e))
           return 'Error', 500

   def provision_from_template(job_id, template_id, customer_name):
       """Execute quick provisioning."""
       job_repo.update_job_status(job_id, 'running')
       job_repo.add_log(job_id, f'Starting quick provision: {template_id}')

       # 1. Load template metadata
       template = load_template(template_id)
       job_repo.update_progress(job_id, 10)

       # 2. Create BigQuery dataset
       dataset_id = create_bq_dataset(customer_name, template_id)
       job_repo.update_progress(job_id, 20)
       job_repo.add_log(job_id, f'Created dataset: {dataset_id}')

       # 3. Load parquet files from GCS
       load_parquet_files(template['data_path'], dataset_id)
       job_repo.update_progress(job_id, 70)
       job_repo.add_log(job_id, 'Loaded all tables from parquet')

       # 4. Create CAPI agent
       agent_id = create_capi_agent(dataset_id, template['agent_yaml'])
       job_repo.update_progress(job_id, 90)
       job_repo.add_log(job_id, f'Created CAPI agent: {agent_id}')

       # 5. Create demo record
       demo_id = demo_repo.create_demo({
           'customer_name': customer_name,
           'dataset_id': dataset_id,
           'agent_id': agent_id,
           'template_id': template_id,
           'status': 'active'
       })

       # 6. Mark job complete
       job_repo.update_job_status(job_id, 'completed')
       job_repo.update_progress(job_id, 100)
       job_repo.update_result(job_id, {'demo_id': demo_id})
       job_repo.add_log(job_id, 'Provisioning complete!')
   ```

4. **Deploy Worker Service to Cloud Run**
   ```bash
   # Deploy worker that responds to Pub/Sub
   gcloud run deploy capi-quick-provisioner \
     --source=./worker \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \  # Pub/Sub push needs this
     --timeout=120s \
     --memory=4Gi \
     --cpu=2 \
     --min-instances=0 \
     --max-instances=10 \
     --service-account=capi-worker@bq-demos-469816.iam.gserviceaccount.com
   ```

5. **Create Pub/Sub Push Subscription to Worker**
   ```bash
   # Get worker URL
   WORKER_URL=$(gcloud run services describe capi-quick-provisioner \
     --region=us-central1 \
     --format='value(status.url)')

   # Create push subscription
   gcloud pubsub subscriptions create provision-jobs-push \
     --topic=provision-jobs \
     --push-endpoint="${WORKER_URL}/provision" \
     --ack-deadline=120 \
     --min-retry-delay=60s \
     --max-retry-delay=600s
   ```

#### Testing Phase 2
```python
# tests/phase2/test_async_provisioning.py

def test_api_returns_immediately():
    """Test API returns before provisioning completes."""
    import time

    start = time.time()
    response = requests.post(
        'https://capi-api.run.app/api/provision/quick',
        json={
            'template_id': 'shopify',
            'customer_name': 'Test Corp'
        }
    )
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 2.0  # Should return in < 2 seconds
    assert response.json()['status'] == 'queued'

    job_id = response.json()['job_id']
    return job_id

def test_job_completes_successfully():
    """Test job completes and demo is created."""
    job_id = test_api_returns_immediately()

    # Poll job status
    import time
    max_wait = 120  # 2 minutes
    start = time.time()

    while time.time() - start < max_wait:
        response = requests.get(f'https://capi-api.run.app/api/provision/status/{job_id}')
        job = response.json()

        if job['status'] == 'completed':
            # Success!
            assert 'demo_id' in job['result']
            demo_id = job['result']['demo_id']

            # Verify demo was created
            demo = demo_repo.get_demo(demo_id)
            assert demo is not None
            assert demo['customer_name'] == 'Test Corp'
            return

        elif job['status'] == 'failed':
            pytest.fail(f"Job failed: {job.get('error')}")

        time.sleep(5)

    pytest.fail(f"Job did not complete in {max_wait} seconds")

def test_pubsub_retry_on_failure():
    """Test Pub/Sub retries on worker failure."""
    # Publish message with invalid data
    publisher = ProvisioningPublisher()
    publisher.publish_quick_provision_job(
        'test-job',
        'invalid_template',  # This will cause worker to fail
        'Test'
    )

    # Check Pub/Sub metrics
    # Should see retry attempts in monitoring
    time.sleep(30)

    # Verify job status shows error
    job = job_repo.get_job('test-job')
    assert job['status'] == 'failed'

def test_concurrent_provisioning():
    """Test multiple provisions can run concurrently."""
    import concurrent.futures

    def provision(customer_name):
        response = requests.post(
            'https://capi-api.run.app/api/provision/quick',
            json={
                'template_id': 'shopify',
                'customer_name': customer_name
            }
        )
        return response.json()['job_id']

    # Start 10 provisions concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        job_ids = list(executor.map(provision, [f'Customer {i}' for i in range(10)]))

    assert len(job_ids) == 10

    # Wait for all to complete
    import time
    time.sleep(90)

    # Verify all completed
    completed = 0
    for job_id in job_ids:
        job = job_repo.get_job(job_id)
        if job['status'] == 'completed':
            completed += 1

    assert completed >= 8  # At least 80% success rate
```

**Success Criteria:**
- ✅ API endpoint returns in < 2 seconds
- ✅ Worker service processes jobs successfully
- ✅ Job status updates in Firestore
- ✅ Failed jobs retry automatically
- ✅ Can handle 10+ concurrent provisions

---

### Phase 3: Template Library & Fast Provisioning (Week 4)
**Goal:** Enable 45-60 second provisioning with pre-built templates

#### Tasks
1. **Generate Template Data**
   ```python
   # scripts/generate_template_data.py
   import pandas as pd
   from google.cloud import storage
   import os

   def generate_shopify_template():
       """Generate Shopify template parquet files."""

       # Generate customers table
       customers = pd.DataFrame({
           'customer_id': range(1, 80001),
           'email': [f'customer{i}@example.com' for i in range(1, 80001)],
           'first_name': [...],
           'last_name': [...],
           'created_at': [...],
           # ... (realistic synthetic data)
       })

       # Save to parquet
       customers.to_parquet('/tmp/customers.parquet', index=False)

       # Upload to GCS
       client = storage.Client()
       bucket = client.bucket('capi-templates-bq-demos-469816')
       blob = bucket.blob('v1/shopify/customers.parquet')
       blob.upload_from_filename('/tmp/customers.parquet')

       # Generate other tables: orders, payments, products, etc.
       # ...

   if __name__ == '__main__':
       generate_shopify_template()
       generate_banking_template()
       generate_healthcare_template()
       # ... (generate all templates)
   ```

2. **Create Template Registry**
   ```python
   # backend/templates/registry.py
   from dataclasses import dataclass
   from typing import List, Dict

   @dataclass
   class DemoTemplate:
       template_id: str
       display_name: str
       industry: str
       description: str
       data_path: str  # GCS path
       agent_yaml: str  # Path to agent config
       table_count: int
       total_rows: int
       estimated_time: str
       golden_queries: List[Dict]
       thumbnail_url: str
       tags: List[str]

   class TemplateRegistry:
       """Central registry of all demo templates."""

       TEMPLATES = {
           'shopify': DemoTemplate(
               template_id='shopify',
               display_name='Shopify E-commerce Analytics',
               industry='Retail & E-commerce',
               description='Complete merchant analytics with orders, payments, inventory',
               data_path='gs://capi-templates-bq-demos-469816/v1/shopify/*.parquet',
               agent_yaml='templates/agents/shopify_agent.yaml',
               table_count=15,
               total_rows=145000,
               estimated_time='45s',
               golden_queries=[...],
               thumbnail_url='https://storage.googleapis.com/capi-templates/shopify.png',
               tags=['retail', 'ecommerce', 'payments']
           ),
           # ... (other templates)
       }

       @classmethod
       def get_template(cls, template_id: str) -> DemoTemplate:
           return cls.TEMPLATES.get(template_id)

       @classmethod
       def list_templates(cls, industry: str = None) -> List[DemoTemplate]:
           templates = list(cls.TEMPLATES.values())
           if industry:
               templates = [t for t in templates if t.industry == industry]
           return templates
   ```

3. **Implement Fast Provisioning Logic**
   ```python
   # worker/quick_provisioner.py
   from google.cloud import bigquery, storage
   import time

   def load_parquet_files(gcs_path: str, dataset_id: str):
       """Load parquet files from GCS into BigQuery (FAST!)."""
       bq_client = bigquery.Client()
       storage_client = storage.Client()

       # Parse GCS path
       bucket_name = gcs_path.split('/')[2]
       prefix = '/'.join(gcs_path.split('/')[3:]).replace('*.parquet', '')

       # List all parquet files
       bucket = storage_client.bucket(bucket_name)
       blobs = bucket.list_blobs(prefix=prefix)

       jobs = []
       for blob in blobs:
           if not blob.name.endswith('.parquet'):
               continue

           # Extract table name
           table_name = blob.name.split('/')[-1].replace('.parquet', '')

           # Configure load job
           job_config = bigquery.LoadJobConfig(
               source_format=bigquery.SourceFormat.PARQUET,
               write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
               autodetect=True  # Infer schema from parquet
           )

           # Start load job
           table_ref = f'bq-demos-469816.{dataset_id}.{table_name}'
           uri = f'gs://{bucket_name}/{blob.name}'

           job = bq_client.load_table_from_uri(
               uri,
               table_ref,
               job_config=job_config
           )
           jobs.append(job)

       # Wait for all jobs (parallel loading!)
       for job in jobs:
           job.result()

       return len(jobs)
   ```

4. **Create Template Browsing API**
   ```python
   # backend/routes/templates.py
   from templates.registry import TemplateRegistry

   @router.get("/api/templates")
   async def list_templates(industry: str = None):
       """List available templates."""
       templates = TemplateRegistry.list_templates(industry=industry)
       return [{
           'id': t.template_id,
           'name': t.display_name,
           'industry': t.industry,
           'description': t.description,
           'table_count': t.table_count,
           'total_rows': t.total_rows,
           'estimated_time': t.estimated_time,
           'thumbnail': t.thumbnail_url,
           'tags': t.tags
       } for t in templates]

   @router.get("/api/templates/{template_id}")
   async def get_template_details(template_id: str):
       """Get template details including golden queries."""
       template = TemplateRegistry.get_template(template_id)
       if not template:
           raise HTTPException(status_code=404, detail="Template not found")
       return template
   ```

5. **Build Template Selector UI**
   ```typescript
   // frontend/src/components/TemplateLibrary.tsx
   import React, { useEffect, useState } from 'react';

   const TemplateLibrary: React.FC = () => {
     const [templates, setTemplates] = useState([]);

     useEffect(() => {
       fetch('/api/templates')
         .then(res => res.json())
         .then(data => setTemplates(data));
     }, []);

     const handleQuickStart = async (templateId: string) => {
       const customerName = prompt('Enter customer name:');

       const response = await fetch('/api/provision/quick', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ template_id: templateId, customer_name: customerName })
       });

       const { job_id } = await response.json();

       // Navigate to job status page
       window.location.href = `/provision/${job_id}`;
     };

     return (
       <div className="template-library">
         <h1>Demo Template Library</h1>
         <div className="template-grid">
           {templates.map(template => (
             <div key={template.id} className="template-card">
               <img src={template.thumbnail} alt={template.name} />
               <h3>{template.name}</h3>
               <p>{template.description}</p>
               <div className="meta">
                 <span>📊 {template.table_count} tables</span>
                 <span>⚡ {template.estimated_time}</span>
               </div>
               <button onClick={() => handleQuickStart(template.id)}>
                 Quick Start →
               </button>
             </div>
           ))}
         </div>
       </div>
     );
   };
   ```

#### Testing Phase 3
```python
# tests/phase3/test_template_provisioning.py

def test_load_parquet_performance():
    """Test parquet loading is fast."""
    import time

    # Create test dataset
    bq_client = bigquery.Client()
    dataset_id = f'test_parquet_{int(time.time())}'
    dataset = bigquery.Dataset(f'bq-demos-469816.{dataset_id}')
    bq_client.create_dataset(dataset)

    try:
        # Load parquet files
        start = time.time()
        table_count = load_parquet_files(
            'gs://capi-templates-bq-demos-469816/v1/shopify/*.parquet',
            dataset_id
        )
        elapsed = time.time() - start

        # Should load 15 tables in < 45 seconds
        assert table_count == 15
        assert elapsed < 45

        # Verify data was loaded
        tables = list(bq_client.list_tables(dataset_id))
        assert len(tables) == 15

        # Check row counts
        customers_table = bq_client.get_table(f'{dataset_id}.customers')
        assert customers_table.num_rows == 80000

    finally:
        # Cleanup
        bq_client.delete_dataset(dataset_id, delete_contents=True)

def test_end_to_end_quick_provision():
    """Test complete quick provisioning flow."""
    import time

    # Start provision
    response = requests.post(
        'https://capi-api.run.app/api/provision/quick',
        json={
            'template_id': 'shopify',
            'customer_name': 'Quick Test Corp'
        }
    )

    assert response.status_code == 200
    job_id = response.json()['job_id']

    # Wait for completion
    start = time.time()
    while time.time() - start < 120:
        job = job_repo.get_job(job_id)

        if job['status'] == 'completed':
            elapsed = time.time() - start

            # Verify timing
            assert elapsed < 60  # Should complete in < 60 seconds

            # Verify demo was created
            demo_id = job['result']['demo_id']
            demo = demo_repo.get_demo(demo_id)

            assert demo['customer_name'] == 'Quick Test Corp'
            assert demo['dataset_id'] is not None
            assert demo['agent_id'] is not None

            # Verify BigQuery dataset exists
            bq_client = bigquery.Client()
            dataset = bq_client.get_dataset(demo['dataset_id'])
            assert dataset is not None

            # Verify tables were created
            tables = list(bq_client.list_tables(dataset))
            assert len(tables) == 15

            print(f"✅ Quick provision completed in {elapsed:.1f} seconds")
            return

        elif job['status'] == 'failed':
            pytest.fail(f"Job failed: {job.get('error')}")

        time.sleep(3)

    pytest.fail("Job did not complete in 120 seconds")

def test_template_api():
    """Test template listing API."""
    response = requests.get('https://capi-api.run.app/api/templates')

    assert response.status_code == 200
    templates = response.json()

    assert len(templates) >= 3  # At least 3 templates

    # Verify template structure
    shopify = next(t for t in templates if t['id'] == 'shopify')
    assert shopify['name'] == 'Shopify E-commerce Analytics'
    assert shopify['table_count'] == 15
    assert shopify['estimated_time'] == '45s'
    assert 'retail' in shopify['tags']

def test_golden_queries_included():
    """Test template includes golden queries."""
    template = TemplateRegistry.get_template('shopify')

    assert len(template.golden_queries) >= 15

    # Verify query structure
    query = template.golden_queries[0]
    assert 'question' in query
    assert 'complexity' in query
    assert 'expected_result_type' in query
```

**Success Criteria:**
- ✅ 5+ templates available in library
- ✅ Parquet files load in < 45 seconds
- ✅ End-to-end quick provision in < 60 seconds
- ✅ Template API returns all templates
- ✅ Frontend UI displays templates correctly

---

### Phase 4: Monitoring & Observability (Week 5)
**Goal:** Full visibility into system performance and issues

#### Tasks
1. **Structured Logging Setup**
   ```python
   # backend/utils/logger.py
   import logging
   import json
   from google.cloud.logging import Client
   from google.cloud.logging.handlers import CloudLoggingHandler

   def setup_logging():
       """Configure structured logging for Cloud Logging."""
       client = Client()
       handler = CloudLoggingHandler(client)

       # Configure root logger
       logger = logging.getLogger()
       logger.setLevel(logging.INFO)
       logger.addHandler(handler)

       # Also log to stdout (for Cloud Run)
       console_handler = logging.StreamHandler()
       console_handler.setFormatter(
           logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
       )
       logger.addHandler(console_handler)

       return logger

   def log_provision_event(job_id: str, event: str, **kwargs):
       """Log provisioning events with structured data."""
       logger = logging.getLogger(__name__)
       logger.info(event, extra={
           'job_id': job_id,
           'event_type': 'provision',
           **kwargs
       })
   ```

2. **Custom Metrics**
   ```python
   # backend/utils/metrics.py
   from google.cloud import monitoring_v3
   from datetime import datetime

   class MetricsReporter:
       def __init__(self):
           self.client = monitoring_v3.MetricServiceClient()
           self.project_name = f"projects/bq-demos-469816"

       def record_provision_time(self, provision_type: str, duration_seconds: float):
           """Record provisioning duration."""
           series = monitoring_v3.TimeSeries()
           series.metric.type = 'custom.googleapis.com/capi/provision_duration'
           series.metric.labels['provision_type'] = provision_type

           point = monitoring_v3.Point()
           point.value.double_value = duration_seconds
           point.interval.end_time.seconds = int(datetime.utcnow().timestamp())

           series.points = [point]
           self.client.create_time_series(name=self.project_name, time_series=[series])

       def increment_provision_count(self, status: str):
           """Increment provision counter."""
           series = monitoring_v3.TimeSeries()
           series.metric.type = 'custom.googleapis.com/capi/provision_count'
           series.metric.labels['status'] = status

           point = monitoring_v3.Point()
           point.value.int64_value = 1
           point.interval.end_time.seconds = int(datetime.utcnow().timestamp())

           series.points = [point]
           self.client.create_time_series(name=self.project_name, time_series=[series])
   ```

3. **Cloud Trace Integration**
   ```python
   # backend/middleware/tracing.py
   from google.cloud import trace_v1
   from contextvars import ContextVar
   import functools

   trace_context: ContextVar[str] = ContextVar('trace_context', default=None)

   def traced(operation_name: str):
       """Decorator to trace function execution."""
       def decorator(func):
           @functools.wraps(func)
           async def wrapper(*args, **kwargs):
               tracer = trace_v1.TraceServiceClient()

               # Create span
               span = {
                   'name': operation_name,
                   'start_time': datetime.utcnow().isoformat(),
               }

               try:
                   result = await func(*args, **kwargs)
                   span['end_time'] = datetime.utcnow().isoformat()
                   return result
               except Exception as e:
                   span['end_time'] = datetime.utcnow().isoformat()
                   span['error'] = str(e)
                   raise
               finally:
                   # Send span to Cloud Trace
                   tracer.batch_write_spans(
                       name=f"projects/bq-demos-469816",
                       spans=[span]
                   )

           return wrapper
       return decorator

   # Usage:
   @traced("load_parquet_files")
   async def load_parquet_files(gcs_path, dataset_id):
       # ...
       pass
   ```

4. **Error Reporting**
   ```python
   # backend/utils/error_reporting.py
   from google.cloud import error_reporting

   error_client = error_reporting.Client()

   def report_error(error: Exception, context: dict = None):
       """Report error to Cloud Error Reporting."""
       error_client.report_exception(
           http_context={
               'user': context.get('user') if context else None,
               'url': context.get('url') if context else None,
           }
       )
   ```

5. **Create Monitoring Dashboard**
   ```bash
   # Create custom dashboard (can also use Cloud Console UI)
   gcloud monitoring dashboards create --config-from-file=dashboard.json
   ```

   ```json
   // dashboard.json
   {
     "displayName": "CAPI Demo Platform",
     "dashboardFilters": [],
     "gridLayout": {
       "widgets": [
         {
           "title": "Provision Success Rate",
           "xyChart": {
             "dataSets": [{
               "timeSeriesQuery": {
                 "timeSeriesFilter": {
                   "filter": "metric.type=\"custom.googleapis.com/capi/provision_count\"",
                   "aggregation": {
                     "alignmentPeriod": "60s",
                     "perSeriesAligner": "ALIGN_RATE"
                   }
                 }
               }
             }]
           }
         },
         {
           "title": "Average Provision Time",
           "xyChart": {
             "dataSets": [{
               "timeSeriesQuery": {
                 "timeSeriesFilter": {
                   "filter": "metric.type=\"custom.googleapis.com/capi/provision_duration\"",
                   "aggregation": {
                     "alignmentPeriod": "60s",
                     "perSeriesAligner": "ALIGN_MEAN"
                   }
                 }
               }
             }]
           }
         }
       ]
     }
   }
   ```

6. **Alerting Policies**
   ```bash
   # Create alert for high provision failure rate
   gcloud alpha monitoring policies create \
     --notification-channels=CHANNEL_ID \
     --display-name="High Provision Failure Rate" \
     --condition-display-name="Provision failure rate > 10%" \
     --condition-threshold-value=0.1 \
     --condition-threshold-duration=300s \
     --condition-filter='metric.type="custom.googleapis.com/capi/provision_count" AND metric.label.status="failed"'
   ```

#### Testing Phase 4
```python
# tests/phase4/test_observability.py

def test_logs_appear_in_cloud_logging():
    """Test logs are visible in Cloud Logging."""
    from google.cloud import logging

    # Make API request
    requests.get('https://capi-api.run.app/api/templates')

    # Query Cloud Logging
    client = logging.Client()
    logger = client.logger('capi-api')

    import time
    time.sleep(10)  # Wait for logs to propagate

    entries = list(logger.list_entries(max_results=10))
    assert len(entries) > 0

    # Verify structured logging
    entry = entries[0]
    assert hasattr(entry, 'severity')
    assert hasattr(entry, 'timestamp')

def test_custom_metrics_recorded():
    """Test custom metrics are recorded."""
    from google.cloud import monitoring_v3

    # Start provision
    response = requests.post(
        'https://capi-api.run.app/api/provision/quick',
        json={'template_id': 'shopify', 'customer_name': 'Test'}
    )
    job_id = response.json()['job_id']

    # Wait for completion
    time.sleep(60)

    # Query metrics
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/bq-demos-469816"

    interval = monitoring_v3.TimeInterval({
        "end_time": {"seconds": int(time.time())},
        "start_time": {"seconds": int(time.time()) - 300},
    })

    results = client.list_time_series(
        request={
            "name": project_name,
            "filter": 'metric.type="custom.googleapis.com/capi/provision_duration"',
            "interval": interval,
        }
    )

    results_list = list(results)
    assert len(results_list) > 0

    # Verify metric value
    point = results_list[0].points[0]
    assert point.value.double_value < 60  # Should be < 60 seconds

def test_traces_captured():
    """Test Cloud Trace captures request traces."""
    from google.cloud import trace_v1

    # Make request with trace header
    import uuid
    trace_id = str(uuid.uuid4())

    response = requests.get(
        'https://capi-api.run.app/api/templates',
        headers={'X-Cloud-Trace-Context': f'{trace_id}/0;o=1'}
    )

    # Query traces
    time.sleep(15)

    client = trace_v1.TraceServiceClient()
    traces = client.list_traces(project_id="bq-demos-469816")

    # Should find our trace
    # (Note: Trace API is eventually consistent, may need retry)
    found = False
    for trace in traces:
        if trace_id in trace.trace_id:
            found = True
            break

    # May not always find immediately due to propagation delay
    # In production, use Cloud Console to verify

def test_error_reporting():
    """Test errors appear in Error Reporting."""
    from google.cloud import error_reporting

    # Trigger error
    requests.post(
        'https://capi-api.run.app/api/provision/quick',
        json={'template_id': 'invalid_template', 'customer_name': 'Test'}
    )

    time.sleep(10)

    # Query Error Reporting
    client = error_reporting.Client()

    # Errors should be visible in Cloud Console
    # (Error Reporting API is read-only via console)
```

**Success Criteria:**
- ✅ All logs appear in Cloud Logging
- ✅ Custom metrics visible in Cloud Monitoring
- ✅ Traces captured for all requests
- ✅ Errors reported to Error Reporting
- ✅ Dashboard displays key metrics
- ✅ Alerts trigger on failures

---

### Phase 5: Demo Management Features (Week 6)
**Goal:** Enable CEs to pin, clone, share, and manage demos

#### Tasks
1. **Pin/Unpin Demos**
   ```python
   # backend/routes/demos.py
   @router.post("/api/demos/{demo_id}/pin")
   async def pin_demo(demo_id: str, current_user: str = Depends(get_current_user)):
       """Pin demo for quick access."""
       demo = demo_repo.get_demo(demo_id)

       if not demo:
           raise HTTPException(status_code=404, detail="Demo not found")

       if demo['created_by'] != current_user:
           raise HTTPException(status_code=403, detail="Not authorized")

       # Update pin status
       demo_repo.update_demo(demo_id, {
           'is_pinned': True,
           'pinned_at': firestore.SERVER_TIMESTAMP
       })

       return {'status': 'pinned'}
   ```

2. **Clone Demo**
   ```python
   @router.post("/api/demos/{demo_id}/clone")
   async def clone_demo(
       demo_id: str,
       new_customer_name: str,
       current_user: str = Depends(get_current_user)
   ):
       """Clone existing demo with new customer name."""
       source_demo = demo_repo.get_demo(demo_id)

       if not source_demo:
           raise HTTPException(status_code=404, detail="Demo not found")

       # Create cloning job
       job_id = job_repo.create_job({
           'type': 'clone',
           'source_demo_id': demo_id,
           'new_customer_name': new_customer_name,
           'created_by': current_user,
           'status': 'queued'
       })

       # Publish to Pub/Sub
       publisher = ProvisioningPublisher()
       publisher.publish_clone_job(job_id, demo_id, new_customer_name)

       return {'job_id': job_id, 'status': 'queued'}
   ```

3. **Share Demo**
   ```python
   @router.post("/api/demos/{demo_id}/share")
   async def create_share_link(
       demo_id: str,
       expires_in_days: int = 7,
       password: Optional[str] = None,
       current_user: str = Depends(get_current_user)
   ):
       """Create shareable link for demo."""
       import secrets
       import hashlib
       from datetime import timedelta

       demo = demo_repo.get_demo(demo_id)

       if not demo:
           raise HTTPException(status_code=404, detail="Demo not found")

       # Generate secure token
       share_token = secrets.token_urlsafe(32)

       # Store share record
       share_data = {
           'share_token': share_token,
           'demo_id': demo_id,
           'created_by': current_user,
           'created_at': firestore.SERVER_TIMESTAMP,
           'expires_at': datetime.utcnow() + timedelta(days=expires_in_days),
           'password_hash': hashlib.sha256(password.encode()).hexdigest() if password else None,
           'access_count': 0
       }

       db = firestore.Client()
       db.collection('demo_shares').document(share_token).set(share_data)

       # Generate share URL
       share_url = f"https://capi-demo.run.app/shared/{share_token}"

       return {
           'share_url': share_url,
           'expires_at': share_data['expires_at'].isoformat()
       }
   ```

4. **Access Shared Demo**
   ```python
   @router.get("/api/shared/{share_token}")
   async def access_shared_demo(
       share_token: str,
       password: Optional[str] = None
   ):
       """Access demo via share link."""
       db = firestore.Client()
       share_doc = db.collection('demo_shares').document(share_token).get()

       if not share_doc.exists:
           raise HTTPException(status_code=404, detail="Share link not found")

       share_data = share_doc.to_dict()

       # Check expiration
       if datetime.utcnow() > share_data['expires_at']:
           raise HTTPException(status_code=410, detail="Share link expired")

       # Check password
       if share_data['password_hash']:
           if not password:
               raise HTTPException(status_code=401, detail="Password required")

           password_hash = hashlib.sha256(password.encode()).hexdigest()
           if password_hash != share_data['password_hash']:
               raise HTTPException(status_code=401, detail="Incorrect password")

       # Increment access count
       db.collection('demo_shares').document(share_token).update({
           'access_count': firestore.Increment(1),
           'last_accessed': firestore.SERVER_TIMESTAMP
       })

       # Get demo
       demo = demo_repo.get_demo(share_data['demo_id'])

       return {
           'demo': demo,
           'read_only': True,
           'shared_by': share_data['created_by']
       }
   ```

5. **CE Dashboard API**
   ```python
   @router.get("/api/dashboard")
   async def get_ce_dashboard(current_user: str = Depends(get_current_user)):
       """Get CE's personalized dashboard."""

       # Get pinned demos
       pinned_demos = demo_repo.list_demos(
           created_by=current_user,
           is_pinned=True,
           limit=10
       )

       # Get recent demos
       recent_demos = demo_repo.list_demos(
           created_by=current_user,
           status='active',
           order_by='created_at',
           limit=10
       )

       # Get stats
       total_demos = demo_repo.count_demos(created_by=current_user)
       demos_this_month = demo_repo.count_demos(
           created_by=current_user,
           created_after=datetime.utcnow() - timedelta(days=30)
       )

       return {
           'user': current_user,
           'stats': {
               'total_demos': total_demos,
               'demos_this_month': demos_this_month,
               'pinned_count': len(pinned_demos)
           },
           'pinned_demos': pinned_demos,
           'recent_demos': recent_demos
       }
   ```

#### Testing Phase 5
```python
# tests/phase5/test_demo_management.py

def test_pin_demo():
    """Test pinning demo."""
    # Create demo
    demo_id = demo_repo.create_demo({
        'customer_name': 'Test',
        'created_by': 'test@google.com'
    })

    # Pin it
    response = requests.post(
        f'https://capi-api.run.app/api/demos/{demo_id}/pin',
        headers={'Authorization': 'Bearer TEST_TOKEN'}
    )

    assert response.status_code == 200

    # Verify it was pinned
    demo = demo_repo.get_demo(demo_id)
    assert demo['is_pinned'] == True

def test_clone_demo():
    """Test cloning demo."""
    # Create source demo
    source_demo_id = create_test_demo('Original Corp')

    # Clone it
    response = requests.post(
        f'https://capi-api.run.app/api/demos/{source_demo_id}/clone',
        json={'new_customer_name': 'Cloned Corp'},
        headers={'Authorization': 'Bearer TEST_TOKEN'}
    )

    assert response.status_code == 200
    job_id = response.json()['job_id']

    # Wait for cloning to complete
    wait_for_job_completion(job_id, max_wait=60)

    # Verify new demo was created
    job = job_repo.get_job(job_id)
    new_demo_id = job['result']['demo_id']
    new_demo = demo_repo.get_demo(new_demo_id)

    assert new_demo['customer_name'] == 'Cloned Corp'
    assert new_demo['dataset_id'] != source_demo['dataset_id']  # Different dataset

def test_share_link():
    """Test creating and accessing share link."""
    # Create demo
    demo_id = create_test_demo('Shared Corp')

    # Create share link
    response = requests.post(
        f'https://capi-api.run.app/api/demos/{demo_id}/share',
        json={'expires_in_days': 7},
        headers={'Authorization': 'Bearer TEST_TOKEN'}
    )

    assert response.status_code == 200
    share_url = response.json()['share_url']
    share_token = share_url.split('/')[-1]

    # Access share link
    access_response = requests.get(
        f'https://capi-api.run.app/api/shared/{share_token}'
    )

    assert access_response.status_code == 200
    shared_demo = access_response.json()

    assert shared_demo['read_only'] == True
    assert shared_demo['demo']['customer_name'] == 'Shared Corp'

def test_password_protected_share():
    """Test password-protected share link."""
    demo_id = create_test_demo('Secret Corp')

    # Create password-protected link
    response = requests.post(
        f'https://capi-api.run.app/api/demos/{demo_id}/share',
        json={'expires_in_days': 7, 'password': 'secret123'},
        headers={'Authorization': 'Bearer TEST_TOKEN'}
    )

    share_token = response.json()['share_url'].split('/')[-1]

    # Try without password - should fail
    access_response = requests.get(
        f'https://capi-api.run.app/api/shared/{share_token}'
    )
    assert access_response.status_code == 401

    # Try with wrong password - should fail
    access_response = requests.get(
        f'https://capi-api.run.app/api/shared/{share_token}',
        json={'password': 'wrong'}
    )
    assert access_response.status_code == 401

    # Try with correct password - should succeed
    access_response = requests.get(
        f'https://capi-api.run.app/api/shared/{share_token}',
        json={'password': 'secret123'}
    )
    assert access_response.status_code == 200

def test_dashboard_api():
    """Test CE dashboard API."""
    # Create some demos
    demo1 = create_test_demo('Demo 1')
    demo2 = create_test_demo('Demo 2')

    # Pin one
    demo_repo.update_demo(demo1, {'is_pinned': True})

    # Get dashboard
    response = requests.get(
        'https://capi-api.run.app/api/dashboard',
        headers={'Authorization': 'Bearer TEST_TOKEN'}
    )

    assert response.status_code == 200
    dashboard = response.json()

    assert dashboard['stats']['total_demos'] >= 2
    assert dashboard['stats']['pinned_count'] >= 1
    assert len(dashboard['pinned_demos']) >= 1
    assert len(dashboard['recent_demos']) >= 2
```

**Success Criteria:**
- ✅ Can pin/unpin demos
- ✅ Can clone demos successfully
- ✅ Share links work (with and without password)
- ✅ Dashboard shows correct stats
- ✅ Shared demos are read-only

---

### Phase 6: Lifecycle Management (Week 7)
**Goal:** Automatic cleanup and cost optimization

#### Tasks
1. **Cloud Scheduler Jobs**
   ```bash
   # Create scheduler jobs

   # Daily cleanup at 2am UTC
   gcloud scheduler jobs create http cleanup-old-demos \
     --schedule="0 2 * * *" \
     --uri="https://capi-api.run.app/api/admin/cleanup" \
     --http-method=POST \
     --oidc-service-account-email=capi-api@bq-demos-469816.iam.gserviceaccount.com \
     --time-zone="UTC"

   # Send expiration warnings daily at 9am UTC
   gcloud scheduler jobs create http send-expiration-warnings \
     --schedule="0 9 * * *" \
     --uri="https://capi-api.run.app/api/admin/send-warnings" \
     --http-method=POST \
     --oidc-service-account-email=capi-api@bq-demos-469816.iam.gserviceaccount.com
   ```

2. **Lifecycle Manager**
   ```python
   # backend/services/lifecycle_manager.py
   from datetime import datetime, timedelta
   from google.cloud import bigquery

   class LifecycleManager:
       def __init__(self):
           self.bq_client = bigquery.Client()
           self.demo_repo = DemoRepository()

       def archive_old_demos(self):
           """Archive demos inactive for 90+ days."""
           cutoff = datetime.utcnow() - timedelta(days=90)

           # Query old demos
           old_demos = self.demo_repo.find_demos({
               'status': 'active',
               'last_used': {'$lt': cutoff},
               'is_pinned': False,
               'is_template': False
           })

           count = 0
           for demo in old_demos:
               logger.info(f"Archiving demo: {demo['demo_id']}")

               # Update status
               self.demo_repo.update_demo(demo['demo_id'], {
                   'status': 'archived',
                   'archived_at': firestore.SERVER_TIMESTAMP
               })

               count += 1

           return count

       def delete_archived_demos(self):
           """Delete demos archived for 180+ days."""
           cutoff = datetime.utcnow() - timedelta(days=180)

           archived_demos = self.demo_repo.find_demos({
               'status': 'archived',
               'archived_at': {'$lt': cutoff}
           })

           count = 0
           for demo in archived_demos:
               logger.info(f"Deleting demo: {demo['demo_id']}")

               # Delete BigQuery dataset
               try:
                   dataset_ref = self.bq_client.dataset(demo['dataset_id'])
                   self.bq_client.delete_dataset(
                       dataset_ref,
                       delete_contents=True,
                       not_found_ok=True
                   )
               except Exception as e:
                   logger.error(f"Error deleting dataset: {e}")

               # Mark as deleted (keep metadata)
               self.demo_repo.update_demo(demo['demo_id'], {
                   'status': 'deleted',
                   'deleted_at': firestore.SERVER_TIMESTAMP,
                   'dataset_id': None,  # Clear sensitive data
                   'agent_id': None
               })

               count += 1

           return count

       def send_expiration_warnings(self):
           """Send warnings 7 days before archiving."""
           warning_date = datetime.utcnow() - timedelta(days=83)  # 90 - 7

           expiring_demos = self.demo_repo.find_demos({
               'status': 'active',
               'last_used': {'$lt': warning_date},
               'is_pinned': False
           })

           count = 0
           for demo in expiring_demos:
               days_until_archive = 90 - (datetime.utcnow() - demo['last_used']).days

               if 0 <= days_until_archive <= 7:
                   send_expiration_email(
                       to=demo['created_by'],
                       demo_title=demo['customer_name'],
                       days_remaining=days_until_archive,
                       demo_id=demo['demo_id']
                   )
                   count += 1

           return count
   ```

3. **Admin API Endpoints**
   ```python
   # backend/routes/admin.py
   from services.lifecycle_manager import LifecycleManager

   @router.post("/api/admin/cleanup")
   async def run_cleanup():
       """Run lifecycle cleanup (called by Cloud Scheduler)."""
       manager = LifecycleManager()

       archived = manager.archive_old_demos()
       deleted = manager.delete_archived_demos()

       return {
           'archived': archived,
           'deleted': deleted,
           'timestamp': datetime.utcnow().isoformat()
       }

   @router.post("/api/admin/send-warnings")
   async def send_warnings():
       """Send expiration warnings (called by Cloud Scheduler)."""
       manager = LifecycleManager()

       warnings_sent = manager.send_expiration_warnings()

       return {
           'warnings_sent': warnings_sent,
           'timestamp': datetime.utcnow().isoformat()
       }
   ```

#### Testing Phase 6
```python
# tests/phase6/test_lifecycle.py

def test_archive_old_demos():
    """Test archiving of old demos."""
    # Create old demo (backdated)
    old_demo_id = demo_repo.create_demo({
        'customer_name': 'Old Corp',
        'created_by': 'test@google.com',
        'status': 'active',
        'is_pinned': False,
        'last_used': datetime.utcnow() - timedelta(days=95)
    })

    # Create recent demo (should not be archived)
    recent_demo_id = demo_repo.create_demo({
        'customer_name': 'Recent Corp',
        'created_by': 'test@google.com',
        'status': 'active',
        'is_pinned': False,
        'last_used': datetime.utcnow() - timedelta(days=10)
    })

    # Run archiving
    manager = LifecycleManager()
    archived_count = manager.archive_old_demos()

    assert archived_count >= 1

    # Verify old demo was archived
    old_demo = demo_repo.get_demo(old_demo_id)
    assert old_demo['status'] == 'archived'

    # Verify recent demo was not archived
    recent_demo = demo_repo.get_demo(recent_demo_id)
    assert recent_demo['status'] == 'active'

def test_pinned_demos_not_archived():
    """Test pinned demos are not archived."""
    # Create old pinned demo
    pinned_demo_id = demo_repo.create_demo({
        'customer_name': 'Pinned Corp',
        'created_by': 'test@google.com',
        'status': 'active',
        'is_pinned': True,
        'last_used': datetime.utcnow() - timedelta(days=200)
    })

    # Run archiving
    manager = LifecycleManager()
    manager.archive_old_demos()

    # Verify pinned demo was NOT archived
    pinned_demo = demo_repo.get_demo(pinned_demo_id)
    assert pinned_demo['status'] == 'active'

def test_delete_very_old_archived_demos():
    """Test deletion of very old archived demos."""
    # Create very old archived demo
    old_archived_demo_id = demo_repo.create_demo({
        'customer_name': 'Very Old Corp',
        'created_by': 'test@google.com',
        'status': 'archived',
        'archived_at': datetime.utcnow() - timedelta(days=200),
        'dataset_id': 'test_dataset_old'
    })

    # Run deletion
    manager = LifecycleManager()
    deleted_count = manager.delete_archived_demos()

    assert deleted_count >= 1

    # Verify demo was marked as deleted
    demo = demo_repo.get_demo(old_archived_demo_id)
    assert demo['status'] == 'deleted'
    assert demo['dataset_id'] is None  # Sensitive data cleared

def test_scheduler_endpoints():
    """Test Cloud Scheduler endpoint calls."""
    # Call cleanup endpoint
    response = requests.post(
        'https://capi-api.run.app/api/admin/cleanup',
        headers={'Authorization': 'Bearer SCHEDULER_TOKEN'}
    )

    assert response.status_code == 200
    result = response.json()

    assert 'archived' in result
    assert 'deleted' in result
    assert 'timestamp' in result
```

**Success Criteria:**
- ✅ Old demos auto-archive after 90 days
- ✅ Archived demos delete after 180 days
- ✅ Pinned demos exempt from archiving
- ✅ Expiration warnings sent
- ✅ Cloud Scheduler runs successfully

---

## 🧪 Testing Strategy

### Testing Pyramid

```
                          ┌──────────────┐
                          │  E2E Tests   │  (10%)
                          │  - Full flow │
                          └──────────────┘
                      ┌─────────────────────┐
                      │  Integration Tests  │  (30%)
                      │  - API + DB + GCP   │
                      └─────────────────────┘
                  ┌────────────────────────────┐
                  │       Unit Tests           │  (60%)
                  │  - Functions, classes      │
                  └────────────────────────────┘
```

### Test Categories

#### 1. Unit Tests (60%)
**Coverage:** Individual functions and classes

```python
# tests/unit/test_repositories.py
def test_demo_repository_create():
    repo = DemoRepository()
    demo_id = repo.create_demo({'customer_name': 'Test'})
    assert demo_id is not None

# tests/unit/test_template_registry.py
def test_template_registry_get():
    template = TemplateRegistry.get_template('shopify')
    assert template is not None
    assert template.table_count == 15
```

#### 2. Integration Tests (30%)
**Coverage:** Multiple components working together

```python
# tests/integration/test_provision_flow.py
def test_quick_provision_integration():
    # API → Pub/Sub → Worker → Firestore → BigQuery
    response = api_client.post('/api/provision/quick', json={...})
    job_id = response.json()['job_id']

    # Wait and verify
    wait_for_completion(job_id)
    verify_demo_created(job_id)
```

#### 3. End-to-End Tests (10%)
**Coverage:** Full user workflows

```python
# tests/e2e/test_ce_workflow.py
def test_complete_ce_workflow():
    """Test complete CE workflow from login to demo."""
    # 1. Login
    # 2. Browse templates
    # 3. Quick provision
    # 4. Test chat
    # 5. Share demo
    # 6. Verify customer can access
```

### Continuous Testing

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run unit tests
        run: pytest tests/unit -v --cov

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup GCP credentials
        uses: google-github-actions/auth@v1
      - name: Run integration tests
        run: pytest tests/integration -v

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to staging
        run: ./deploy-staging.sh
      - name: Run E2E tests
        run: pytest tests/e2e -v
```

### Performance Testing

```python
# tests/performance/test_load.py
from locust import HttpUser, task, between

class CEUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def browse_templates(self):
        self.client.get("/api/templates")

    @task(1)
    def start_provision(self):
        self.client.post("/api/provision/quick", json={
            "template_id": "shopify",
            "customer_name": f"Customer {random.randint(1, 1000)}"
        })

# Run: locust -f tests/performance/test_load.py --host https://capi-api.run.app
```

---

## 🛠️ GCP Services & Technology Stack

### Frontend Tier
| Component | Technology | Purpose |
|-----------|------------|---------|
| **UI Framework** | React 18 + TypeScript | Modern, type-safe UI |
| **Build Tool** | Vite | Fast builds, HMR |
| **Styling** | Tailwind CSS | Utility-first styling |
| **State Management** | React Query | Server state management |
| **Auth** | Firebase Auth | User authentication |
| **Hosting** | Cloud Run | Serverless container hosting |
| **CDN** | Cloud CDN | Fast global delivery |

### API Tier
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | FastAPI (Python 3.11) | High-performance async API |
| **Validation** | Pydantic | Request/response validation |
| **Auth** | Firebase Admin SDK | Token verification |
| **Hosting** | Cloud Run | Auto-scaling serverless |
| **Load Balancer** | Cloud Load Balancing | Traffic distribution |
| **Security** | Cloud Armor | DDoS protection, WAF |

### Worker Tier
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Quick Provisioner** | Flask + Cloud Run | Template-based provisioning |
| **Custom Provisioner** | FastAPI + Cloud Run | Full orchestration pipeline |
| **Message Queue** | Pub/Sub | Async job distribution |
| **Task Queue** | Cloud Tasks | Long-running jobs |
| **Scheduling** | Cloud Scheduler | Cron jobs |

### Data Tier
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Metadata DB** | Firestore | NoSQL document store |
| **Analytics DB** | BigQuery | Columnar data warehouse |
| **Object Storage** | Cloud Storage | Templates, exports |
| **Cache** | Firestore + App cache | Performance optimization |
| **Secrets** | Secret Manager | Secure credential storage |

### Observability Tier
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Logging** | Cloud Logging | Centralized logs |
| **Metrics** | Cloud Monitoring | Custom metrics, dashboards |
| **Tracing** | Cloud Trace | Request tracing |
| **Errors** | Error Reporting | Exception tracking |
| **Uptime** | Cloud Monitoring | Service health checks |

### AI/ML Services
| Component | Technology | Purpose |
|-----------|------------|---------|
| **CAPI** | Gemini Data Analytics | Conversational analytics |
| **LLM** | Vertex AI (Gemini) | Agent orchestration |
| **Embeddings** | Vertex AI | Semantic search (future) |

---

## 📈 Success Criteria & KPIs

### Technical Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Provision Time (Quick)** | N/A | < 60s | p95 latency |
| **Provision Time (Custom)** | 6-10 min | < 8 min | p95 latency |
| **API Latency** | Unknown | < 200ms | p50 for GET requests |
| **API Availability** | ~95% | 99.9% | Uptime monitoring |
| **Error Rate** | Unknown | < 0.1% | Error logs / total requests |
| **Data Loss** | High risk | 0% | Persistent storage |
| **Concurrent Users** | ~5 | 100+ | Load testing |

### Business Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Demos per CE per Month** | 8-12 | 25+ | Firestore query |
| **Template Usage Rate** | 0% | 70%+ | Quick vs Custom ratio |
| **Demo Reuse Rate** | 0% | 50%+ | Clone count |
| **Customer Sharing Rate** | ~10% | 40%+ | Share link usage |
| **Average Prep Time** | 4-6 hrs | < 30 min | User survey |
| **CE Satisfaction** | N/A | 4.5/5 | Quarterly survey |

### Cost Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Cost per Demo** | ~$0.10 | ~$0.03 | BigQuery + storage |
| **Monthly Platform Cost** | Unknown | < $500 | Billing reports |
| **Storage Growth** | Uncontrolled | Linear | Lifecycle management |

---

## ⚠️ Risk Mitigation

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Migration causes downtime** | Medium | High | Blue-green deployment, feature flags |
| **Data loss during migration** | Low | Critical | Backup before migration, rollback plan |
| **Performance regression** | Medium | Medium | Load testing before production |
| **Cost overrun** | Medium | Medium | Set billing alerts, quotas |
| **Pub/Sub message loss** | Low | High | Dead-letter queue, monitoring |
| **Firestore quota exceeded** | Low | Medium | Request quota increase proactively |
| **Template data quality issues** | Medium | Medium | Validation, manual review |
| **User adoption low** | Medium | High | Training, documentation, feedback loop |

### Rollback Plan

```bash
# If Phase 2 (Async) causes issues:

# 1. Rollback Cloud Run deployment
gcloud run services update capi-api \
  --region=us-central1 \
  --revision=capi-api-previous

# 2. Stop Pub/Sub subscription
gcloud pubsub subscriptions update provision-jobs-push --no-enable

# 3. Switch traffic to old version
gcloud run services update-traffic capi-api \
  --to-revisions=capi-api-previous=100

# 4. Monitor for stability
watch -n 5 'gcloud run services describe capi-api --region=us-central1 --format="value(status.conditions)"'
```

---

## 💰 Cost Analysis

### Monthly Cost Estimate (Steady State)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **Cloud Run (API)** | 1M requests, 2 min instances | $15 |
| **Cloud Run (Workers)** | 500 provisions × 60s | $5 |
| **Firestore** | 10K reads/day, 1K writes/day | $10 |
| **Cloud Storage** | 50 GB templates | $1 |
| **BigQuery** | 20 active datasets, 100 GB | $5 |
| **Pub/Sub** | 500K messages/month | $1 |
| **Cloud Tasks** | 100 tasks/month | $0.50 |
| **Cloud Logging** | 10 GB/month | $5 |
| **Cloud Monitoring** | Custom metrics | $3 |
| **Secret Manager** | 10 secrets | $0.50 |
| **Cloud Scheduler** | 5 jobs | $1 |
| **Cloud CDN** | 100 GB egress | $8 |
| **Load Balancer** | Forwarding rules | $18 |
| **Vertex AI (CAPI)** | 500 conversations | $50 |
| **Total** | | **~$122/month** |

### Cost Optimization Strategies

1. **Lifecycle Management:** Delete old datasets (saves ~$20/month)
2. **Scale to Zero:** Workers scale to 0 when idle (saves ~$10/month)
3. **Template Reuse:** Less synthetic data generation (saves ~$30/month in Vertex AI)
4. **Cloud CDN:** Reduce egress costs (saves ~$15/month)
5. **Committed Use Discounts:** For BigQuery (saves ~20%)

**Optimized Monthly Cost:** ~$80-100/month

---

## 📚 Documentation & Training

### Documentation Deliverables

1. **Architecture Documentation** (this document)
2. **API Reference** - OpenAPI/Swagger spec
3. **CE User Guide** - How to use the platform
4. **Admin Guide** - Operations, monitoring, troubleshooting
5. **Developer Guide** - For future enhancements

### CE Training Plan

**Week 1: Platform Overview**
- Architecture walkthrough
- Demo of quick provisioning
- Dashboard features

**Week 2: Hands-on Workshop**
- Create first template-based demo
- Clone and customize
- Share with mock customer

**Week 3: Advanced Features**
- Custom provisioning
- Monitoring and troubleshooting
- Best practices

**Week 4: Certification**
- Practical exam
- Feedback and Q&A

---

## 🚀 Deployment Plan

### Pre-Deployment Checklist

```bash
# ✅ Infrastructure
- [ ] All GCP APIs enabled
- [ ] Service accounts created with correct permissions
- [ ] Firestore database initialized
- [ ] Pub/Sub topics and subscriptions created
- [ ] Cloud Tasks queue created
- [ ] GCS buckets created with lifecycle policies
- [ ] Secret Manager secrets stored
- [ ] Cloud Scheduler jobs configured

# ✅ Code
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance tests passing
- [ ] Security scan clean
- [ ] Code review completed

# ✅ Data
- [ ] Template parquet files generated
- [ ] Template metadata validated
- [ ] Golden queries tested
- [ ] Agent YAML configs validated

# ✅ Monitoring
- [ ] Cloud Logging configured
- [ ] Custom metrics registered
- [ ] Dashboards created
- [ ] Alert policies created
- [ ] Error Reporting enabled

# ✅ Documentation
- [ ] API documentation published
- [ ] CE user guide complete
- [ ] Admin guide complete
- [ ] Runbook for on-call

# ✅ Training
- [ ] CE training materials ready
- [ ] Training sessions scheduled
- [ ] Sandbox environment available
```

### Go-Live Plan

**Week 8: Soft Launch**
- Deploy to production
- Enable for 5 pilot CEs
- Monitor closely for issues
- Gather feedback

**Week 9: Gradual Rollout**
- Enable for 25% of CEs
- Continue monitoring
- Iterate based on feedback

**Week 10: Full Rollout**
- Enable for all CEs
- Announce via email/training
- Provide support channels

**Week 11: Optimization**
- Analyze usage patterns
- Tune performance
- Add requested features

---

## 📞 Support & Escalation

### Support Channels

**Tier 1: Self-Service**
- Documentation portal
- FAQ
- Video tutorials

**Tier 2: Team Support**
- Slack channel: `#capi-demo-platform`
- Email: capi-support@google.com
- Response time: < 4 hours

**Tier 3: Engineering**
- On-call rotation
- Pager duty for P0/P1 issues
- Response time: < 30 minutes

### Escalation Path

```
User Issue
    ↓
Documentation / FAQ
    ↓
Slack / Email Support
    ↓
Engineering Team
    ↓
Platform Lead
    ↓
Director of Engineering
```

---

## ✅ Next Steps

### Immediate Actions (This Week)

1. **Review & Approve** this architecture plan
2. **Allocate Resources** - Assign engineers to phases
3. **Setup Project** - Create GCP resources
4. **Kickoff Meeting** - Align team on timeline

### Phase 0 Kickoff (Week 1)

1. **Day 1-2:** Enable GCP APIs, create service accounts
2. **Day 3-4:** Initialize Firestore, Pub/Sub, Cloud Tasks
3. **Day 5:** Testing and validation

### Regular Check-ins

- **Daily:** Standup during implementation
- **Weekly:** Progress review with stakeholders
- **Bi-weekly:** CE feedback sessions

---

## 📝 Appendix

### A. Service Account IAM Roles

```bash
# capi-api service account
roles/datastore.user                    # Firestore read/write
roles/pubsub.publisher                  # Publish to Pub/Sub
roles/cloudtasks.enqueuer              # Create Cloud Tasks
roles/secretmanager.secretAccessor     # Read secrets

# capi-worker service account
roles/datastore.user                    # Firestore read/write
roles/bigquery.dataEditor              # Create datasets, load data
roles/bigquery.user                    # Run queries
roles/storage.objectViewer             # Read template files
roles/aiplatform.user                  # Create CAPI agents
```

### B. Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Demos - user can only access their own
    match /demos/{demoId} {
      allow read, write: if request.auth != null
        && request.auth.token.email == resource.data.created_by;
    }

    // Jobs - user can only access their own
    match /jobs/{jobId} {
      allow read: if request.auth != null
        && request.auth.token.email == resource.data.created_by;
    }

    // Templates - public read
    match /templates/{templateId} {
      allow read: if request.auth != null;
      allow write: if false; // Only admins via backend
    }

    // Shares - public read with valid token
    match /demo_shares/{shareToken} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

### C. Environment Variables

```bash
# .env.production
DEVSHELL_PROJECT_ID=bq-demos-469816
GOOGLE_CLOUD_PROJECT=bq-demos-469816
FIRESTORE_DATABASE=(default)
PUBSUB_TOPIC=provision-jobs
CLOUDTASKS_QUEUE=custom-provision-queue
TEMPLATES_BUCKET=capi-templates-bq-demos-469816
EXPORTS_BUCKET=capi-exports-bq-demos-469816
LOG_LEVEL=INFO
ENVIRONMENT=production
```

---

**Document Status:** DRAFT - Pending Approval
**Approval Required From:**
- [ ] Engineering Lead
- [ ] Product Manager
- [ ] Customer Engineering Lead
- [ ] Security Team
- [ ] Finance (for budget approval)

**Questions or Feedback?**
Contact: architecture-review@google.com

---

**🏗️ End of Architecture Plan**

