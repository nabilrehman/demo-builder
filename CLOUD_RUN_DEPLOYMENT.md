# Cloud Run Deployment Guide

Complete guide for deploying the Demo Generation CAPI backend to Google Cloud Run with agent model configuration.

## Prerequisites

- Google Cloud Project: `bq-demos-469816`
- Cloud Run API enabled
- Authenticated with `gcloud`
- Container Registry or Artifact Registry configured

## Quick Deploy

### Option 1: Deploy with gcloud (Recommended)

```bash
# Deploy with default configuration (Gemini for speed agents, Claude for quality agents)
gcloud run deploy demo-gen-capi-backend \
  --source ./backend \
  --region us-central1 \
  --project bq-demos-469816 \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=bq-demos-469816" \
  --set-env-vars "LOCATION=us-central1" \
  --set-env-vars "RESEARCH_AGENT_MODEL=gemini" \
  --set-env-vars "DEMO_STORY_AGENT_MODEL=gemini" \
  --set-env-vars "DATA_MODELING_AGENT_MODEL=claude" \
  --set-env-vars "CAPI_AGENT_MODEL=claude" \
  --set-env-vars "DEMO_NUM_QUERIES=6" \
  --set-env-vars "DEMO_NUM_SCENES=4" \
  --set-env-vars "DEMO_NUM_ENTITIES=8" \
  --set-env-vars "V2_MAX_PAGES=30" \
  --set-env-vars "V2_MAX_DEPTH=2" \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10
```

### Option 2: Deploy with YAML

Create `service.yaml`:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: demo-gen-capi-backend
  namespace: 'bq-demos-469816'
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: '10'
        autoscaling.knative.dev/minScale: '0'
    spec:
      containerConcurrency: 80
      timeoutSeconds: 3600
      serviceAccountName: PROJECT_NUMBER-compute@developer.gserviceaccount.com
      containers:
      - image: gcr.io/bq-demos-469816/demo-gen-capi-backend:latest
        resources:
          limits:
            cpu: '2'
            memory: 4Gi
        env:
        # ====================================================================
        # Agent Model Configuration (Gemini vs Claude)
        # ====================================================================
        - name: RESEARCH_AGENT_MODEL
          value: gemini          # 2x faster (131s vs 263s)
        - name: DEMO_STORY_AGENT_MODEL
          value: gemini          # 2.13x faster (43s vs 92s), same quality
        - name: DATA_MODELING_AGENT_MODEL
          value: claude          # User preference
        - name: CAPI_AGENT_MODEL
          value: claude          # Quality critical (Gemini incomplete)

        # ====================================================================
        # Google Cloud Configuration
        # ====================================================================
        - name: PROJECT_ID
          value: bq-demos-469816
        - name: LOCATION
          value: us-central1
        - name: ENVIRONMENT
          value: production

        # ====================================================================
        # Demo Complexity Configuration
        # ====================================================================
        - name: DEMO_NUM_QUERIES
          value: '6'
        - name: DEMO_NUM_SCENES
          value: '4'
        - name: DEMO_NUM_ENTITIES
          value: '8'

        # ====================================================================
        # Research Agent V2 Configuration
        # ====================================================================
        - name: V2_MAX_PAGES
          value: '30'
        - name: V2_MAX_DEPTH
          value: '2'
        - name: V2_ENABLE_BLOG
          value: 'false'
        - name: V2_ENABLE_LINKEDIN
          value: 'false'
        - name: V2_ENABLE_YOUTUBE
          value: 'false'
