#!/bin/bash
# ========================================
# LOCAL DEVELOPMENT SERVER
# ========================================
# Starts the FastAPI backend locally with hot reload
# Usage: ./local_server.sh

set -e  # Exit on error

echo "🚀 Starting Local Development Server..."
echo "========================================"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Load local environment
if [ -f local.env ]; then
    set -a
    source local.env
    set +a
    echo "✅ Loaded local.env"
else
    echo "❌ ERROR: local.env not found"
    echo "   Run this script from the backend/ directory"
    exit 1
fi

# Set Google Cloud credentials path (only if file exists)
# On Cloud Shell, use default compute engine credentials instead
if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"
    echo "✅ Using ADC credentials from file"
else
    echo "✅ Using default credentials (Cloud Shell/GCE metadata service)"
fi

# Check gcloud authentication
echo ""
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q "@"; then
    echo "❌ Not authenticated with gcloud"
    echo ""
    echo "Please run:"
    echo "  gcloud auth application-default login"
    echo "  gcloud config set project $PROJECT_ID"
    echo ""
    exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)
echo "✅ Authenticated as: $ACTIVE_ACCOUNT"

# Verify project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "⚠️  Warning: Current project is $CURRENT_PROJECT, expected $PROJECT_ID"
    echo "   Setting project..."
    gcloud config set project $PROJECT_ID
fi

# Show configuration
echo ""
echo "📋 Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Location: $LOCATION"
echo "  Environment: $ENVIRONMENT"
echo "  Gemini API Key: ${GEMINI_API_KEY:0:25}..."
echo "  Dataset: $DATASET_ID"
echo "  Debug: $DEBUG"
echo ""

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8000 is already in use"
    echo ""
    PID=$(lsof -Pi :8000 -sTCP:LISTEN -t)
    echo "   Process using port 8000: PID $PID"
    echo ""
    read -p "   Kill it and continue? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill -9 $PID
        echo "   ✅ Killed process $PID"
    else
        echo "   ❌ Exiting. Please free port 8000 manually."
        exit 1
    fi
fi

# Show helpful URLs
echo "🌐 Server will be available at:"
echo "  Main URL:       http://localhost:8000"
echo "  CE Dashboard:   http://localhost:8000/ce-dashboard"
echo "  API Docs:       http://localhost:8000/docs"
echo "  Health Check:   http://localhost:8000/health"
echo ""
echo "📝 Logs will appear below. Press Ctrl+C to stop."
echo "========================================"
echo ""

# Start uvicorn with hot reload
uvicorn api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level info \
  --access-log \
  --use-colors
