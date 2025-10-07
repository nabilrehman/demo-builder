"""
User Management API Endpoints

Provides REST API for user statistics, job management, and preferences.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging

# Import auth middleware
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middleware.auth import optional_google_user, verify_google_user
from services.firestore_service import firestore_service
from services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["user-management"])

# Initialize user service with Firestore client
user_service = None
if firestore_service.db:
    user_service = UserService(firestore_service.db)


# ============================================================================
# Request/Response Models
# ============================================================================

class UserStatsResponse(BaseModel):
    """User statistics response."""
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    running_jobs: int
    pending_jobs: int
    success_rate: float
    avg_completion_time: int  # seconds
    total_time_saved: int  # seconds


class RecentActivityResponse(BaseModel):
    """Recent activity response."""
    activities: List[Dict]
    total: int


class DeleteJobResponse(BaseModel):
    """Job deletion response."""
    success: bool
    message: str


class UpdateJobRequest(BaseModel):
    """Request to update job metadata."""
    is_pinned: Optional[bool] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(user: dict = Depends(verify_google_user)):
    """
    Get user statistics.

    Requires authentication. Returns job counts, success rate, and time saved.
    """
    if not user_service:
        raise HTTPException(status_code=503, detail="User service not available (Firestore disabled)")

    user_id = user['uid']
    logger.info(f"Fetching stats for user {user['email']}")

    stats = await user_service.get_user_stats(user_id)

    return UserStatsResponse(**stats)


@router.get("/activity", response_model=RecentActivityResponse)
async def get_recent_activity(
    limit: int = 5,
    user: dict = Depends(verify_google_user)
):
    """
    Get recent job activity.

    Requires authentication. Returns recent jobs ordered by creation date.
    """
    if not user_service:
        raise HTTPException(status_code=503, detail="User service not available (Firestore disabled)")

    user_id = user['uid']
    logger.info(f"Fetching recent activity for user {user['email']} (limit={limit})")

    activities = await user_service.get_recent_activity(user_id, limit=limit)

    return RecentActivityResponse(
        activities=activities,
        total=len(activities)
    )


@router.delete("/jobs/{job_id}", response_model=DeleteJobResponse)
async def delete_job(
    job_id: str,
    user: dict = Depends(verify_google_user)
):
    """
    Delete a job.

    Requires authentication. User can only delete their own jobs.
    """
    if not user_service:
        raise HTTPException(status_code=503, detail="User service not available (Firestore disabled)")

    user_id = user['uid']
    logger.info(f"User {user['email']} deleting job {job_id}")

    # Verify job belongs to user
    job = await firestore_service.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Delete job
    success = await user_service.delete_job(user_id, job_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete job")

    return DeleteJobResponse(
        success=True,
        message=f"Job {job_id} deleted successfully"
    )


@router.patch("/jobs/{job_id}")
async def update_job(
    job_id: str,
    updates: UpdateJobRequest,
    user: dict = Depends(verify_google_user)
):
    """
    Update job metadata (pin, tags, notes).

    Requires authentication. User can only update their own jobs.
    """
    if not user_service:
        raise HTTPException(status_code=503, detail="User service not available (Firestore disabled)")

    user_id = user['uid']
    logger.info(f"User {user['email']} updating job {job_id}")

    # Verify job belongs to user
    job = await firestore_service.get_job(user_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Build updates dict (only include non-None values)
    update_dict = {}
    if updates.is_pinned is not None:
        update_dict['is_pinned'] = updates.is_pinned
    if updates.tags is not None:
        update_dict['tags'] = updates.tags
    if updates.notes is not None:
        update_dict['notes'] = updates.notes

    if not update_dict:
        raise HTTPException(status_code=400, detail="No updates provided")

    # Update job
    success = await user_service.update_job_metadata(user_id, job_id, update_dict)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update job")

    return {
        "success": True,
        "message": f"Job {job_id} updated successfully",
        "updates": update_dict
    }


@router.get("/profile")
async def get_user_profile(user: dict = Depends(verify_google_user)):
    """
    Get user profile.

    Requires authentication. Returns user info and preferences.
    """
    user_id = user['uid']
    email = user['email']

    # Get profile from Firestore (if exists)
    # For now, return basic info from auth token
    profile = {
        "user_id": user_id,
        "email": email,
        "display_name": email.split('@')[0],  # Use email prefix as display name
        "preferences": {
            "default_mode": "default",
            "email_notifications": False,
            "retention_days": 90
        }
    }

    return profile
