# 🔥 Firebase Authentication & Firestore Setup Guide

This guide will help you set up Firebase for the CAPI Demo Generation tool.

## ✅ Current Status
- ✅ Branch created: `firebase-auth-persistence`
- ✅ Feature flag infrastructure added (`ENABLE_AUTH`)
- ✅ Backend config created (`backend/config.py`)
- ⏳ Pending: Firebase Console setup

---

## 📋 Phase 1: Firebase Console Setup

### Step 1: Add Firebase to GCP Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add Project"
3. Select **existing GCP project**: `bq-demos-469816`
4. Accept Firebase terms
5. **Enable Google Analytics**: NO (not needed for this)

### Step 2: Enable Authentication

1. In Firebase Console → **Authentication**
2. Click "Get Started"
3. Select **Sign-in method** tab
4. Enable **Google** provider
   - Click "Google"
   - Toggle "Enable"
   - Select project support email (your @google.com email)
   - **Domain restriction**: We'll handle this in code (`@google.com` only)
   - Click "Save"

5. Add **Authorized domains**:
   - Go to Authentication → Settings → Authorized domains
   - Add: `demo-generation-549403515075.us-east5.run.app`
   - Add: `localhost` (for local testing)

### Step 3: Enable Firestore Database

1. In Firebase Console → **Firestore Database**
2. Click "Create database"
3. **Location**: `us-central1` (same as CloudRun backend)
4. **Security rules**: Start in **production mode** (we'll add custom rules)

### Step 4: Set Firestore Security Rules

1. In Firestore → **Rules** tab
2. Replace default rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper function: Check if user is a Googler
    function isGoogler() {
      return request.auth != null && 
             request.auth.token.email.matches('.*@google[.]com$');
    }
    
    // Users collection: Each user can only access their own data
    match /users/{userId} {
      // Only allow if authenticated AND user is a Googler AND accessing own data
      allow read, write: if isGoogler() && request.auth.uid == userId;
      
      // User profile
      match /profile {
        allow read, write: if isGoogler() && request.auth.uid == userId;
      }
      
      // User's jobs (each user can only see their own jobs)
      match /jobs/{jobId} {
        allow read, write: if isGoogler() && request.auth.uid == userId;
      }
    }
    
    // Deny all other access
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

3. Click **Publish**

### Step 5: Get Firebase Config (Frontend)

1. In Firebase Console → **Project Settings** (gear icon)
2. Scroll to "Your apps"
3. Click **Web** icon (`</>`)
4. Register app:
   - App nickname: `CAPI Demo Frontend`
   - **DO NOT** check "Firebase Hosting"
   - Click "Register app"

5. **Copy the Firebase config object** (looks like this):

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "bq-demos-469816.firebaseapp.com",
  projectId: "bq-demos-469816",
  storageBucket: "bq-demos-469816.appspot.com",
  messagingSenderId: "...",
  appId: "1:...:web:..."
};
```

### Step 6: Download Service Account Key (Backend)

1. In Firebase Console → **Project Settings** → **Service Accounts**
2. Click "Generate new private key"
3. **Save the JSON file** as `firebase-service-account.json`
4. **DO NOT commit this file to git!**

For CloudRun:
- Upload this file as a Secret in Google Secret Manager
- OR: Add it as a base64-encoded env variable

---

## 📂 Phase 2: Create Configuration Files

### Frontend: `newfrontend/conversational-api-demo-frontend/src/lib/firebase.ts`

Create this file with your Firebase config from Step 5:

```typescript
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Firebase configuration from Firebase Console
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize services
export const auth = getAuth(app);
export const firestore = getFirestore(app);

// Google Auth Provider with domain hint
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  hd: 'google.com', // Hint that only google.com accounts should be shown
});

export default app;
```

### Frontend: `newfrontend/conversational-api-demo-frontend/.env`

```bash
# Firebase Configuration
VITE_FIREBASE_API_KEY=AIzaSy...  # From Firebase Console
VITE_FIREBASE_AUTH_DOMAIN=bq-demos-469816.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=bq-demos-469816
VITE_FIREBASE_STORAGE_BUCKET=bq-demos-469816.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=...  # From Firebase Console
VITE_FIREBASE_APP_ID=1:...:web:...  # From Firebase Console

# Feature Flag
VITE_ENABLE_AUTH=false  # Set to true when ready to test auth
```

### Frontend: `newfrontend/conversational-api-demo-frontend/.env.production`

```bash
# Firebase Configuration (same as .env)
VITE_FIREBASE_API_KEY=AIzaSy...
VITE_FIREBASE_AUTH_DOMAIN=bq-demos-469816.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=bq-demos-469816
VITE_FIREBASE_STORAGE_BUCKET=bq-demos-469816.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=1:...:web:...

