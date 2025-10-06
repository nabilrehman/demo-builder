"""
Verify that the setup is complete and working.
"""
import os
import sys
from dotenv import load_dotenv

print("🔍 Verifying Agentic CAPI Demo Setup")
print("=" * 80)

# Load environment
load_dotenv()

# Check 1: Gemini API Key
print("\n1. Checking Gemini API Key...")
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key and len(gemini_key) > 20:
    print("   ✅ Gemini API key is set")
else:
    print("   ❌ Gemini API key is missing or invalid")
    print("   Run: ./setup_env.sh")
    sys.exit(1)

# Check 2: Google Cloud Project
print("\n2. Checking Google Cloud Project...")
project_id = os.getenv("PROJECT_ID", "bq-demos-469816")
print(f"   ✅ Project ID: {project_id}")

# Check 3: Import test
print("\n3. Checking Python packages...")
try:
    import google.generativeai as genai
    print("   ✅ google-generativeai installed")
except ImportError:
    print("   ❌ google-generativeai not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from google.cloud import aiplatform
    print("   ✅ google-cloud-aiplatform installed")
except ImportError:
    print("   ❌ google-cloud-aiplatform not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import langgraph
    print("   ✅ langgraph installed")
except ImportError:
    print("   ❌ langgraph not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Check 4: Test Gemini API connection
print("\n4. Testing Gemini API connection...")
try:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content("Say 'Hello'")
    print(f"   ✅ Gemini API works! Response: {response.text[:50]}...")
except Exception as e:
    print(f"   ❌ Gemini API error: {e}")
    sys.exit(1)

# Check 5: Vertex AI setup
print("\n5. Checking Vertex AI setup...")
try:
    from google.cloud import aiplatform
    aiplatform.init(project=project_id, location="us-central1")
    print("   ✅ Vertex AI initialized")
    print("   ⚠️  Note: You still need to enable Claude in Model Garden")
    print("   🔗 https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-3-5-sonnet-v2")
except Exception as e:
    print(f"   ⚠️  Vertex AI warning: {e}")

print("\n" + "=" * 80)
print("✅ Setup verification complete!")
print("\nNext steps:")
print("1. Enable Claude in Vertex AI Model Garden (if not done)")
print("2. Run: python test_research_agent.py")
print("=" * 80)