```

Deploy:
```bash
gcloud run services replace service.yaml --region us-central1
```

## Environment Configurations

### Configuration Profiles

#### Speed Mode (Development/Demos - ~3 minutes)

```bash
gcloud run services update demo-gen-capi-backend \
  --region us-central1 \
  --update-env-vars \
    "RESEARCH_AGENT_MODEL=gemini,\
DEMO_STORY_AGENT_MODEL=gemini,\
DATA_MODELING_AGENT_MODEL=gemini,\
CAPI_AGENT_MODEL=claude"
```

**Best for:**
- Rapid prototyping
- Development environment
- Quick customer demos
- Cost optimization

**Performance:**
- Research: 131s (Gemini)
- Demo Story: 43s (Gemini)
- Data Modeling: ~40s (Gemini - untested)
- CAPI: 84s (Claude - quality critical)
- **Total: ~3 minutes**

#### Quality Mode (Production - ~5 minutes)

```bash
gcloud run services update demo-gen-capi-backend \
  --region us-central1 \
  --update-env-vars \
    "RESEARCH_AGENT_MODEL=claude,\
DEMO_STORY_AGENT_MODEL=gemini,\
DATA_MODELING_AGENT_MODEL=claude,\
CAPI_AGENT_MODEL=claude"
```

**Best for:**
- Production deployments
- Customer-facing demos
- Comprehensive analysis required
- Quality > Speed

**Performance:**
- Research: 263s (Claude - more thorough)
- Demo Story: 43s (Gemini - same quality as Claude)
- Data Modeling: ~40s (Claude)
- CAPI: 84s (Claude)
- **Total: ~5 minutes**

#### Balanced Mode (Recommended Default - ~4 minutes)

```bash
gcloud run services update demo-gen-capi-backend \
  --region us-central1 \
  --update-env-vars \
    "RESEARCH_AGENT_MODEL=gemini,\
DEMO_STORY_AGENT_MODEL=gemini,\
DATA_MODELING_AGENT_MODEL=claude,\
CAPI_AGENT_MODEL=claude"
```

**Best for:**
- General purpose
- Most use cases
- Good balance of speed and quality

**Performance:**
- Research: 131s (Gemini)
- Demo Story: 43s (Gemini)
- Data Modeling: ~40s (Claude)
- CAPI: 84s (Claude)
- **Total: ~4 minutes**

## Hot-Swapping Models (No Rebuild Required!)

### Change a Single Agent Model

```bash
# Switch Research agent from Gemini to Claude
gcloud run services update demo-gen-capi-backend \
  --region us-central1 \
  --update-env-vars RESEARCH_AGENT_MODEL=claude

# Takes ~30 seconds (vs 5 minutes to rebuild container)
```

### Verify Current Configuration

```bash
# View all environment variables
gcloud run services describe demo-gen-capi-backend \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"

# Filter for agent models only
gcloud run services describe demo-gen-capi-backend \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | \
  grep AGENT_MODEL
```

## Multi-Environment Deployment

### Development Service

```bash
gcloud run deploy demo-gen-capi-dev \
  --source ./backend \
  --region us-central1 \
  --set-env-vars "RESEARCH_AGENT_MODEL=gemini" \
  --set-env-vars "DEMO_STORY_AGENT_MODEL=gemini" \
  --set-env-vars "DATA_MODELING_AGENT_MODEL=gemini" \
  --set-env-vars "CAPI_AGENT_MODEL=claude" \
  --memory 2Gi \
  --cpu 1
```

### Production Service

```bash
gcloud run deploy demo-gen-capi-prod \
  --source ./backend \
  --region us-central1 \
  --set-env-vars "RESEARCH_AGENT_MODEL=claude" \
  --set-env-vars "DEMO_STORY_AGENT_MODEL=gemini" \
  --set-env-vars "DATA_MODELING_AGENT_MODEL=claude" \
  --set-env-vars "CAPI_AGENT_MODEL=claude" \
  --memory 4Gi \
  --cpu 2
```

## A/B Testing with Traffic Splitting

```bash
# Deploy "gemini-research" revision
gcloud run deploy demo-gen-capi-backend \
  --image gcr.io/bq-demos-469816/demo-gen-capi-backend:latest \
  --region us-central1 \
  --set-env-vars "RESEARCH_AGENT_MODEL=gemini" \
  --tag gemini-research \
  --no-traffic