# Feature Flag (enable for production)
VITE_ENABLE_AUTH=true
```

### Backend: `.env` (local testing)

```bash
# Copy from .env.example and fill in:
ENABLE_AUTH=false  # Start with false for testing
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/firebase-service-account.json
```

---

## 🧪 Phase 3: Local Testing

### Test Mode 1: Without Auth (Backward Compatible)

```bash
# Terminal 1: Backend
cd backend
ENABLE_AUTH=false uvicorn api:app --reload --port 8000

# Terminal 2: Frontend
cd newfrontend/conversational-api-demo-frontend
VITE_ENABLE_AUTH=false npm run dev

# Access: http://localhost:5173
# Should work exactly like before (no login required)
```

### Test Mode 2: With Auth

```bash
# Terminal 1: Backend
cd backend
ENABLE_AUTH=true \
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/firebase-service-account.json \
uvicorn api:app --reload --port 8000

# Terminal 2: Frontend  
cd newfrontend/conversational-api-demo-frontend
VITE_ENABLE_AUTH=true npm run dev

# Access: http://localhost:5173
# Should redirect to /login
# Click "Sign in with Google"
# Only @google.com accounts should work
```

---

## 🚀 Phase 4: CloudRun Deployment

### Option A: Using Secret Manager (Recommended)

```bash
# 1. Upload service account to Secret Manager
gcloud secrets create firebase-service-account \
  --data-file=/path/to/firebase-service-account.json \
  --project=bq-demos-469816

# 2. Grant CloudRun access
gcloud secrets add-iam-policy-binding firebase-service-account \
  --member=serviceAccount:CLOUDRUN_SERVICE_ACCOUNT@bq-demos-469816.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# 3. Deploy with secret
gcloud run deploy demo-generation \
  --source . \
  --region us-east5 \
  --set-env-vars "ENABLE_AUTH=true" \
  --set-secrets "/tmp/firebase-service-account.json=firebase-service-account:latest"
```

### Option B: Base64 Encoded (Simpler)

```bash
# 1. Base64 encode the JSON
cat firebase-service-account.json | base64 > firebase-base64.txt

# 2. Deploy with base64 content in env var
gcloud run deploy demo-generation \
  --source . \
  --region us-east5 \
  --set-env-vars "ENABLE_AUTH=true,FIREBASE_SERVICE_ACCOUNT_BASE64=$(cat firebase-base64.txt)"

# 3. Decode in backend/config.py
import os
import base64
import json

if 'FIREBASE_SERVICE_ACCOUNT_BASE64' in os.environ:
    service_account_json = base64.b64decode(os.environ['FIREBASE_SERVICE_ACCOUNT_BASE64'])
    with open('/tmp/firebase-service-account.json', 'w') as f:
        f.write(service_account_json.decode('utf-8'))
```

---

## 📊 Firestore Data Structure

Once auth is enabled, jobs will be stored like this:

```
users/
  qwertyuiop123 (Firebase UID)/
    profile/
      email: "john@google.com"
      displayName: "John Doe"
      photoURL: "https://..."
      createdAt: 2025-10-06T...
    
    jobs/
      job-uuid-1/
        jobId: "abc-123"
        customerUrl: "https://www.nike.com"
        status: "completed"
        demoTitle: "Nike E-commerce Analytics"
        datasetId: "demo_nike_20251006"
        createdAt: 2025-10-06T...
      
      job-uuid-2/
        ...
```

---

## 🔍 Troubleshooting

### Issue: "Firebase: Error (auth/popup-blocked)"
**Solution**: Allow popups in browser for localhost or CloudRun domain

### Issue: "Firestore: Missing or insufficient permissions"
**Solution**: Check Firestore security rules - make sure `isGoogler()` function is correct

### Issue: "Backend: Could not load service account"
**Solution**: Check `FIREBASE_SERVICE_ACCOUNT_PATH` points to valid JSON file

### Issue: "Only see my jobs, not other users"
**Solution**: This is correct! Multi-tenancy working as designed ✅

---

## ✅ Checklist

Before enabling auth in production:

- [ ] Firebase project added to bq-demos-469816
- [ ] Google Sign-In enabled in Firebase Auth
- [ ] Authorized domains added (CloudRun URL + localhost)
- [ ] Firestore database created in us-central1
- [ ] Firestore security rules deployed
- [ ] Frontend Firebase config added to .env
- [ ] Backend service account JSON downloaded
- [ ] Tested locally with ENABLE_AUTH=false (backward compatible)
- [ ] Tested locally with ENABLE_AUTH=true (@google.com restriction works)
- [ ] Service account uploaded to CloudRun (secret or env var)
- [ ] Deployed to CloudRun with ENABLE_AUTH=true

---

## 📚 Next Steps

Once Firebase is set up, the implementation continues with:

1. ✅ Install dependencies (`firebase`, `firebase-admin`)
2. ✅ Create auth middleware (backend)
3. ✅ Create Firestore service layer (backend)
4. ✅ Create AuthContext (frontend)
5. ✅ Create Login page (frontend)
6. ✅ Create Job History page (frontend)
7. ✅ Add Protected Routes (frontend)

See the todo list for current progress!
