# ✅ Firebase Setup Complete (via gcloud)

All Firebase infrastructure has been configured through Google Cloud CLI!

## 🎉 What's Been Set Up

### 1. Firebase APIs Enabled ✅
- Firebase API
- Identity Toolkit (Firebase Authentication)
- Firestore
- Firebase Hosting

### 2. Firestore Database Created ✅
- **Location:** us-central1
- **Mode:** Firestore Native
- **Type:** Free Tier
- **Database ID:** (default)

### 3. Security Rules Created ✅
- File: `firestore.rules`
- **@google.com domain restriction** enforced
- **User isolation:** Each user can only access their own data
- **Structure:** `users/{userId}/jobs/{jobId}`

### 4. Service Account Configured ✅
- **Account:** `firebase-backend-sa@bq-demos-469816.iam.gserviceaccount.com`
- **Roles:**
  - `roles/firebase.admin` (Firebase Admin)
  - `roles/datastore.user` (Firestore User)

---

## 🔑 Authentication Approach

**We're using Application Default Credentials (ADC) - No JSON key needed!**

### Why ADC is Better:
- ✅ More secure (no key files to manage)
- ✅ Works automatically on CloudRun
- ✅ No risk of accidentally committing keys
- ✅ Follows Google Cloud best practices

### How It Works:

**Local Development:**
```bash
# Your Cloud Shell automatically has credentials
gcloud auth application-default login  # Already done
```

**CloudRun Deployment:**
```bash
# CloudRun uses its default service account automatically
# No configuration needed!
```

**Backend Code:**
```python
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK with Application Default Credentials
# This automatically uses the service account on CloudRun
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'bq-demos-469816',
})
```

---

## 📋 Frontend Configuration Needed

You still need to get the Firebase web config for the frontend. This can be done via:

### Option 1: Firebase Console (Quickest)
1. Go to https://console.firebase.google.com
2. Select project: `bq-demos-469816`
3. Click gear icon → Project Settings
4. Scroll to "Your apps" → Web app
5. If no web app exists:
   - Click `</>` icon to add web app
   - Name: `CAPI Demo Frontend`
   - Copy the config object

### Option 2: Use Existing Firebase Project
If the web app already exists, the config looks like:
```javascript
{
  apiKey: "AIzaSy...",
  authDomain: "bq-demos-469816.firebaseapp.com",
  projectId: "bq-demos-469816",
  storageBucket: "bq-demos-469816.appspot.com",
  messagingSenderId: "...",
  appId: "1:...:web:..."
}
```

---

## 🚀 Next Steps

### 1. Get Firebase Web Config (Manual Step)
- [ ] Go to Firebase Console
- [ ] Get web app config
- [ ] Add to frontend `.env` file

### 2. Install Dependencies
```bash
# Backend
pip install firebase-admin google-cloud-firestore

# Frontend
npm install firebase
```

### 3. Implement Auth Code
The code structure is ready in:
- `backend/config.py` (feature flag: `ENABLE_AUTH`)
- `backend/.env.example` (configuration template)
- `FIREBASE_SETUP_GUIDE.md` (comprehensive guide)

### 4. Test Locally
```bash
# Without auth (backward compatible)
ENABLE_AUTH=false uvicorn api:app --reload

# With auth
ENABLE_AUTH=true uvicorn api:app --reload
```

---

## 📊 Firebase Console Access

**Access Firebase Console:**
https://console.firebase.google.com/project/bq-demos-469816

**What you'll see:**
- ✅ Authentication (ready to enable Google Sign-In)
- ✅ Firestore Database (empty, ready for data)
- ✅ Settings (get web app config here)

---

## 🔐 Security Summary

### Firestore Rules:
```javascript
// Only @google.com users can access
// Each user sees only their own jobs
match /users/{userId} {
  allow read, write: if isGoogler() && request.auth.uid == userId;
  
  match /jobs/{jobId} {
    allow read, write: if isGoogler() && request.auth.uid == userId;
  }
}
```

### Backend Authentication:
- Uses Application Default Credentials (ADC)
- CloudRun automatically authenticated
- No JSON keys to manage

### Frontend Authentication:
- Firebase Web SDK with Google Sign-In
- Domain hint: `hd=google.com`
- Client-side validation + server-side enforcement

---

## ✅ What's Left

### Manual Steps (5 minutes):
1. **Enable Google Sign-In in Firebase Console**
   - Go to Authentication → Sign-in method
   - Enable "Google" provider
   
2. **Get Web App Config**
   - Project Settings → Your apps → Web
   - Copy config object

3. **Add Authorized Domains**
   - Authentication → Settings → Authorized domains
   - Add: `demo-generation-549403515075.us-east5.run.app`

### Code Implementation (already planned):
- Install Firebase dependencies
- Create auth middleware
- Create Firestore service layer
- Create frontend auth components
- Test with feature flags

---

**Status:** 🟢 Firebase infrastructure ready! Just need web app config to proceed with code implementation.
