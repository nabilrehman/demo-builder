"""
Firestore service layer for user-scoped job persistence.

Provides functions to save and retrieve provisioning jobs scoped to individual users.
Jobs are stored under: users/{userId}/jobs/{jobId}
"""
from google.cloud import firestore
from datetime import datetime
from typing import List, Optional, Dict
import logging

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_service.config import ENABLE_AUTH
FIRESTORE_DATABASE_ID = os.getenv("FIRESTORE_DATABASE_ID", "(default)")

logger = logging.getLogger(__name__)


class FirestoreService:
    """Firestore service for user-scoped job persistence."""

    def __init__(self):
        """Initialize Firestore client if auth is enabled."""
        if ENABLE_AUTH:
            try:
                self.db = firestore.Client(database=FIRESTORE_DATABASE_ID)
                logger.info(f"✅ Firestore client initialized: {FIRESTORE_DATABASE_ID}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Firestore: {e}")
                self.db = None
        else:
            self.db = None
            logger.info("🔓 Firestore disabled (ENABLE_AUTH=false)")

    async def save_job(self, user_id: str, job_id: str, job_data: Dict) -> None:
        """
        Save job to Firestore under users/{userId}/jobs/{jobId}.

        Args:
            user_id: Firebase user ID (from auth token)
            job_id: Unique job ID
            job_data: Job data to save (status, customer_url, etc.)
        """
        if not self.db:
            logger.debug("Firestore disabled, skipping save_job")
            return

        try:
            doc_ref = self.db.collection('users').document(user_id).collection('jobs').document(job_id)

            # Add server timestamp for updates
            save_data = {
                **job_data,
                'updated_at': firestore.SERVER_TIMESTAMP
            }

            # If this is a new job, also add created_at
            if 'created_at' not in job_data:
                save_data['created_at'] = firestore.SERVER_TIMESTAMP

            doc_ref.set(save_data, merge=True)
            logger.info(f"💾 Job saved to Firestore: users/{user_id}/jobs/{job_id}")

        except Exception as e:
            logger.error(f"❌ Failed to save job to Firestore: {e}", exc_info=True)

    async def get_user_jobs(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict]:
        """
        Get jobs for a user with filtering and pagination.

        Args:
            user_id: Firebase user ID
            limit: Maximum number of jobs to return (default 50)
            offset: Number of jobs to skip (for pagination)
            status: Filter by status (completed, running, failed, pending)
            search: Search in customer_url (case-insensitive)

        Returns:
            List of job dictionaries with 'id' field
        """
        if not self.db:
            logger.debug("Firestore disabled, returning empty jobs list")
            return []

        try:
            jobs_ref = self.db.collection('users').document(user_id).collection('jobs')

            # Build query
            query = jobs_ref

            # Filter by status if provided
            if status and status != 'all':
                query = query.where('status', '==', status)

            # Order by created_at descending (newest first)
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING)

            # Get all matching documents (we'll apply pagination and search in memory for now)
            docs = query.stream()

            jobs = []
            for doc in docs:
                job_data = doc.to_dict()
                job_data['id'] = doc.id

                # Apply search filter if provided
                if search:
                    customer_url = job_data.get('customer_url', '').lower()
                    if search.lower() not in customer_url:
                        continue

                jobs.append(job_data)

            # Apply pagination
            total_count = len(jobs)
            jobs = jobs[offset:offset + limit]

            logger.info(f"📋 Retrieved {len(jobs)}/{total_count} jobs for user {user_id} (status={status}, search={search})")
            return jobs

        except Exception as e:
            logger.error(f"❌ Failed to get user jobs from Firestore: {e}", exc_info=True)
            return []

    async def get_job(self, user_id: str, job_id: str) -> Optional[Dict]:
        """
        Get a specific job for a user.

        Args:
            user_id: Firebase user ID
            job_id: Unique job ID

        Returns:
            Job dictionary with 'id' field, or None if not found
        """
        if not self.db:
            logger.debug("Firestore disabled, returning None for get_job")
            return None

        try:
            doc_ref = self.db.collection('users').document(user_id).collection('jobs').document(job_id)
            doc = doc_ref.get()

            if doc.exists:
                job_data = doc.to_dict()
                job_data['id'] = doc.id
                logger.info(f"📄 Retrieved job: users/{user_id}/jobs/{job_id}")
                return job_data
            else:
                logger.warning(f"⚠️ Job not found: users/{user_id}/jobs/{job_id}")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to get job from Firestore: {e}", exc_info=True)
            return None

    async def update_job_status(self, user_id: str, job_id: str, status: str, metadata: Dict = None) -> None:
        """
        Update job status (and optionally metadata).

        Args:
            user_id: Firebase user ID
            job_id: Unique job ID
            status: New status (e.g., 'running', 'completed', 'failed')
            metadata: Optional metadata to update (e.g., dataset_id, agent_id, etc.)
        """
        if not self.db:
            logger.debug("Firestore disabled, skipping update_job_status")
            return

        try:
            doc_ref = self.db.collection('users').document(user_id).collection('jobs').document(job_id)

            update_data = {
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            }

            if metadata:
                update_data['metadata'] = metadata

            doc_ref.set(update_data, merge=True)
            logger.info(f"✅ Job status updated: users/{user_id}/jobs/{job_id} -> {status}")

        except Exception as e:
            logger.error(f"❌ Failed to update job status: {e}", exc_info=True)

    async def delete_job(self, user_id: str, job_id: str) -> bool:
        """
        Delete a job from Firestore.

        Args:
            user_id: Firebase user ID
            job_id: Unique job ID

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.db:
            logger.debug("Firestore disabled, skipping delete_job")
            return False

        try:
            doc_ref = self.db.collection('users').document(user_id).collection('jobs').document(job_id)
            doc_ref.delete()
            logger.info(f"🗑️ Job deleted: users/{user_id}/jobs/{job_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete job: {e}", exc_info=True)
            return False


# ============================================================================
# Singleton Instance
# ============================================================================

# Create singleton instance to be imported by other modules
firestore_service = FirestoreService()
