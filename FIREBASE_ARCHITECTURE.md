# 🔥 Firebase Architecture for User-Scoped Job Management

## Overview
This document explains how Firebase Authentication and Firestore work together to provide user-scoped job isolation.

---

## 🏗️ Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                             │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  User clicks "Sign In with Google"                             ││
│  └────────────────────┬───────────────────────────────────────────┘│
│                       ↓                                              │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  Firebase Auth SDK                                             ││
│  │  - signInWithPopup(googleProvider)                             ││
│  │  - User selects Google account                                 ││
│  │  - Firebase returns: { uid, email, token }                     ││
│  └────────────────────┬───────────────────────────────────────────┘│
│                       ↓                                              │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  AuthContext stores user:                                      ││
│  │  {                                                              ││
│  │    uid: "abc123xyz",                                           ││
│  │    email: "alice@google.com",                                  ││
│  │    getIdToken: () => "eyJhbGc..."  // JWT token                ││
│  │  }                                                              ││
│  └────────────────────┬───────────────────────────────────────────┘│
│                       ↓                                              │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  User creates a provisioning job                               ││
│  │                                                                 ││
│  │  fetch('/api/provision/start', {                               ││
│  │    headers: {                                                   ││
│  │      'Authorization': 'Bearer eyJhbGc...'  // ← JWT token      ││
│  │    },                                                           ││
│  │    body: { customer_url: 'https://nike.com' }                  ││
│  │  })                                                             ││
│  └────────────────────┬───────────────────────────────────────────┘│
└────────────────────────┼────────────────────────────────────────────┘
                         │
                         ↓ HTTP Request with JWT token
                         │
┌────────────────────────┼────────────────────────────────────────────┐
│                        ↓        BACKEND (FastAPI)                    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  middleware/auth.py                                            ││
│  │  ─────────────────────────────────────────────────────────────││
│  │  async def optional_google_user(authorization: str = Header())││
│  │                                                                 ││
│  │    1. Extract token from "Bearer eyJhbGc..."                   ││
│  │    2. Verify with Firebase Admin SDK:                          ││
│  │       decoded = auth.verify_id_token(token)                    ││
│  │    3. Check email domain: must be @google.com                  ││
│  │    4. Return: { uid: "abc123", email: "alice@google.com" }    ││
│  └────────────────────┬───────────────────────────────────────────┘│
│                       ↓                                              │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  routes/provisioning.py                                        ││
│  │  ─────────────────────────────────────────────────────────────││
│  │  @router.post("/start")                                        ││
│  │  async def start_provision(                                    ││
│  │      request: StartRequest,                                    ││
│  │      user: dict = Depends(optional_google_user)  # ← from auth││
│  │  ):                                                             ││
│  │      user_id = user['uid']  # "abc123xyz"                      ││
│  │      job_id = uuid.uuid4()                                     ││
│  │                                                                 ││
│  │      # Save to Firestore                                       ││
│  │      await firestore_service.save_job(                         ││
│  │          user_id=user_id,    # ← User's UID                    ││
│  │          job_id=job_id,                                        ││
│  │          job_data={                                            ││
│  │              customer_url: "https://nike.com",                 ││
│  │              status: "running",                                ││
│  │              mode: "default"                                   ││
│  │          }                                                      ││
│  │      )                                                          ││
│  └────────────────────┬───────────────────────────────────────────┘│
└────────────────────────┼────────────────────────────────────────────┘
                         │
                         ↓ Save to Firestore
                         │
┌────────────────────────┼────────────────────────────────────────────┐
│                        ↓      FIRESTORE (Database)                   │
│                                                                       │
│  Collection: users/                                                  │
│  ├─ abc123xyz/  ← User A (alice@google.com)                         │
│  │  └─ jobs/                                                         │
│  │     ├─ job-001/                                                   │
│  │     │  ├─ customer_url: "https://nike.com"                       │
│  │     │  ├─ status: "running"                                      │
│  │     │  ├─ mode: "default"                                        │
│  │     │  ├─ created_at: 2025-10-07T10:00:00                       │
│  │     │  └─ metadata: { dataset_id, agent_id, ... }               │
│  │     │                                                             │
│  │     └─ job-002/                                                   │
│  │        ├─ customer_url: "https://adidas.com"                     │
│  │        ├─ status: "completed"                                    │
│  │        └─ ...                                                     │
│  │                                                                   │
│  └─ xyz789def/  ← User B (bob@google.com)                           │
│     └─ jobs/                                                         │
│        └─ job-003/                                                   │
│           ├─ customer_url: "https://puma.com"                       │
│           ├─ status: "running"                                      │
│           └─ ...                                                     │
│                                                                       │
│  🔒 FIRESTORE SECURITY RULES:                                        │
│  ───────────────────────────────────────────────────────────────   │
│  match /users/{userId}/jobs/{jobId} {                                │
│    allow read, write: if request.auth.uid == userId;                │
│  }                                                                   │
│  ───────────────────────────────────────────────────────────────   │
│  ↑ This ensures User A cannot access User B's jobs                  │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🔐 How Firebase Authentication Works

