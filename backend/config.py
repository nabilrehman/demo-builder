"""
Configuration for CAPI Demo Generation Backend.

Includes feature flags for optional Firebase authentication.
"""
import os
from typing import Optional

# ========================================
# FEATURE FLAGS
# ========================================

# Enable Firebase Authentication and Firestore persistence
# When FALSE: App works without auth (backward compatible)
# When TRUE: Requires Google Sign-In (@google.com only) and persists jobs to Firestore
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'

# ========================================
# FIREBASE CONFIGURATION
# ========================================

# Firebase project ID (same as GCP project)
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'bq-demos-469816')

# Path to Firebase service account key (for backend)
# Download from: Firebase Console → Project Settings → Service Accounts
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv(
    'FIREBASE_SERVICE_ACCOUNT_PATH',
    '/tmp/firebase-service-account.json'  # Default path for CloudRun
)

# ========================================
# FIRESTORE CONFIGURATION
# ========================================

# Firestore database ID (default is "(default)")
FIRESTORE_DATABASE_ID = os.getenv('FIRESTORE_DATABASE_ID', '(default)')

# Firestore location
FIRESTORE_LOCATION = os.getenv('FIRESTORE_LOCATION', 'us-central1')

# ========================================
# AUTHENTICATION CONFIGURATION
# ========================================

# Allowed email domain for authentication
ALLOWED_EMAIL_DOMAIN = os.getenv('ALLOWED_EMAIL_DOMAIN', 'google.com')

# ========================================
# EXISTING CONFIGURATION
# ========================================

# GCP Project for BigQuery, Vertex AI, etc.
PROJECT_ID = os.getenv('PROJECT_ID') or os.getenv('DEVSHELL_PROJECT_ID') or 'bq-demos-469816'
LOCATION = os.getenv('LOCATION', 'us-central1')

# LLM Model Selection
RESEARCH_AGENT_MODEL = os.getenv('RESEARCH_AGENT_MODEL', 'gemini')
DEMO_STORY_AGENT_MODEL = os.getenv('DEMO_STORY_AGENT_MODEL', 'gemini')
DATA_MODELING_AGENT_MODEL = os.getenv('DATA_MODELING_AGENT_MODEL', 'claude')
CAPI_AGENT_MODEL = os.getenv('CAPI_AGENT_MODEL', 'claude')

# Demo Generation Settings
DEMO_NUM_QUERIES = int(os.getenv('DEMO_NUM_QUERIES', '6'))
DEMO_NUM_SCENES = int(os.getenv('DEMO_NUM_SCENES', '4'))
DEMO_NUM_ENTITIES = int(os.getenv('DEMO_NUM_ENTITIES', '8'))

# Research Agent V2 Settings
V2_MAX_PAGES = int(os.getenv('V2_MAX_PAGES', '30'))
V2_MAX_DEPTH = int(os.getenv('V2_MAX_DEPTH', '2'))
V2_ENABLE_BLOG = os.getenv('V2_ENABLE_BLOG', 'false').lower() == 'true'
V2_ENABLE_LINKEDIN = os.getenv('V2_ENABLE_LINKEDIN', 'false').lower() == 'true'
V2_ENABLE_YOUTUBE = os.getenv('V2_ENABLE_YOUTUBE', 'false').lower() == 'true'

# Force LLM data generation (no Faker fallback)
FORCE_LLM_DATA_GENERATION = os.getenv('FORCE_LLM_DATA_GENERATION', 'true').lower() == 'true'

# ========================================
# LOGGING
# ========================================

def print_config():
    """Print current configuration (useful for debugging)."""
    print("=" * 80)
    print("CAPI DEMO GENERATION - CONFIGURATION")
    print("=" * 80)
    print(f"🔐 ENABLE_AUTH: {ENABLE_AUTH}")
    if ENABLE_AUTH:
        print(f"   Firebase Project: {FIREBASE_PROJECT_ID}")
        print(f"   Allowed Domain: @{ALLOWED_EMAIL_DOMAIN}")
        print(f"   Firestore: {FIRESTORE_DATABASE_ID} ({FIRESTORE_LOCATION})")
    print(f"📊 Project: {PROJECT_ID}")
    print(f"🤖 Models: Research={RESEARCH_AGENT_MODEL}, Story={DEMO_STORY_AGENT_MODEL}")
    print("=" * 80)


if __name__ == "__main__":
    # Test configuration
    print_config()
