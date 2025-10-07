"""
Firebase Authentication Middleware for FastAPI.

Verifies Firebase ID tokens and restricts access to @google.com emails only.
"""
import logging
from typing import Optional
from fastapi import HTTPException, Header, Depends
from firebase_admin import auth, credentials, initialize_app
import firebase_admin

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_service.config import (
    ENABLE_AUTH,
    FIREBASE_PROJECT_ID,
    FIREBASE_SERVICE_ACCOUNT_PATH,
    ALLOWED_EMAIL_DOMAIN
)

logger = logging.getLogger(__name__)

# ============================================================================
# Firebase Admin SDK Initialization
# ============================================================================

def initialize_firebase():
    """Initialize Firebase Admin SDK with Application Default Credentials (ADC)."""
    if not ENABLE_AUTH:
        logger.info("🔓 Authentication DISABLED (ENABLE_AUTH=false)")
        return

    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
        logger.info("✅ Firebase already initialized")
    except ValueError:
        # Firebase not initialized yet
        try:
            # Try to use Application Default Credentials (works on CloudRun/GCE)
            if os.path.exists(FIREBASE_SERVICE_ACCOUNT_PATH):
                # Use service account key if available
                cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
                initialize_app(cred, {
                    'projectId': FIREBASE_PROJECT_ID
                })
                logger.info(f"✅ Firebase initialized with service account: {FIREBASE_SERVICE_ACCOUNT_PATH}")
            else:
                # Use Application Default Credentials (ADC)
                # This works automatically on CloudRun, GCE, local with gcloud auth
                cred = credentials.ApplicationDefault()
                initialize_app(cred, {
                    'projectId': FIREBASE_PROJECT_ID
                })
                logger.info("✅ Firebase initialized with Application Default Credentials (ADC)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            # Don't raise - allow app to start without auth if needed
            pass


# ============================================================================
# Auth Dependency
# ============================================================================

async def verify_google_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Verify Firebase ID token and restrict to @google.com emails only.

    This function acts as a FastAPI dependency that:
    1. If ENABLE_AUTH=false: Returns None (no auth required)
    2. If ENABLE_AUTH=true: Verifies Firebase token and enforces @google.com domain

    Args:
        authorization: Authorization header with format "Bearer {token}"

    Returns:
        User info dict with 'uid', 'email' if authenticated
        None if authentication is disabled

    Raises:
        HTTPException 401: If token is missing, invalid, or email not @google.com
    """
    # If auth is disabled, return None (allow all requests)
    if not ENABLE_AUTH:
        return None

    # Auth is enabled - require valid token
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header. Please sign in with Google."
        )

    # Extract token from "Bearer {token}"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise ValueError("Invalid authorization scheme")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected 'Bearer {token}'"
        )

    # Verify Firebase ID token
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email')

        if not email:
            raise HTTPException(
                status_code=401,
                detail="Email not found in token. Please sign in with Google."
            )

        # Enforce @google.com domain restriction
        if not email.endswith(f"@{ALLOWED_EMAIL_DOMAIN}"):
            logger.warning(f"⚠️ Unauthorized access attempt from: {email}")
            raise HTTPException(
                status_code=403,
                detail=f"Access restricted to @{ALLOWED_EMAIL_DOMAIN} email addresses only."
            )

        logger.info(f"✅ Authenticated user: {email}")

        return {
            'uid': uid,
            'email': email
        }

    except auth.InvalidIdTokenError as e:
        logger.error(f"❌ Invalid Firebase ID token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token. Please sign in again."
        )
    except auth.ExpiredIdTokenError as e:
        logger.error(f"❌ Expired Firebase ID token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token expired. Please sign in again."
        )
    except Exception as e:
        logger.error(f"❌ Token verification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="Authentication failed. Please try again."
        )


# ============================================================================
# Optional Auth Dependency
# ============================================================================

async def optional_google_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Optional authentication - returns user info if auth is enabled and token provided.

    Unlike verify_google_user, this does NOT raise an error if auth is enabled
    but no token is provided. This is useful for endpoints that want to support
    both authenticated and unauthenticated access.

    Returns:
        User info dict if authenticated
        None if auth is disabled OR no token provided
    """
    if not ENABLE_AUTH or not authorization:
        return None

    try:
        return await verify_google_user(authorization)
    except HTTPException:
        return None
