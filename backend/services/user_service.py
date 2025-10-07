"""
User Management Service

Provides user-specific analytics and job management functions.
"""
from google.cloud import firestore
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management and analytics."""

    def __init__(self, db: firestore.Client):
        """Initialize with Firestore client."""
        self.db = db

    async def get_user_stats(self, user_id: str) -> Dict:
        """
        Calculate user statistics from their jobs.

        Args:
            user_id: Firebase user ID

        Returns:
            Dictionary with user stats:
            - total_jobs: Total number of jobs
            - completed_jobs: Number of completed jobs
            - failed_jobs: Number of failed jobs
            - running_jobs: Number of currently running jobs
            - success_rate: Percentage of successful jobs
            - avg_completion_time: Average time for completed jobs (seconds)
            - total_time_saved: Estimated time saved using the platform
        """
        try:
            # Get all jobs for user
            jobs_ref = self.db.collection('users').document(user_id).collection('jobs')
            jobs = jobs_ref.stream()

            total_jobs = 0
            completed_jobs = 0
            failed_jobs = 0
            running_jobs = 0
            pending_jobs = 0
            total_completion_time = 0

            for job_doc in jobs:
                total_jobs += 1
                job = job_doc.to_dict()

                status = job.get('status', 'unknown')

                if status == 'completed':
                    completed_jobs += 1

                    # Calculate completion time if timestamps available
                    created_at = job.get('created_at')
                    updated_at = job.get('updated_at')

                    if created_at and updated_at:
                        # Convert Firestore timestamps to datetime
                        if hasattr(created_at, 'seconds'):
                            created_dt = datetime.fromtimestamp(created_at.seconds)
                        else:
                            created_dt = datetime.fromisoformat(str(created_at))

                        if hasattr(updated_at, 'seconds'):
                            updated_dt = datetime.fromtimestamp(updated_at.seconds)
                        else:
                            updated_dt = datetime.fromisoformat(str(updated_at))

                        completion_time = (updated_dt - created_dt).total_seconds()
                        total_completion_time += completion_time

                elif status == 'failed':
                    failed_jobs += 1
                elif status == 'running':
                    running_jobs += 1
                elif status == 'pending':
                    pending_jobs += 1

            # Calculate success rate
            finished_jobs = completed_jobs + failed_jobs
            success_rate = (completed_jobs / finished_jobs * 100) if finished_jobs > 0 else 0

            # Calculate average completion time
            avg_completion_time = (total_completion_time / completed_jobs) if completed_jobs > 0 else 0

            # Estimate time saved (assume manual process takes 4 hours per demo)
            manual_time_per_demo = 4 * 60 * 60  # 4 hours in seconds
            time_saved = (manual_time_per_demo - avg_completion_time) * completed_jobs if completed_jobs > 0 else 0

            stats = {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'running_jobs': running_jobs,
                'pending_jobs': pending_jobs,
                'success_rate': round(success_rate, 1),
                'avg_completion_time': int(avg_completion_time),
                'total_time_saved': int(time_saved)
            }

            logger.info(f"📊 User stats for {user_id}: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error calculating user stats: {e}", exc_info=True)
            return {
                'total_jobs': 0,
                'completed_jobs': 0,
                'failed_jobs': 0,
                'running_jobs': 0,
                'pending_jobs': 0,
                'success_rate': 0,
                'avg_completion_time': 0,
                'total_time_saved': 0
            }

    async def get_recent_activity(self, user_id: str, limit: int = 5) -> List[Dict]:
        """
        Get recent job activity for user.

        Args:
            user_id: Firebase user ID
            limit: Number of recent items to return

        Returns:
            List of recent activity items
        """
        try:
            jobs_ref = self.db.collection('users').document(user_id).collection('jobs')

            # Order by created_at descending (most recent first)
            query = jobs_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            jobs = query.stream()

            activity = []
            for job_doc in jobs:
                job = job_doc.to_dict()

                # Format activity item
                activity_item = {
                    'job_id': job_doc.id,
                    'customer_url': job.get('customer_url', ''),
                    'status': job.get('status', 'unknown'),
                    'created_at': job.get('created_at'),
                    'mode': job.get('mode', 'default'),
                    'metadata': job.get('metadata', {})
                }

                activity.append(activity_item)

            logger.info(f"📋 Retrieved {len(activity)} recent activities for user {user_id}")
            return activity

        except Exception as e:
            logger.error(f"Error getting recent activity: {e}", exc_info=True)
            return []

    async def delete_job(self, user_id: str, job_id: str) -> bool:
        """
        Delete a user's job.

        Args:
            user_id: Firebase user ID
            job_id: Job ID to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            doc_ref = self.db.collection('users').document(user_id).collection('jobs').document(job_id)
            doc_ref.delete()

            logger.info(f"🗑️ Deleted job {job_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting job: {e}", exc_info=True)
            return False

    async def update_job_metadata(self, user_id: str, job_id: str, updates: Dict) -> bool:
        """
        Update job metadata (e.g., pin/unpin, add tags).

        Args:
            user_id: Firebase user ID
            job_id: Job ID to update
            updates: Dictionary of fields to update

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            doc_ref = self.db.collection('users').document(user_id).collection('jobs').document(job_id)

            # Add updated timestamp
            updates['updated_at'] = firestore.SERVER_TIMESTAMP

            doc_ref.update(updates)

            logger.info(f"✏️ Updated job {job_id} for user {user_id}: {updates}")
            return True

        except Exception as e:
            logger.error(f"Error updating job metadata: {e}", exc_info=True)
            return False
