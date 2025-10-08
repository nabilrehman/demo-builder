# 🚀 Deployment Test Plan - User-Scoped Job Management

## 📍 Deployed App
**URL:** https://demo-gen-capi-prod-549403515075.us-central1.run.app/ce-dashboard
**Project:** bq-demos-469816
**Service:** demo-gen-capi-prod
**Region:** us-central1

---

## ✅ Pre-Test Verification

### 1. Check Service is Running
```bash
# Service URL
gcloud run services describe demo-gen-capi-prod \
  --region=us-central1 \
  --format="value(status.url)"

# Should return: https://demo-gen-capi-prod-549403515075.us-central1.run.app
```

### 2. Verify Environment Variables
```bash
# Check ENABLE_AUTH is set
gcloud run services describe demo-gen-capi-prod \
  --region=us-central1 \
  --format="table(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)" \
  | grep ENABLE_AUTH

# Expected: ENABLE_AUTH | true
```

### 3. Test API Endpoint
```bash
# Without auth (should return empty jobs or all in-memory jobs)
curl https://demo-gen-capi-prod-549403515075.us-central1.run.app/api/provision/history

# Expected: {"jobs":[],"total":0}
```

---

## 🧪 Test Plan - User Isolation

### Test 1: User A Creates Jobs ✅

**Steps:**
1. Open app: https://demo-gen-capi-prod-549403515075.us-central1.run.app/ce-dashboard
2. Click "Sign In with Google"
3. Sign in with **your primary @google.com account** (e.g., yourname@google.com)
4. Verify you see:
   - ✅ User email displayed in header
   - ✅ "Sign Out" button visible
   - ✅ "Your Recent Provisions" header

5. Create a job:
   - Enter customer URL: `https://nike.com`
   - Click "Start Provision"
   - Wait for job to start

6. Verify:
   - ✅ Job appears in "Your Recent Provisions" table
   - ✅ Job shows "running" status
   - ✅ You can click on it to view progress

**Expected Result:**
- Job is visible in your dashboard
- Job is stored in Firestore: `users/{your-uid}/jobs/{job-id}`

---

### Test 2: User B Cannot See User A's Jobs ✅

**Steps:**
1. Open **NEW INCOGNITO WINDOW**
2. Navigate to: https://demo-gen-capi-prod-549403515075.us-central1.run.app/ce-dashboard
3. Click "Sign In with Google"
4. Sign in with **DIFFERENT @google.com account** (e.g., colleague@google.com)
5. Go to dashboard

**Verify:**
- ✅ Dashboard shows "Your Recent Provisions" (0 items)
- ✅ You DO NOT see User A's Nike job
- ✅ Empty state message: "No provisions yet. Start by provisioning a chatbot above."

**Expected Result:**
- User B sees empty dashboard
- User A's jobs are NOT visible

---

### Test 3: User B Creates Their Own Job ✅

**Steps (continue in incognito window as User B):**
1. Enter customer URL: `https://adidas.com`
2. Click "Start Provision"
3. Wait for job to start

