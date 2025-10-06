#!/bin/bash
set -e

echo "🔍 Pre-deployment CloudRun checks..."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# =============================================================================
# CRITICAL CHECK 1: Verify correct data generator in orchestrator
# =============================================================================
echo "✓ Checking data generator selection..."

if grep -q "SyntheticDataGeneratorOptimized" backend/agentic_service/demo_orchestrator.py | grep -v "^#" | grep -v "_deleted_do_not_use"; then
    echo -e "${RED}❌ CRITICAL ERROR: Using broken SyntheticDataGeneratorOptimized!${NC}"
    echo "   File: backend/agentic_service/demo_orchestrator.py"
    echo "   Issue: This version has keyword filtering and falls back to Faker"
    echo ""
    echo "   Fix: Change all imports to:"
    echo "   from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown"
    echo ""
    ERRORS=$((ERRORS + 1))
else
    # Verify markdown version IS being used
    MARKDOWN_COUNT=$(grep -c "SyntheticDataGeneratorMarkdown" backend/agentic_service/demo_orchestrator.py || echo "0")
    if [ "$MARKDOWN_COUNT" -ge 2 ]; then
        echo -e "${GREEN}   ✅ Using correct SyntheticDataGeneratorMarkdown ($MARKDOWN_COUNT occurrences)${NC}"
    else
        echo -e "${RED}❌ ERROR: SyntheticDataGeneratorMarkdown not found in orchestrator${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# =============================================================================
# CRITICAL CHECK 2: Verify dependencies are complete
# =============================================================================
echo ""
echo "✓ Checking dependencies..."

if ! grep -q "langgraph>=0.0.50" backend/requirements.txt; then
    echo -e "${RED}❌ CRITICAL ERROR: Missing langgraph dependency${NC}"
    echo "   Add to backend/requirements.txt: langgraph>=0.0.50"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}   ✅ langgraph found${NC}"
fi

if ! grep -q "google-cloud-aiplatform" backend/requirements.txt; then
    echo -e "${RED}❌ CRITICAL ERROR: Missing google-cloud-aiplatform dependency${NC}"
    echo "   Add to backend/requirements.txt: google-cloud-aiplatform>=1.38.0"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}   ✅ google-cloud-aiplatform found${NC}"
fi

if ! grep -q "anthropic" backend/requirements.txt; then
    echo -e "${RED}❌ CRITICAL ERROR: Missing anthropic dependency${NC}"
    echo "   Add to backend/requirements.txt: anthropic[vertex]>=0.40.0"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}   ✅ anthropic found${NC}"
fi

# =============================================================================
# CHECK 3: Verify logging configuration
# =============================================================================
echo ""
echo "✓ Checking logging configuration..."

if grep -q "filename='backend.log'" backend/api.py; then
    echo -e "${YELLOW}⚠️  WARNING: Logging to file instead of stdout${NC}"
    echo "   File: backend/api.py"
    echo "   Issue: Cloud Run captures stdout/stderr, not file writes"
    echo "   Recommendation: Change to logging.basicConfig(stream=sys.stdout)"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}   ✅ Not logging to file${NC}"
fi

# =============================================================================
# CHECK 4: Verify CORS configuration
# =============================================================================
echo ""
echo "✓ Checking CORS configuration..."

if grep -q 'allow_origins=\["\*"\]' backend/api.py; then
    echo -e "${YELLOW}⚠️  WARNING: CORS allows all origins${NC}"
    echo "   File: backend/api.py"
    echo "   Recommendation: Restrict origins for production"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}   ✅ CORS not wide open${NC}"
fi

# =============================================================================
# CHECK 5: Verify Dockerfile port configuration
# =============================================================================
echo ""
echo "✓ Checking Dockerfile port configuration..."

if grep -q 'PORT:-8080' Dockerfile; then
    echo -e "${GREEN}   ✅ Dockerfile uses PORT env var correctly${NC}"
else
    echo -e "${RED}❌ ERROR: Dockerfile doesn't use PORT env var${NC}"
    echo "   Cloud Run requires: --port \${PORT:-8080}"
    ERRORS=$((ERRORS + 1))
fi

# =============================================================================
# CHECK 6: Verify .dockerignore exists
# =============================================================================
echo ""
echo "✓ Checking .dockerignore..."

if [ -f ".dockerignore" ]; then
    echo -e "${GREEN}   ✅ .dockerignore exists${NC}"

    # Check for common exclusions
    if grep -q "backend.log" .dockerignore; then
        echo -e "${GREEN}   ✅ Excludes log files${NC}"
    else
        echo -e "${YELLOW}⚠️  WARNING: .dockerignore should exclude backend.log${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  WARNING: No .dockerignore file${NC}"
    echo "   Recommendation: Create .dockerignore to reduce image size"
    WARNINGS=$((WARNINGS + 1))
fi

# =============================================================================
# CHECK 7: Verify deleted folder is properly marked
# =============================================================================
echo ""
echo "✓ Checking deprecated code isolation..."

if [ -d "backend/agentic_service/agents/_deleted_do_not_use" ]; then
    echo -e "${GREEN}   ✅ Deleted folder exists for deprecated code${NC}"

    if [ -f "backend/agentic_service/agents/_deleted_do_not_use/README.md" ]; then
        echo -e "${GREEN}   ✅ README.md warning exists${NC}"
    else
        echo -e "${YELLOW}⚠️  WARNING: No README.md in deleted folder${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${GREEN}   ✅ No deprecated code folder (clean)${NC}"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=================================================="
echo "Pre-deployment Check Summary"
echo "=================================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "Safe to deploy to Cloud Run:"
    echo "  gcloud run deploy demo-gen-capi-prod \\"
    echo "    --source . \\"
    echo "    --region us-central1 \\"
    echo "    --allow-unauthenticated"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}✅ PASSED with $WARNINGS warning(s)${NC}"
    echo ""
    echo "Safe to deploy, but review warnings above."
    echo ""
    exit 0
else
    echo -e "${RED}❌ FAILED with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "DO NOT DEPLOY until errors are fixed!"
    echo ""
    exit 1
fi
