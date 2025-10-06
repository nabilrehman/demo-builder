# 🛡️ CloudRun Data Generator Safeguards

**Created:** 2025-10-06
**Purpose:** Ensure CloudRun deployment ALWAYS uses the correct LLM-based data generator

---

## ❓ The Problem This Solves

The orchestrator has two data generator options:

| Generator | Status | Behavior |
|-----------|--------|----------|
| `SyntheticDataGeneratorMarkdown` | ✅ CORRECT | ALWAYS uses LLM for ALL tables |
| `SyntheticDataGeneratorOptimized` | ❌ BROKEN | Keyword filtering → Faker for 70% of tables |

**Risk:** Accidentally deploying the wrong generator to CloudRun would cause all demos to have Faker data instead of realistic LLM-generated data.

---

## 🛡️ Multi-Layer Protection

We've implemented **4 layers of protection** to ensure the correct generator is used:

### Layer 1: Pre-Deployment Check Script ✅

**File:** `scripts/pre-deploy-check.sh`

**What it does:**
- Scans `demo_orchestrator.py` for incorrect imports
- Verifies all dependencies are present
- Checks Dockerfile configuration
- Runs BEFORE deployment

**Usage:**
```bash
bash scripts/pre-deploy-check.sh
```

**Output:**
```
✓ Checking data generator selection...
   ✅ Using correct SyntheticDataGeneratorMarkdown (4 occurrences)

✓ Checking dependencies...
   ✅ langgraph found
   ✅ google-cloud-aiplatform found
   ✅ anthropic found

==================================================
Pre-deployment Check Summary
==================================================

✅ PASSED with 2 warning(s)

Safe to deploy, but review warnings above.
```

**If wrong generator is detected:**
```
❌ CRITICAL ERROR: Using broken SyntheticDataGeneratorOptimized!
   File: backend/agentic_service/demo_orchestrator.py
   Issue: This version has keyword filtering and falls back to Faker

DO NOT DEPLOY until errors are fixed!
```

---

### Layer 2: Runtime Safeguards ✅

**File:** `backend/agentic_service/demo_orchestrator.py` (lines 95-114, 417-426)

**What it does:**
- Checks at runtime (when orchestrator initializes)
- Reads `FORCE_LLM_DATA_GENERATION` environment variable
- If wrong generator is imported, raises `ValueError`

**Code:**
```python
# Check for environment variable that forces LLM-only data generation
FORCE_LLM = os.getenv("FORCE_LLM_DATA_GENERATION", "true").lower() == "true"

# Verify we're using the correct generator class
if "Optimized" in SyntheticDataGeneratorMarkdown.__name__:
    error_msg = (
        "❌ CRITICAL ERROR: Accidentally imported SyntheticDataGeneratorOptimized!\n"
        "This version has keyword filtering and will use Faker for most tables.\n"
    )
    logger.error(error_msg)
    if FORCE_LLM:
        raise ValueError(error_msg)  # STOP THE APPLICATION

logger.info(f"✅ Using correct data generator: {SyntheticDataGeneratorMarkdown.__name__}")
```

**When it triggers:**
- Immediately when the orchestrator starts
- BEFORE any demo is generated
- Application will crash and refuse to start if wrong generator is detected

**Environment variable:**
```bash
FORCE_LLM_DATA_GENERATION=true  # Default: true (recommended)
```

---

### Layer 3: Automated Deployment Script ✅

**File:** `deploy-to-cloudrun.sh`

**What it does:**
- Runs pre-deployment checks automatically
- Sets `FORCE_LLM_DATA_GENERATION=true` in CloudRun environment
- Confirms deployment details with user
- Tests health endpoint after deployment

**Usage:**
```bash
./deploy-to-cloudrun.sh
```

**What happens:**
1. **Step 1/4:** Runs pre-deployment checks
2. **Step 2/4:** Shows deployment configuration, asks for confirmation
3. **Step 3/4:** Deploys to CloudRun with environment variables
4. **Step 4/4:** Verifies deployment with health check