# Deploy "claude-research" revision
gcloud run deploy demo-gen-capi-backend \
  --image gcr.io/bq-demos-469816/demo-gen-capi-backend:latest \
  --region us-central1 \
  --set-env-vars "RESEARCH_AGENT_MODEL=claude" \
  --tag claude-research \
  --no-traffic

# Split traffic 50/50
gcloud run services update-traffic demo-gen-capi-backend \
  --region us-central1 \
  --to-tags gemini-research=50,claude-research=50
```

## Security Best Practices

### Use Secret Manager for API Keys

```bash
# Create secret for Gemini API key
echo -n "YOUR_GEMINI_API_KEY" | \
  gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy automatic

# Grant Cloud Run service account access
PROJECT_NUMBER=$(gcloud projects describe bq-demos-469816 --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secret
gcloud run deploy demo-gen-capi-backend \
  --source ./backend \
  --region us-central1 \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

## Monitoring and Debugging

### View Logs with Agent Selection Info

```bash
# View recent logs
gcloud run logs read demo-gen-capi-backend \
  --region us-central1 \
  --limit 100

# Filter for agent selection logs
gcloud run logs read demo-gen-capi-backend \
  --region us-central1 \
  --limit 50 | \
  grep "Selected.*agent"

# Expected output:
# ✅ RESEARCH Agent: CustomerResearchAgentV2GeminiPro (GEMINI) [source: env var]
# ✅ DEMO_STORY Agent: DemoStoryAgentGeminiPro (GEMINI) [source: env var]
# ✅ DATA_MODELING Agent: DataModelingAgent (CLAUDE) [source: env var]
# ✅ CAPI Agent: CAPIInstructionGeneratorOptimized (CLAUDE) [source: env var]
```

### Monitor Performance

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe demo-gen-capi-backend \
  --region us-central1 \
  --format='value(status.url)')

# Test provisioning endpoint
curl -X POST $SERVICE_URL/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.nike.com"}'

# Check status
curl -s $SERVICE_URL/api/provision/status/JOB_ID | jq .
```

## Resource Recommendations

### Minimal (Development)
```bash
--memory 2Gi
--cpu 1
--max-instances 3
```

### Standard (Production)
```bash
--memory 4Gi
--cpu 2
--max-instances 10
```

### High Performance
```bash
--memory 8Gi
--cpu 4
--max-instances 20
```

## Troubleshooting

### Issue: Agent not using correct model

**Solution:** Check environment variables
```bash
gcloud run services describe demo-gen-capi-backend \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### Issue: Import errors for agent classes

**Solution:** Verify all agent files are in container
```bash
# Check container logs
gcloud run logs read demo-gen-capi-backend \
  --region us-central1 \
  --limit 100 | grep "ImportError"
```

### Issue: Slow performance

**Solution:** Check which agents are using Claude vs Gemini
```bash
# View agent configuration via API
curl $SERVICE_URL/health | jq .
```

## Complete Deployment Checklist

- [ ] Set all 4 agent model environment variables
- [ ] Configure Gemini API key via Secret Manager
- [ ] Set service account permissions (Vertex AI, BigQuery)
- [ ] Configure memory (4Gi recommended)
- [ ] Set timeout (3600s for long-running jobs)
- [ ] Enable auto-scaling (max 10 instances)
- [ ] Test with sample customer URL
- [ ] Verify logs show correct agent selection
- [ ] Monitor first few demo generations
- [ ] Set up alerts for errors

## Reference

- **Benchmark Results:** `benchmarks/AGENT_SELECTOR_GUIDE.md`
- **Agent Config:** `backend/agentic_service/config/README.md`
- **Configuration Script:** `backend/scripts/show_agent_config.py`

## Support

For issues or questions:
1. Check logs: `gcloud run logs read demo-gen-capi-backend --region us-central1`
2. Verify config: `python3 scripts/show_agent_config.py --detailed`
3. Review benchmarks: `cat benchmarks/AGENT_SELECTOR_GUIDE.md`