**Verify:**
- ✅ User B's Adidas job appears in their dashboard
- ✅ User A's Nike job is still NOT visible
- ✅ Only 1 job shown (User B's Adidas job)

---

### Test 4: User A Still Sees Only Their Jobs ✅

**Steps (go back to original window as User A):**
1. Refresh the dashboard
2. Check "Your Recent Provisions"

**Verify:**
- ✅ User A sees their Nike job
- ✅ User A does NOT see User B's Adidas job
- ✅ Only User A's jobs are visible

---

### Test 5: Direct URL Access Protection ✅

**Steps:**
1. As User A, click on your Nike job
2. Copy the job ID from the URL (e.g., `/provision-progress?jobId=abc-123`)
3. Switch to incognito window (signed in as User B)
4. Paste the URL: `https://demo-gen-capi-prod-549403515075.us-central1.run.app/provision-progress?jobId=abc-123`
5. Press Enter

**Expected Result:**
- ✅ Error: "Job not found" or 404
- ✅ User B CANNOT view User A's job details

---

### Test 6: API Authorization ✅

**Steps:**

**As User A:**
1. Open Browser DevTools (F12)
2. Go to: Application → IndexedDB → firebaseLocalStorage
3. Find and copy the Firebase Auth token (starts with `eyJhbGc...`)

**As User B (incognito):**
1. Open Browser DevTools
2. Copy User B's Firebase token

**Test API with User A's token:**
```bash
# Replace with User A's actual token
TOKEN_A="eyJhbGc..."

curl -H "Authorization: Bearer $TOKEN_A" \
  https://demo-gen-capi-prod-549403515075.us-central1.run.app/api/provision/history

# Should return ONLY User A's jobs
```

**Test API with User B's token:**
```bash
# Replace with User B's actual token
TOKEN_B="eyJhbGc..."

curl -H "Authorization: Bearer $TOKEN_B" \
  https://demo-gen-capi-prod-549403515075.us-central1.run.app/api/provision/history

# Should return ONLY User B's jobs (different from User A's)
```

**Expected:**
- ✅ Different tokens return different jobs
- ✅ No overlap between User A and User B's jobs

---

### Test 7: Firestore Data Verification ✅

**Steps:**
```bash
# Check Firestore has user data
gcloud firestore collections list --database="(default)" --project=bq-demos-469816

# Expected output: users

# List all users with jobs
gcloud firestore documents list users --database="(default)" --project=bq-demos-469816

# Should show multiple user IDs (different UIDs for User A and User B)
```

**Verify in Firebase Console:**
1. Go to: https://console.firebase.google.com/project/bq-demos-469816/firestore
2. Navigate to `users` collection
3. Verify structure:
   ```
   users/
     {user-a-uid}/
       jobs/
         {nike-job-id}/
           customer_url: "https://nike.com"
           status: "running"
     {user-b-uid}/
       jobs/
         {adidas-job-id}/
           customer_url: "https://adidas.com"
           status: "running"
   ```

---

### Test 8: Job Persistence ✅

**Steps:**
1. As User A, create a job
2. Close browser completely
3. Wait 5 minutes
4. Open browser again
5. Navigate to: https://demo-gen-capi-prod-549403515075.us-central1.run.app/ce-dashboard
6. Sign in as User A

**Verify:**
- ✅ All previously created jobs are still visible
- ✅ Jobs did NOT disappear (persisted in Firestore)

---

## 🔍 Debugging Checklist

### If jobs don't show up:

**1. Check browser console:**
```javascript
// Open DevTools → Console
// Look for:
✅ "Firebase initialized successfully"
✅ "User signed in: yourname@google.com"
✅ "Fetching jobs..."
❌ Any errors?
```

**2. Check Network tab:**
```
DevTools → Network → Filter: "history"
Request: GET /api/provision/history
Headers:
  Authorization: Bearer eyJhbGc...  ← Should be present
Response:
  Status: 200
  Body: {"jobs": [...], "total": N}
```

**3. Check backend logs:**
```bash
gcloud run services logs read demo-gen-capi-prod \
  --region=us-central1 \
  --limit=50 \
  --project=bq-demos-469816

# Look for:
✅ "Authenticated request from yourname@google.com"
✅ "Retrieved N jobs for user {uid}"
❌ Any errors?
```

### If User B can see User A's jobs (SECURITY ISSUE):

**Check backend code:**
```bash
# Verify the history endpoint filters by user
cat backend/routes/provisioning.py | grep -A 20 "def get_provision_history"

# Should see:
# user_id = user['uid']
# firestore_jobs = await firestore_service.get_user_jobs(user_id, limit)
```

**Check Firestore queries:**
```bash
# Enable Firestore debug logs
gcloud run services update demo-gen-capi-prod \
  --set-env-vars "LOG_LEVEL=DEBUG" \
  --region=us-central1

# Check logs for Firestore queries
gcloud run services logs read demo-gen-capi-prod --region=us-central1 --limit=100 | grep -i firestore
```

---

## 📊 Success Criteria

All tests must pass:

- ✅ User A can sign in and create jobs
- ✅ User B can sign in and create jobs
- ✅ User A sees ONLY their jobs
- ✅ User B sees ONLY their jobs
- ✅ User B CANNOT access User A's job via direct URL
- ✅ API returns different jobs for different auth tokens
- ✅ Firestore has separate collections per user
- ✅ Jobs persist after browser close/reopen

---

## 🎯 Quick Test (5 minutes)

**Fastest way to verify:**

1. **Window 1:** Sign in as yourname@google.com → Create Nike job
2. **Incognito Window:** Sign in as colleague@google.com → Create Adidas job
3. **Verify:**
   - Window 1 shows only Nike job
   - Incognito shows only Adidas job
4. **Pass:** Users are isolated ✅
5. **Fail:** Both users see both jobs ❌

---

## 🚨 If Tests Fail

### Backend not using Firestore:
```bash
# Check ENABLE_AUTH is set
gcloud run services describe demo-gen-capi-prod \
  --region=us-central1 \
  --format=json | grep -i enable_auth

# If not set, update:
gcloud run services update demo-gen-capi-prod \
  --set-env-vars ENABLE_AUTH=true \
  --region=us-central1
```

### Frontend not sending auth token:
```bash
# Check .env has VITE_ENABLE_AUTH=true
cat newfrontend/conversational-api-demo-frontend/.env.local

# If missing, add and rebuild:
echo "VITE_ENABLE_AUTH=true" >> newfrontend/conversational-api-demo-frontend/.env.local
cd newfrontend/conversational-api-demo-frontend
npm run build

# Redeploy
```

---

## 📞 Support

If tests fail, provide:
1. Browser console logs
2. Network tab screenshot
3. Backend logs (gcloud command above)
4. Which test failed

---

**Next:** Run the tests above with 2 different Google accounts!

**Time needed:** 10 minutes
**Prerequisites:** 2 @google.com accounts
