#!/bin/bash

###############################################################################
# Local Docker Build Test Script
###############################################################################
#
# This script tests the Docker build locally before deploying to Cloud Run.
# It builds the Docker image and optionally runs it to verify everything works.
#
# Usage:
#   ./test-docker-build.sh [--run]
#
# Options:
#   --run    Build and run the container locally on port 8080
#
# Examples:
#   ./test-docker-build.sh           # Just build the image
#   ./test-docker-build.sh --run     # Build and run the container
#
###############################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

IMAGE_NAME="demo-gen-capi-backend"
TAG="local-test"
PORT=8080

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Docker Build Test - Demo Generation CAPI Backend${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if Docker is running
echo -e "${BLUE}→ Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Build the Docker image
echo ""
echo -e "${BLUE}→ Building Docker image...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes (installing dependencies and building frontend)${NC}"
echo ""

docker build -t ${IMAGE_NAME}:${TAG} .

echo ""
echo -e "${GREEN}✓ Docker image built successfully!${NC}"
echo ""

# Show image details
echo -e "${BLUE}Image Details:${NC}"
docker images ${IMAGE_NAME}:${TAG} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

# If --run flag is provided, run the container
if [[ "$1" == "--run" ]]; then
    echo -e "${BLUE}→ Running container on port ${PORT}...${NC}"
    echo ""

    # Stop any existing container with the same name
    if docker ps -a --format '{{.Names}}' | grep -q "^${IMAGE_NAME}-test$"; then
        echo -e "${YELLOW}Stopping existing container...${NC}"
        docker stop ${IMAGE_NAME}-test 2>/dev/null || true
        docker rm ${IMAGE_NAME}-test 2>/dev/null || true
    fi

    # Run the container
    docker run -d \
      --name ${IMAGE_NAME}-test \
      -p ${PORT}:8000 \
      -e PROJECT_ID=bq-demos-469816 \
      -e LOCATION=us-central1 \
      -e ENVIRONMENT=local-test \
      -e RESEARCH_AGENT_MODEL=gemini \
      -e DEMO_STORY_AGENT_MODEL=gemini \
      -e DATA_MODELING_AGENT_MODEL=claude \
      -e CAPI_AGENT_MODEL=claude \
      ${IMAGE_NAME}:${TAG}

    echo ""
    echo -e "${GREEN}✓ Container started!${NC}"
    echo ""

    # Wait for the service to be ready
    echo -e "${BLUE}→ Waiting for service to be ready...${NC}"
    sleep 5

    # Test health endpoint
    echo -e "${BLUE}→ Testing health endpoint...${NC}"
    if curl -s http://localhost:${PORT}/health | grep -q "healthy"; then
        echo -e "${GREEN}✓ Service is healthy!${NC}"
    else
        echo -e "${RED}✗ Service health check failed${NC}"
        echo "Showing container logs:"
        docker logs ${IMAGE_NAME}-test
        exit 1
    fi

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Container Running Successfully! 🎉${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Access Points:${NC}"
    echo "• Dashboard:      http://localhost:${PORT}"
    echo "• Health Check:   http://localhost:${PORT}/health"
    echo "• API Docs:       http://localhost:${PORT}/docs"
    echo ""
    echo -e "${YELLOW}Management Commands:${NC}"
    echo "• View logs:      docker logs -f ${IMAGE_NAME}-test"
    echo "• Stop container: docker stop ${IMAGE_NAME}-test"
    echo "• Remove:         docker rm ${IMAGE_NAME}-test"
    echo ""
    echo -e "${YELLOW}Test Provisioning:${NC}"
    echo "curl -X POST http://localhost:${PORT}/api/provision/start \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"customer_url\": \"https://www.nike.com\"}'"
    echo ""
else
    echo -e "${YELLOW}Build Complete!${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Run the container:  ./test-docker-build.sh --run"
    echo "2. Deploy to Cloud Run: ./deploy-to-cloudrun.sh"
    echo ""
fi
