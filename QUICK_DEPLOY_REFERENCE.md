# 🚀 Quick CloudRun Deploy Reference

**Use this card for fast deployment**

---

## ✅ Pre-Deployment Checklist

```bash
# 1. Run the pre-deployment checks
bash scripts/pre-deploy-check.sh

# Look for this output:
# ✅ Using correct SyntheticDataGeneratorMarkdown (4 occurrences)
# ✅ PASSED with 2 warning(s)
```

---

## 🚀 Deploy Command

```bash
# Automated deployment (RECOMMENDED)
./deploy-to-cloudrun.sh
```

**Or manual:**
```bash
gcloud run deploy demo-gen-capi-prod \
  --source . \
  --project bq-demos-469816 \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars "FORCE_LLM_DATA_GENERATION=true,PROJECT_ID=bq-demos-469816,LOCATION=us-central1"
```

---

## ✅ Post-Deployment Verification

### 1. Check logs for safeguard message:
```bash
gcloud run services logs read demo-gen-capi-prod --region us-central1 --limit 20
```

**Look for:**
```
✅ Using correct data generator: SyntheticDataGeneratorMarkdown
🔒 FORCE_LLM_DATA_GENERATION=true - Faker fallback is DISABLED
```

### 2. Test provisioning:
```bash
SERVICE_URL=$(gcloud run services describe demo-gen-capi-prod \
  --region us-central1 --format='value(status.url)')

curl -X POST $SERVICE_URL/api/provision/start \
  -H 'Content-Type: application/json' \
  -d '{"customer_url": "https://www.nike.com"}'
```

### 3. Verify data quality:
After provisioning completes, check BigQuery:
```bash
bq head -n 3 nike_capi_demo_YYYYMMDD.products
```

**GOOD (LLM data):** "Nike Air Max 270", "Jordan 1 Retro High"  
**BAD (Faker data):** "new", "it", "option"

---

## 🛡️ Safeguards in Place

1. ✅ **Pre-deployment script** checks code before deploy
2. ✅ **Runtime safeguard** crashes app if wrong generator imported
3. ✅ **Environment variable** `FORCE_LLM_DATA_GENERATION=true` enforces LLM-only
4. ✅ **Deprecated code** moved to `_deleted_do_not_use/` folder

---

## 🚨 If Something Goes Wrong

### Error: "Using SyntheticDataGeneratorOptimized"
**Fix:** Re-run deployment script, it will detect and block this

### Error: Bad data in BigQuery (random words)
**Fix:** Delete dataset and re-provision:
```bash
bq rm -r -f -d bq-demos-469816:DATASET_NAME
# Then re-provision via UI
```

---

## 📚 Full Documentation

- **Safeguards Guide:** `CLOUDRUN_DATA_GENERATOR_SAFEGUARDS.md`
- **Root Cause Analysis:** `DATA_CORRUPTION_ROOT_CAUSE_ANALYSIS.md`
- **Deployment Guide:** `CLOUDRUN_DEPLOYMENT_GUIDE.md`
- **Recommendations:** `CLOUDRUN_RECOMMENDATIONS_ACTIONABLE.md`

---

**Quick Answer: "Will CloudRun use the correct version?"**

✅ **YES** - 4 layers of protection ensure it:
1. Pre-deployment check script blocks bad code
2. Runtime safeguard crashes app if wrong generator detected
3. Environment variable forces LLM-only mode
4. Automated deployment script sets everything correctly

**Just use:** `./deploy-to-cloudrun.sh` and you're protected!