### Step 1: User Signs In (Frontend)

```typescript
// newfrontend/.../AuthContext.tsx

const signInWithGoogle = async () => {
  const provider = new GoogleAuthProvider();

  // Opens Google sign-in popup
  const result = await signInWithPopup(auth, provider);

  // Firebase returns user object:
  // {
  //   uid: "abc123xyz",              // Unique user ID
  //   email: "alice@google.com",
  //   displayName: "Alice",
  //   photoURL: "https://...",
  //   getIdToken: () => "eyJhbGc..."  // JWT token
  // }

  return result.user;
};
```

**What happens:**
1. User clicks "Sign In with Google"
2. Firebase Auth SDK opens Google OAuth popup
3. User selects Google account
4. Firebase generates a JWT token
5. Frontend stores user object in AuthContext

---

### Step 2: Frontend Sends JWT Token (Frontend → Backend)

```typescript
// newfrontend/.../CEDashboard.tsx

const handleDefaultProvision = async () => {
  // Get Firebase JWT token
  const token = await user.getIdToken();

  // Send to backend
  await fetch('/api/provision/start', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,  // ← JWT token here
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ customer_url: 'https://nike.com' })
  });
};
```

**JWT Token Example:**
```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJhYmMxMjMiLCJlbWFpbCI6ImFsaWNlQGdvb2dsZS5jb20iLCJpc3MiOiJmaXJlYmFzZS5nb29nbGUuY29tIiwiaWF0IjoxNjk2NzAwMDAwfQ.signature
```

Decoded:
```json
{
  "uid": "abc123xyz",
  "email": "alice@google.com",
  "iss": "firebase.google.com",
  "iat": 1696700000,
  "exp": 1696703600
}
```

---

### Step 3: Backend Verifies JWT Token (Backend)

```python
# backend/middleware/auth.py

async def optional_google_user(authorization: str = Header(None)):
    """Verify Firebase JWT token."""

    if not authorization:
        return None  # No auth provided

    # Extract token from "Bearer eyJhbGc..."
    scheme, token = authorization.split()

    # Verify token with Firebase Admin SDK
    decoded_token = auth.verify_id_token(token)
    # ↑ This calls Firebase servers to verify the token is:
    #   - Valid signature
    #   - Not expired
    #   - Issued by Firebase

    uid = decoded_token['uid']          # "abc123xyz"
    email = decoded_token.get('email')  # "alice@google.com"

    # Enforce @google.com domain
    if not email.endswith('@google.com'):
        raise HTTPException(403, "Access restricted to @google.com")

    return {
        'uid': uid,
        'email': email
    }
```

**What happens:**
1. Backend extracts JWT token from Authorization header
2. Firebase Admin SDK verifies token signature
3. Firebase Admin SDK checks expiration
4. Backend checks email domain (@google.com)
5. Returns user info to endpoint

---

### Step 4: Backend Saves to User's Firestore Collection

```python
# backend/routes/provisioning.py

@router.post("/start")
async def start_provision(
    request: StartRequest,
    user: Optional[dict] = Depends(optional_google_user)  # ← From Step 3
):
    user_id = user['uid']  # "abc123xyz"
    job_id = str(uuid.uuid4())

    # Save to Firestore under this user's collection
    await firestore_service.save_job(
        user_id=user_id,  # ← User's UID determines path
        job_id=job_id,
        job_data={
            'customer_url': 'https://nike.com',
            'status': 'running',
            'mode': 'default',
            'created_at': datetime.utcnow()
        }
    )

    # Firestore path will be: users/abc123xyz/jobs/{job_id}
```

---

### Step 5: Firestore Service Saves Data

```python
# backend/services/firestore_service.py

async def save_job(self, user_id: str, job_id: str, job_data: dict):
    """Save job to Firestore under user's collection."""

    # Path: users/{user_id}/jobs/{job_id}
    doc_ref = self.db.collection('users') \
                     .document(user_id) \      # ← User's UID
                     .collection('jobs') \
                     .document(job_id)

    # Save data
    doc_ref.set({
        **job_data,
        'updated_at': firestore.SERVER_TIMESTAMP
    }, merge=True)

    # Result: Saved to users/abc123xyz/jobs/job-001
```

---

## 📊 Firestore Data Structure

