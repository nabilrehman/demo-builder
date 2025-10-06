#!/bin/bash
# CloudRun Deployment Script with Pre-Flight Checks
# Ensures correct data generator is deployed

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${PROJECT_ID:-"bq-demos-469816"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"demo-gen-capi-prod"}

echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  CloudRun Deployment - CAPI Demo Generator${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo ""

# =============================================================================
# STEP 1: Pre-deployment checks
# =============================================================================
echo -e "${YELLOW}Step 1/4: Running pre-deployment checks...${NC}"
echo ""

if [ -f "scripts/pre-deploy-check.sh" ]; then
    bash scripts/pre-deploy-check.sh

    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}❌ Pre-deployment checks FAILED${NC}"
        echo "Fix errors above before deploying"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Warning: pre-deploy-check.sh not found, skipping checks${NC}"
fi

echo ""

# =============================================================================
# STEP 2: Confirm deployment details
# =============================================================================
echo -e "${YELLOW}Step 2/4: Confirm deployment details${NC}"
echo ""
echo "  Project ID:    $PROJECT_ID"
echo "  Region:        $REGION"
echo "  Service Name:  $SERVICE_NAME"
echo ""

read -p "Proceed with deployment? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""

# =============================================================================
# STEP 3: Build and deploy to CloudRun
# =============================================================================
echo -e "${YELLOW}Step 3/4: Deploying to Cloud Run...${NC}"
echo ""

gcloud run deploy $SERVICE_NAME \
  --source . \
  --project $PROJECT_ID \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 1 \
  --set-env-vars "\
PROJECT_ID=$PROJECT_ID,\
LOCATION=$REGION,\
ENVIRONMENT=production,\
FORCE_LLM_DATA_GENERATION=true,\
RESEARCH_AGENT_MODEL=gemini,\
DEMO_STORY_AGENT_MODEL=gemini,\
DATA_MODELING_AGENT_MODEL=claude,\
CAPI_AGENT_MODEL=claude,\
DEMO_NUM_QUERIES=6,\
DEMO_NUM_SCENES=4,\
V2_MAX_PAGES=30,\
V2_MAX_DEPTH=2"

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}❌ Deployment FAILED${NC}"
    exit 1
fi

echo ""

# =============================================================================
# STEP 4: Get service URL and verify deployment
# =============================================================================
echo -e "${YELLOW}Step 4/4: Verifying deployment...${NC}"
echo ""

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --project $PROJECT_ID \
  --region $REGION \
  --format='value(status.url)')

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Service URL:${NC} $SERVICE_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test health endpoint
echo "Testing health endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}⚠️  Health check returned HTTP $HTTP_CODE${NC}"
    echo "Service may still be starting up. Check logs:"
    echo "  gcloud run services logs read $SERVICE_NAME --region $REGION --limit 50"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Open the frontend:"
echo "   $SERVICE_URL"
echo ""
echo "2. Test the API:"
echo "   curl -X POST $SERVICE_URL/api/provision/start \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"customer_url\": \"https://www.nike.com\"}'"
echo ""
echo "3. View logs:"
echo "   gcloud run services logs read $SERVICE_NAME \\"
echo "     --region $REGION --limit 50"
echo ""
echo "4. View service details:"
echo "   gcloud run services describe $SERVICE_NAME \\"
echo "     --region $REGION"
echo ""
echo -e "${GREEN}Deployment complete! 🎉${NC}"
echo ""
