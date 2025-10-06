#!/bin/bash

# Setup script for environment configuration

echo "🔧 Setting up environment for Agentic CAPI Demo"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Prompt for Gemini API key
echo ""
echo "📝 Please enter your Gemini API key:"
echo "(Get it from: https://makersuite.google.com/app/apikey)"
read -p "Gemini API Key: " gemini_key

if [ -z "$gemini_key" ]; then
    echo "❌ Error: Gemini API key cannot be empty"
    exit 1
fi

# Create .env file
cat > .env << EOF
# Gemini API Key
GEMINI_API_KEY=${gemini_key}

# Google Cloud Project
PROJECT_ID=bq-demos-469816
LOCATION=us-central1

# Environment
ENVIRONMENT=development
EOF

echo ""
echo "✅ .env file created successfully!"
echo ""
echo "Next steps:"
echo "1. Enable Claude in Vertex AI Model Garden:"
echo "   https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-3-5-sonnet-v2"
echo ""
echo "2. Test the Research Agent:"
echo "   python test_research_agent.py"
echo ""
