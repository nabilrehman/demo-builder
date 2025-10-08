"""
Test User Management Endpoints

Run this to test the new user management features locally.
"""
import asyncio
from google.cloud import firestore
from services.user_service import UserService
from datetime import datetime, timedelta

async def test_user_stats():
    """Test user stats calculation."""
    print("\n🧪 Testing User Stats Calculation...")

    # Initialize Firestore client
    db = firestore.Client(database='(default)')
    user_service = UserService(db)

    # Test user ID (replace with real user ID from Firebase)
    test_user_id = "test_user_123"

    # Create test jobs
    print("Creating test jobs...")
    jobs_ref = db.collection('users').document(test_user_id).collection('jobs')

    # Create completed job
    jobs_ref.document('job-1').set({
        'customer_url': 'https://nike.com',
        'status': 'completed',
        'mode': 'default',
        'created_at': datetime.utcnow() - timedelta(minutes=10),
        'updated_at': datetime.utcnow() - timedelta(minutes=5),
    })

    # Create failed job
    jobs_ref.document('job-2').set({
        'customer_url': 'https://adidas.com',
        'status': 'failed',
        'mode': 'default',
        'created_at': datetime.utcnow() - timedelta(hours=1),
        'updated_at': datetime.utcnow() - timedelta(hours=1),
    })

    # Create running job
    jobs_ref.document('job-3').set({
        'customer_url': 'https://puma.com',
        'status': 'running',
        'mode': 'crazy_frog',
        'created_at': datetime.utcnow() - timedelta(minutes=2),
        'updated_at': datetime.utcnow(),
    })

    # Calculate stats
    print("\nCalculating stats...")
    stats = await user_service.get_user_stats(test_user_id)

    print("\n📊 User Stats:")
    print(f"  Total Jobs: {stats['total_jobs']}")
    print(f"  Completed: {stats['completed_jobs']}")
    print(f"  Failed: {stats['failed_jobs']}")
    print(f"  Running: {stats['running_jobs']}")
    print(f"  Success Rate: {stats['success_rate']}%")
    print(f"  Avg Completion Time: {stats['avg_completion_time']}s")
    print(f"  Time Saved: {stats['total_time_saved']}s")

    # Assertions
    assert stats['total_jobs'] == 3, "Should have 3 total jobs"
    assert stats['completed_jobs'] == 1, "Should have 1 completed job"
    assert stats['failed_jobs'] == 1, "Should have 1 failed job"
    assert stats['running_jobs'] == 1, "Should have 1 running job"
    assert stats['success_rate'] == 50.0, "Success rate should be 50%"

    print("\n✅ User stats test passed!")

    # Cleanup
    print("\nCleaning up test data...")
    for job_id in ['job-1', 'job-2', 'job-3']:
        jobs_ref.document(job_id).delete()

    print("✅ Cleanup complete!")


async def test_recent_activity():
    """Test recent activity fetching."""
    print("\n🧪 Testing Recent Activity...")

    db = firestore.Client(database='(default)')
    user_service = UserService(db)

    test_user_id = "test_user_123"

    # Create test jobs with different timestamps
    jobs_ref = db.collection('users').document(test_user_id).collection('jobs')

    for i in range(5):
        jobs_ref.document(f'activity-{i}').set({
            'customer_url': f'https://customer{i}.com',
            'status': 'completed',
            'mode': 'default',
            'created_at': datetime.utcnow() - timedelta(hours=i),
            'updated_at': datetime.utcnow() - timedelta(hours=i),
        })

    # Get recent activity
    activities = await user_service.get_recent_activity(test_user_id, limit=3)

    print(f"\n📋 Recent Activity (limit=3): {len(activities)} items")
    for activity in activities:
        print(f"  - {activity['customer_url']} ({activity['status']})")

    assert len(activities) == 3, "Should return 3 activities"
    # First activity should be most recent
    assert 'customer0' in activities[0]['customer_url'], "Most recent should be first"

    print("\n✅ Recent activity test passed!")

    # Cleanup
    for i in range(5):
        jobs_ref.document(f'activity-{i}').delete()


async def test_delete_job():
    """Test job deletion."""
    print("\n🧪 Testing Job Deletion...")

    db = firestore.Client(database='(default)')
    user_service = UserService(db)

    test_user_id = "test_user_123"
    jobs_ref = db.collection('users').document(test_user_id).collection('jobs')

    # Create job
    job_id = 'delete-me'
    jobs_ref.document(job_id).set({
        'customer_url': 'https://delete.com',
        'status': 'completed',
        'created_at': datetime.utcnow(),
    })

    # Verify it exists
    doc = jobs_ref.document(job_id).get()
    assert doc.exists, "Job should exist before deletion"

    # Delete it
    success = await user_service.delete_job(test_user_id, job_id)
    assert success, "Deletion should succeed"

    # Verify it's gone
    doc = jobs_ref.document(job_id).get()
    assert not doc.exists, "Job should not exist after deletion"

    print("\n✅ Job deletion test passed!")


async def test_update_job_metadata():
    """Test job metadata updates."""
    print("\n🧪 Testing Job Metadata Updates...")

    db = firestore.Client(database='(default)')
    user_service = UserService(db)

    test_user_id = "test_user_123"
    jobs_ref = db.collection('users').document(test_user_id).collection('jobs')

    # Create job
    job_id = 'update-me'
    jobs_ref.document(job_id).set({
        'customer_url': 'https://update.com',
        'status': 'completed',
        'created_at': datetime.utcnow(),
    })

    # Update it (pin it)
    success = await user_service.update_job_metadata(
        test_user_id,
        job_id,
        {'is_pinned': True, 'tags': ['important', 'demo']}
    )
    assert success, "Update should succeed"

    # Verify update
    doc = jobs_ref.document(job_id).get()
    job = doc.to_dict()
    assert job['is_pinned'] == True, "Job should be pinned"
    assert 'important' in job['tags'], "Job should have tags"

    print("\n✅ Job metadata update test passed!")

    # Cleanup
    jobs_ref.document(job_id).delete()


async def run_all_tests():
    """Run all user management tests."""
    print("=" * 60)
    print("🧪 User Management Tests")
    print("=" * 60)

    try:
        await test_user_stats()
        await test_recent_activity()
        await test_delete_job()
        await test_update_job_metadata()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
