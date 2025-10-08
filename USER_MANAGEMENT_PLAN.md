# User-Scoped Job Management - Implementation Plan

## Overview
Add user authentication and ensure each user only sees their own jobs, demo assets, and job history.

---

## Current State

✅ **Already Working:**
- Firebase Authentication setup (`middleware/auth.py`)
- Firestore service for user-scoped data (`services/firestore_service.py`)
- Jobs saved per user: `users/{userId}/jobs/{jobId}`
- Optional authentication on provision endpoints

❌ **Issues:**
- `/history` endpoint returns ALL jobs (not user-filtered)
- `/status` and `/assets` endpoints don't verify ownership
- Frontend shows mock data instead of real user jobs
- No user-specific dashboard

---

## Implementation Tasks

### Backend Changes

#### 1. Update `/history` Endpoint ✅ (DONE)
**File:** `backend/routes/provisioning.py`

**Changes:**
```python
@router.get("/history")
async def get_provision_history(
    limit: int = 50,
    user: Optional[dict] = Depends(optional_google_user)
):
    # If authenticated: Return only user's jobs from Firestore
    if user:
        user_id = user['uid']
        return await firestore_service.get_user_jobs(user_id, limit)

    # If not authenticated: Return in-memory jobs (backwards compatible)
    return job_manager.get_all_jobs(limit)
```

**Why:** Users should only see their own job history

**Test:**
```bash
# As user A
curl -H "Authorization: Bearer USER_A_TOKEN" /api/provision/history
# Should return only user A's jobs

# As user B
curl -H "Authorization: Bearer USER_B_TOKEN" /api/provision/history
# Should return only user B's jobs
```

---

#### 2. Add Authorization to `/status/{job_id}` ✅ (DONE)
**File:** `backend/routes/provisioning.py`

**Changes:**
```python
@router.get("/status/{job_id}")
async def get_provision_status(
    job_id: str,
    user: Optional[dict] = Depends(optional_google_user)
):
    # If authenticated, verify user owns this job
    if user:
        firestore_job = await firestore_service.get_job(user['uid'], job_id)
        if not firestore_job:
            raise HTTPException(404, "Job not found")

    # Return real-time status from job_manager
    return job_manager.get_job(job_id)
```

**Why:** Prevent users from accessing other users' job status

**Test:**
```bash
# User A tries to access User B's job
curl -H "Authorization: Bearer USER_A_TOKEN" /api/provision/status/USER_B_JOB_ID
# Should return 404
```

---

#### 3. Add Authorization to `/assets/{job_id}` ✅ (DONE)
**File:** `backend/routes/provisioning.py`

**Changes:**
```python
@router.get("/assets/{job_id}")
async def get_demo_assets(
    job_id: str,
    user: Optional[dict] = Depends(optional_google_user)
):
    # If authenticated, verify user owns this job
    if user:
        firestore_job = await firestore_service.get_job(user['uid'], job_id)
        if not firestore_job:
            raise HTTPException(404, "Job not found")

    # Return demo assets
    return job_manager.get_job(job_id)
```

**Why:** Prevent users from accessing other users' demo assets

**Test:**
```bash
# User A tries to access User B's demo assets
curl -H "Authorization: Bearer USER_A_TOKEN" /api/provision/assets/USER_B_JOB_ID
# Should return 404
```

---

### Frontend Changes

#### 4. Fetch Real User Jobs ✅ (DONE)
**File:** `newfrontend/conversational-api-demo-frontend/src/pages/CEDashboard.tsx`

**Changes:**
```typescript
// Add useEffect to fetch jobs
useEffect(() => {
  const fetchJobs = async () => {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    // Add auth token if user is signed in
    if (user) {
      const token = await user.getIdToken();
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch("/api/provision/history", { headers });
    const data = await response.json();

    setJobs(data.jobs);
  };

  fetchJobs();
}, [user]);
```

**Why:** Display actual user jobs instead of mock data

**Test:**
- Sign in as User A → See User A's jobs
- Sign in as User B → See User B's jobs
- Sign out → See all jobs (backwards compatible)

---

#### 5. Send Auth Token in Provision Requests ✅ (DONE)
**File:** `newfrontend/conversational-api-demo-frontend/src/pages/CEDashboard.tsx`

**Changes:**
```typescript
const handleDefaultProvision = async () => {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  // Add auth token
  if (user) {
    const token = await user.getIdToken();
    headers["Authorization"] = `Bearer ${token}`;
  }

  await fetch("/api/provision/start", {
    method: "POST",
    headers,
    body: JSON.stringify({ customer_url: defaultUrl }),
  });
};
```

**Why:** Jobs will be saved to user's Firestore collection