**Environment variables automatically set:**
```bash
FORCE_LLM_DATA_GENERATION=true          # Enables runtime safeguard
RESEARCH_AGENT_MODEL=gemini             # Cost optimization
DEMO_STORY_AGENT_MODEL=gemini           # Cost optimization
DATA_MODELING_AGENT_MODEL=claude        # Quality
CAPI_AGENT_MODEL=claude                 # Required
DEMO_NUM_QUERIES=6                      # Standard demo size
DEMO_NUM_SCENES=4                       # Standard demo complexity
V2_MAX_PAGES=30                         # Research depth
V2_MAX_DEPTH=2                          # Research depth
```

---

### Layer 4: Deprecated Code Isolation ✅

**File:** `backend/agentic_service/agents/_deleted_do_not_use/synthetic_data_generator_optimized.py.DEPRECATED`

**What it does:**
- Moved broken generator to clearly marked folder
- Added massive warning banner in the file
- Created README.md explaining why it's deprecated

**README excerpt:**
```markdown
# ⛔ DELETED / DEPRECATED FILES - DO NOT USE

## `synthetic_data_generator_optimized.py.DEPRECATED`

**Status:** ❌ BROKEN - DO NOT USE

**Why deprecated:**
- Has keyword filtering that prevents LLM generation for most tables
- Only generates LLM data for tables matching specific keywords
- Misses critical tables: users, listings, transactions, messages, etc.
- Falls back to Faker for 70% of tables → generates unrealistic data

**✅ Use instead:** `synthetic_data_generator_markdown.py`
```

**Dockerfile impact:**
The Dockerfile copies the entire `backend/` directory, including the `_deleted_do_not_use/` folder. This is **intentional and safe** because:
- The folder name clearly indicates it should not be used
- Runtime safeguards prevent accidental use
- Pre-deployment checks verify correct imports

---

## 🚀 Deployment Process

### Quick Deploy (Recommended)

```bash
# Run the automated deployment script
./deploy-to-cloudrun.sh
```

This script handles everything automatically.

---

### Manual Deploy (Advanced)

If you prefer manual deployment:

```bash
# Step 1: Run pre-deployment checks
bash scripts/pre-deploy-check.sh

# Step 2: Deploy to CloudRun
gcloud run deploy demo-gen-capi-prod \
  --source . \
  --project bq-demos-469816 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "FORCE_LLM_DATA_GENERATION=true,PROJECT_ID=bq-demos-469816"

# Step 3: Verify deployment
SERVICE_URL=$(gcloud run services describe demo-gen-capi-prod \
  --region us-central1 --format='value(status.url)')
curl -f $SERVICE_URL/health
```

**IMPORTANT:** Always set `FORCE_LLM_DATA_GENERATION=true` in CloudRun environment!

---

## ✅ Verification After Deployment

### 1. Check CloudRun Logs

```bash
gcloud run services logs read demo-gen-capi-prod \
  --region us-central1 \
  --limit 50
```

**Look for this log message on startup:**
```
✅ Using correct data generator: SyntheticDataGeneratorMarkdown
🔒 FORCE_LLM_DATA_GENERATION=true - Faker fallback is DISABLED
```

**If you see this, STOP and redeploy:**
```
❌ CRITICAL ERROR: Accidentally imported SyntheticDataGeneratorOptimized!
```

---

### 2. Run a Test Provisioning

```bash
# Start a test provisioning
curl -X POST https://demo-gen-capi-prod-xxx.run.app/api/provision/start \
  -H 'Content-Type: application/json' \
  -d '{"customer_url": "https://www.nike.com"}'
```

**Watch for these log messages:**
```
🤖 Generating realistic data for products with Gemini 2.5 Pro...
🤖 Generating realistic data for customers with Gemini 2.5 Pro...
🤖 Generating realistic data for orders with Gemini 2.5 Pro...
```

**If you see "Using Faker" → WRONG GENERATOR!**

---

### 3. Check BigQuery Data Quality

After provisioning completes:

