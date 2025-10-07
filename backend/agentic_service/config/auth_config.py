"""
Firebase Authentication Configuration.

Environment variables:
- ENABLE_AUTH: "true" to enable Firebase auth, "false" to disable (default: false)
- FIREBASE_PROJECT_ID: Firebase project ID (default: from GCP project)
- FIREBASE_SERVICE_ACCOUNT_PATH: Path to service account JSON (optional, uses ADC if not set)
- ALLOWED_EMAIL_DOMAIN: Domain restriction for authentication (default: google.com)
"""
import os

# ============================================================================
# Authentication Configuration
# ============================================================================

# Feature flag: Enable/disable Firebase authentication
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"

# Firebase configuration
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "bq-demos-469816")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_PATH",
    "/app/firebase-service-account.json"
)

# Domain restriction: Only allow users from this email domain
ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "google.com")