```
Firestore Database
├─ users/
│  ├─ abc123xyz/  ← User A (alice@google.com)
│  │  └─ jobs/
│  │     ├─ f3d8e72a-1234-5678-90ab-cdef12345678/
│  │     │  ├─ customer_url: "https://nike.com"
│  │     │  ├─ status: "completed"
│  │     │  ├─ mode: "default"
│  │     │  ├─ created_at: Timestamp(2025-10-07 10:00:00)
│  │     │  ├─ updated_at: Timestamp(2025-10-07 10:08:30)
│  │     │  ├─ current_phase: "Demo Validator"
│  │     │  ├─ overall_progress: 100
│  │     │  └─ metadata:
│  │     │     ├─ dataset_id: "nike_demo_20251007"
│  │     │     ├─ datasetFullName: "bq-demos-469816.nike_demo_20251007"
│  │     │     ├─ agentId: "projects/.../agents/12345"
│  │     │     └─ demo_title: "Nike E-commerce Analytics"
│  │     │
│  │     └─ a7b9c3d4-5678-90ab-cdef-123456789abc/
│  │        ├─ customer_url: "https://adidas.com"
│  │        ├─ status: "running"
│  │        ├─ current_phase: "Data Modeling Agent"
│  │        └─ overall_progress: 45
│  │
│  └─ xyz789def/  ← User B (bob@google.com)
│     └─ jobs/
│        └─ e5f6g7h8-9012-3456-7890-abcdef123456/
│           ├─ customer_url: "https://puma.com"
│           ├─ status: "failed"
│           └─ metadata:
│              └─ error: "SSL cert error"
```

---

## 🔒 Firestore Security Rules

```javascript
// firestore.rules

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Users can only access their own jobs
    match /users/{userId}/jobs/{jobId} {
      // Allow read/write only if authenticated user's UID matches userId
      allow read, write: if request.auth != null
                         && request.auth.uid == userId;
    }

    // Example:
    // - User A (uid: abc123) can read/write: users/abc123/jobs/*
    // - User A CANNOT read/write: users/xyz789/jobs/*
    // - Unauthenticated users CANNOT read/write anything
  }
}
```

**How it works:**
1. Every Firestore request includes the user's JWT token
2. Firestore extracts `request.auth.uid` from the token
3. Rule checks if `request.auth.uid == userId` (path parameter)
4. If match → Allow access
5. If no match → Deny access (404 error)

---

## 🔄 Complete User Flow Example

### Scenario: Alice creates a job, Bob tries to access it

```
1. Alice signs in
   └─> Frontend: user = { uid: "abc123", email: "alice@google.com" }

2. Alice creates job
   POST /api/provision/start
   Headers: Authorization: Bearer <alice_token>

   └─> Backend verifies alice_token → user_id = "abc123"
   └─> Firestore saves to: users/abc123/jobs/job-001

3. Alice views her jobs
   GET /api/provision/history
   Headers: Authorization: Bearer <alice_token>

   └─> Backend queries: users/abc123/jobs/*
   └─> Returns: [job-001]

4. Bob signs in
   └─> Frontend: user = { uid: "xyz789", email: "bob@google.com" }

5. Bob tries to view Alice's job
   GET /api/provision/status/job-001
   Headers: Authorization: Bearer <bob_token>

   └─> Backend verifies bob_token → user_id = "xyz789"
   └─> Backend queries: users/xyz789/jobs/job-001
   └─> Firestore: Document not found (doesn't exist in Bob's collection)
   └─> Backend returns: 404 "Job not found for bob@google.com"

6. Bob creates his own job
   POST /api/provision/start
   Headers: Authorization: Bearer <bob_token>

   └─> Backend verifies bob_token → user_id = "xyz789"
   └─> Firestore saves to: users/xyz789/jobs/job-002

7. Bob views his jobs
   GET /api/provision/history
   Headers: Authorization: Bearer <bob_token>

   └─> Backend queries: users/xyz789/jobs/*
   └─> Returns: [job-002]  ← Only Bob's job, NOT Alice's
```

---

## 🛡️ Security Features

### 1. Token Verification
```python
# Every request verifies JWT token
decoded = auth.verify_id_token(token)
# Firebase checks:
# - Valid signature (cryptographically signed by Firebase)
# - Not expired (exp claim)
# - Issued by Firebase (iss claim)
```

### 2. Email Domain Restriction
```python
if not email.endswith('@google.com'):
    raise HTTPException(403, "Access restricted to @google.com")
```

### 3. Per-User Data Isolation
```python
# User A queries: users/abc123/jobs/*
# User B queries: users/xyz789/jobs/*
# No cross-contamination possible
```

### 4. Firestore Security Rules
```javascript
// Even if backend had a bug, Firestore rules would still block:
allow read, write: if request.auth.uid == userId;
```

---

## 📝 Implementation Checklist

### Backend Setup