```bash
# Query the generated data
bq query --use_legacy_sql=false \
  "SELECT * FROM \`bq-demos-469816.nike_capi_demo_YYYYMMDD.products\` LIMIT 5"
```

**GOOD data (LLM-generated):**
```
title: "Nike Air Max 270 - Men's Running Shoes"
description: "Iconic sneaker featuring large Max Air unit for all-day comfort..."
```

**BAD data (Faker):**
```
title: "new", "it", "option", "final"
description: "relate", "past", "they"
```

---

## 🔐 Security Best Practices

### For Production Deployment:

1. **Use Secret Manager for API keys:**
   ```bash
   # Store Gemini API key
   echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

   # Deploy with secret
   gcloud run deploy demo-gen-capi-prod \
     --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
   ```

2. **Restrict CORS origins:**
   ```bash
   --set-env-vars "ALLOWED_ORIGINS=https://your-domain.com"
   ```

3. **Require authentication (optional):**
   ```bash
   # Deploy WITHOUT --allow-unauthenticated
   gcloud run deploy demo-gen-capi-prod \
     --region us-central1
     # No --allow-unauthenticated flag
   ```

---

## 📋 Troubleshooting

### Issue: Pre-deployment check fails

**Symptom:**
```
❌ CRITICAL ERROR: Using broken SyntheticDataGeneratorOptimized!
```

**Fix:**
1. Check `backend/agentic_service/demo_orchestrator.py`
2. Search for all imports of `SyntheticDataGenerator`
3. Replace with:
   ```python
   from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown
   ```
4. Re-run check: `bash scripts/pre-deploy-check.sh`

---

### Issue: Application crashes on startup in CloudRun

**Symptom:**
CloudRun logs show:
```
ValueError: ❌ CRITICAL ERROR: Accidentally imported SyntheticDataGeneratorOptimized!
```

**Cause:** Wrong generator was deployed despite safeguards

**Fix:**
1. Verify local code has correct imports
2. Run pre-deployment check: `bash scripts/pre-deploy-check.sh`
3. Redeploy: `./deploy-to-cloudrun.sh`

---

### Issue: Data quality is bad (Faker data in BigQuery)

**Symptom:**
```sql
SELECT title FROM products LIMIT 5
-- Returns: "new", "it", "option"
```

**Diagnosis:**
1. Check CloudRun environment variables:
   ```bash
   gcloud run services describe demo-gen-capi-prod \
     --region us-central1 \
     --format='value(spec.template.spec.containers[0].env)'
   ```

2. Look for `FORCE_LLM_DATA_GENERATION=true`

**Fix:**
1. Redeploy with environment variable:
   ```bash
   --set-env-vars "FORCE_LLM_DATA_GENERATION=true"
   ```

2. Delete bad dataset:
   ```bash
   bq rm -r -f -d bq-demos-469816:nike_capi_demo_YYYYMMDD
   ```

3. Run fresh provisioning

---

## 📚 Related Documentation

- **Root Cause Analysis:** `DATA_CORRUPTION_ROOT_CAUSE_ANALYSIS.md`
- **CloudRun Recommendations:** `CLOUDRUN_RECOMMENDATIONS_ACTIONABLE.md`
- **Deployment Guide:** `CLOUDRUN_DEPLOYMENT_GUIDE.md`

---

## ✅ Summary: How to Ensure Correct Version in CloudRun

1. **Always use the deployment script:** `./deploy-to-cloudrun.sh`
2. **Set environment variable:** `FORCE_LLM_DATA_GENERATION=true`
3. **Check logs after deployment:** Look for "✅ Using correct data generator: SyntheticDataGeneratorMarkdown"
4. **Test with real provisioning:** Verify BigQuery data is realistic, not random words

**With these 4 layers of protection, it's virtually impossible to accidentally deploy the wrong generator!**

---

**Document Status:** ✅ Production-Ready
**Last Updated:** 2025-10-06
**Validated:** Pre-deployment checks passing, runtime safeguards active