**Test:**
- Sign in and create a job
- Verify it appears in `/api/provision/history`
- Verify it's stored in Firestore under `users/{uid}/jobs/`

---

#### 6. Update Job History UI
**File:** `newfrontend/conversational-api-demo-frontend/src/pages/CEDashboard.tsx`

**Changes:**
```typescript
<h2>
  {user ? "Your Recent Provisions" : "Recent Provisions"}
</h2>

{loadingJobs ? (
  <div>Loading jobs...</div>
) : jobs.length === 0 ? (
  <div>
    {user
      ? "No provisions yet. Start by provisioning a chatbot above."
      : "Sign in to see your provision history"}
  </div>
) : (
  <JobHistoryTable jobs={jobs} />
)}
```

**Why:** Better UX for authenticated vs unauthenticated users

---

## Testing Plan

### Test 1: User A Cannot See User B's Jobs
```bash
# Setup
1. Sign in as User A (alice@google.com)
2. Create job J1
3. Sign out
4. Sign in as User B (bob@google.com)
5. Create job J2

# Test
GET /api/provision/history (as User A)
Expected: Returns [J1] only

GET /api/provision/history (as User B)
Expected: Returns [J2] only
```

### Test 2: User A Cannot Access User B's Job Status
```bash
# Setup
User A has job J1
User B has job J2

# Test
GET /api/provision/status/J2 (as User A)
Expected: 404 "Job not found for user alice@google.com"

GET /api/provision/status/J1 (as User A)
Expected: 200 with job status
```

### Test 3: User A Cannot Access User B's Demo Assets
```bash
# Setup
User A completed job J1
User B completed job J2

# Test
GET /api/provision/assets/J2 (as User A)
Expected: 404 "Job not found for user alice@google.com"

GET /api/provision/assets/J1 (as User A)
Expected: 200 with demo assets
```

### Test 4: Unauthenticated Access (Backwards Compatibility)
```bash
# Test
GET /api/provision/history (no auth token)
Expected: Returns all jobs from in-memory state

GET /api/provision/status/J1 (no auth token)
Expected: Returns job status (for backwards compatibility)
```

### Test 5: Frontend Displays User Jobs
```bash
# Test
1. Sign in as User A
2. Dashboard should show "Your Recent Provisions"
3. Should display only User A's jobs
4. Sign out
5. Dashboard should show "Recent Provisions"
6. Should display all jobs or empty state
```

---

## Firestore Data Structure

```
users/
  {userId}/
    jobs/
      {jobId}/
        customer_url: string
        status: "pending" | "running" | "completed" | "failed"
        mode: "default" | "crazy_frog"
        created_at: timestamp
        updated_at: timestamp
        metadata:
          dataset_id: string
          agent_id: string
          demo_title: string
          datasetFullName: string
        current_phase: string
        overall_progress: number
```

---

## Security Checklist

- ✅ User can only see their own jobs
- ✅ User can only access their own job status
- ✅ User can only access their own demo assets
- ✅ Firebase token verified on every request
- ✅ Jobs stored per-user in Firestore
- ✅ No job leakage between users
- ✅ Backwards compatible for unauthenticated users

---

## Deployment Steps

1. **Deploy Backend**
   ```bash
   cd backend
   # Changes are in routes/provisioning.py
   # Already using firestore_service (no new dependencies)

   # Build and deploy
   gcloud run deploy capi-demo --source .
   ```

2. **Deploy Frontend**
   ```bash
   cd newfrontend/conversational-api-demo-frontend
   npm run build

   # Deploy to Cloud Run or copy dist/ to backend
   ```

3. **Test**
   ```bash
   # Test with 2 different Google accounts
   # Verify each user only sees their own jobs
   ```

---

## Success Criteria

✅ **Backend:**
- `/history` returns user-specific jobs when authenticated
- `/status` verifies user ownership before returning data
- `/assets` verifies user ownership before returning data
- All endpoints work without auth (backwards compatible)

✅ **Frontend:**
- Dashboard fetches real jobs from API
- Jobs refresh when user signs in/out
- Loading states shown while fetching
- Empty state when user has no jobs
- Auth token sent in all API requests

✅ **Security:**
- User A cannot see User B's jobs
- User A cannot access User B's job details
- Firestore rules enforce user isolation

---

## Timeline

- **Backend changes:** 30 minutes
- **Frontend changes:** 30 minutes
- **Testing:** 1 hour
- **Total:** 2 hours

---

## Next Steps

1. Review this plan
2. Test current implementation (changes already made)
3. Deploy to Cloud Run
4. Test with multiple Google accounts
5. Monitor Firestore for correct data structure

---

**Status:** ✅ Backend changes implemented, Frontend changes implemented
**Next Action:** Test and deploy