- [x] **1. Firebase Admin SDK initialized**
  - File: `backend/middleware/auth.py`
  - Uses Application Default Credentials (ADC) on Cloud Run
  - Uses service account key locally

- [x] **2. Auth middleware created**
  - Function: `optional_google_user()`
  - Verifies JWT token
  - Enforces @google.com domain
  - Returns user info

- [x] **3. Firestore service created**
  - File: `backend/services/firestore_service.py`
  - Functions: `save_job()`, `get_user_jobs()`, `get_job()`
  - Saves to: `users/{userId}/jobs/{jobId}`

- [x] **4. Endpoints updated**
  - `/api/provision/start` - Saves to user's Firestore
  - `/api/provision/history` - Returns only user's jobs
  - `/api/provision/status/{job_id}` - Verifies ownership
  - `/api/provision/assets/{job_id}` - Verifies ownership

### Frontend Setup

- [x] **1. Firebase Auth SDK initialized**
  - File: `newfrontend/.../firebase.ts`
  - Configured with Firebase project

- [x] **2. AuthContext created**
  - Manages user state
  - Provides `signInWithGoogle()`, `signOut()`
  - Stores user object

- [x] **3. Dashboard updated**
  - Fetches user jobs from `/api/provision/history`
  - Sends JWT token in all requests
  - Shows user-specific messaging

### Firestore Setup

- [ ] **1. Create Firestore database**
  ```bash
  gcloud firestore databases create --region=us-central1
  ```

- [ ] **2. Deploy security rules**
  ```bash
  firebase deploy --only firestore:rules
  ```

- [ ] **3. Create indexes** (if needed)
  - Index on `created_at` for sorting
  - Auto-created when queries run

---

## 🧪 Testing Commands

```bash
# 1. Sign in as User A
# (Use browser)

# 2. Get User A's token
TOKEN_A="eyJhbGc..."  # Copy from browser DevTools → Application → IndexedDB

# 3. Create job as User A
curl -X POST http://localhost:8000/api/provision/start \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://nike.com"}'

# 4. Get User A's jobs
curl http://localhost:8000/api/provision/history \
  -H "Authorization: Bearer $TOKEN_A"

# 5. Sign in as User B
# (Use browser incognito mode)

# 6. Get User B's token
TOKEN_B="eyJhbGc..."

# 7. Try to access User A's job (should fail)
curl http://localhost:8000/api/provision/status/USER_A_JOB_ID \
  -H "Authorization: Bearer $TOKEN_B"
# Expected: 404 "Job not found for user B"

# 8. Get User B's jobs (should be empty or only User B's jobs)
curl http://localhost:8000/api/provision/history \
  -H "Authorization: Bearer $TOKEN_B"
```

---

## 🚀 Deployment

### 1. Enable Firestore
```bash
gcloud firestore databases create --region=us-central1
```

### 2. Deploy Security Rules
```bash
# Create firestore.rules
cat > firestore.rules <<EOF
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/jobs/{jobId} {
      allow read, write: if request.auth != null
                         && request.auth.uid == userId;
    }
  }
}
EOF

# Deploy
firebase deploy --only firestore:rules
```

### 3. Deploy Backend
```bash
cd backend
gcloud run deploy capi-demo --source . --region=us-central1
```

### 4. Test
```bash
# Sign in with 2 different @google.com accounts
# Verify each user only sees their own jobs
```

---

## 📊 Benefits of This Architecture

✅ **Security**
- JWT tokens cryptographically verified
- User data isolated in separate Firestore collections
- Firestore security rules as second layer of defense
- No user can access another user's data

✅ **Scalability**
- Firestore scales automatically
- No need to manage database servers
- Supports millions of users

✅ **Simplicity**
- No custom user database needed
- Firebase handles auth, tokens, sessions
- Firestore handles data storage, queries

✅ **Reliability**
- Data persists across server restarts
- Jobs survive backend crashes
- User can close browser and come back later

✅ **Backwards Compatible**
- Unauthenticated users still work
- In-memory jobs still work for testing
- Gradual migration possible

---

## 🎯 Summary

**Firebase Authentication:**
- Handles Google OAuth sign-in
- Issues JWT tokens
- Verifies tokens on every request

**Firestore:**
- Stores jobs per user: `users/{userId}/jobs/`
- Enforces access control via security rules
- Persists data permanently

**Backend:**
- Verifies JWT tokens
- Queries Firestore by user ID
- Returns only user's own data

**Frontend:**
- Signs in with Google
- Sends JWT token in every request
- Displays user-specific jobs

**Result:**
- ✅ Each user sees only their own jobs
- ✅ No user can access another user's data
- ✅ Data persists forever
- ✅ Secure and scalable

---

**Next Step:** Deploy and test with 2 different @google.com accounts!
