"""
Test API Endpoints

Simple script to test the new provisioning API endpoints.
"""

import requests
import json
import time
import sseclient  # pip install sseclient-py

BASE_URL = "http://localhost:8000"

def test_start_provision():
    """Test starting a new default provisioning job."""
    print("\n" + "="*80)
    print("TEST 1: Start Default Provisioning")
    print("="*80)

    response = requests.post(
        f"{BASE_URL}/api/provision/start",
        json={
            "customer_url": "https://www.shopify.com",
            "project_id": "bq-demos-469816"
        }
    )

    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    return data.get("job_id")


def test_get_status(job_id: str):
    """Test getting job status."""
    print("\n" + "="*80)
    print(f"TEST 2: Get Job Status - {job_id}")
    print("="*80)

    response = requests.get(f"{BASE_URL}/api/provision/status/{job_id}")

    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Status: {data.get('status')}")
    print(f"Current Phase: {data.get('current_phase')}")
    print(f"Overall Progress: {data.get('overall_progress')}%")

    print(f"\nAgents:")
    for agent in data.get("agents", []):
        print(f"  - {agent['name']}: {agent['status']} ({agent['progress_percentage']}%)")

    print(f"\nRecent Logs ({len(data.get('recent_logs', []))}):")
    for log in data.get("recent_logs", [])[-5:]:
        print(f"  [{log['level']}] {log['message']}")

    return data


def test_stream_progress(job_id: str, max_events: int = 20):
    """Test SSE stream of job progress."""
    print("\n" + "="*80)
    print(f"TEST 3: Stream Progress (SSE) - {job_id}")
    print("="*80)

    url = f"{BASE_URL}/api/provision/stream/{job_id}"
    print(f"Connecting to: {url}")

    response = requests.get(url, stream=True, headers={'Accept': 'text/event-stream'})
    client = sseclient.SSEClient(response)

    event_count = 0
    for event in client.events():
        if event.data:
            try:
                data = json.loads(event.data)
                print(f"\n[Event {event_count + 1}]")
                print(f"Status: {data.get('status')}")
                print(f"Phase: {data.get('current_phase')}")
                print(f"Progress: {data.get('overall_progress')}%")

                event_count += 1

                if event_count >= max_events:
                    print(f"\nReached max events ({max_events}), stopping stream")
                    break

                if data.get('status') in ['completed', 'failed', 'cancelled']:
                    print(f"\nJob finished with status: {data.get('status')}")
                    break

            except json.JSONDecodeError:
                print(f"Non-JSON event: {event.data}")


def test_get_history():
    """Test getting job history."""
    print("\n" + "="*80)
    print("TEST 4: Get Job History")
    print("="*80)

    response = requests.get(f"{BASE_URL}/api/provision/history?limit=10")

    print(f"Status Code: {response.status_code}")
    data = response.json()

    print(f"\nTotal Jobs: {data.get('total')}")
    print(f"\nRecent Jobs:")
    for job in data.get("jobs", []):
        print(f"  - {job['job_id'][:8]}... | {job['customer_url']} | {job['status']} | {job.get('total_time', 'N/A')}")


def test_get_assets(job_id: str):
    """Test getting demo assets (only works for completed jobs)."""
    print("\n" + "="*80)
    print(f"TEST 5: Get Demo Assets - {job_id}")
    print("="*80)

    response = requests.get(f"{BASE_URL}/api/provision/assets/{job_id}")

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Demo Title: {data.get('demo_title')}")
        print(f"Golden Queries: {len(data.get('golden_queries', []))}")
        print(f"Schema Tables: {len(data.get('schema', []))}")
        print(f"Dataset ID: {data.get('metadata', {}).get('datasetId')}")
    else:
        print(f"Error: {response.text}")


def test_crazy_frog_provision():
    """Test starting a Crazy Frog mode provisioning job."""
    print("\n" + "="*80)
    print("TEST 6: Start Crazy Frog Provisioning")
    print("="*80)

    response = requests.post(
        f"{BASE_URL}/api/provision/crazy-frog",
        json={
            "customer_url": "https://www.stripe.com",
            "use_case_context": "Leading payment processing company. Need to demo real-time transaction monitoring for CFO. Focus on fraud detection and revenue analytics. Target persona: CFO who wants to see transaction patterns and anomaly detection.",
            "industry_hint": "Fintech",
            "target_persona": "CFO",
            "demo_complexity": "Advanced",
            "special_focus": "Fraud Detection",
            "project_id": "bq-demos-469816"
        }
    )

    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    return data.get("job_id")


if __name__ == "__main__":
    print("\n🧪 TESTING PROVISIONING API ENDPOINTS")
    print("="*80)
    print("Make sure the backend is running: python backend/api.py")
    print("="*80)

    try:
        # Test 1: Start default provision
        job_id = test_start_provision()

        if job_id:
            # Wait a bit for job to start
            time.sleep(2)

            # Test 2: Get status
            test_get_status(job_id)

            # Test 3: Stream progress (limited events for testing)
            print("\n⚠️  Skipping SSE stream test (requires sseclient-py)")
            print("To test SSE: pip install sseclient-py && uncomment line below")
            # test_stream_progress(job_id, max_events=5)

        # Test 4: Get history
        test_get_history()

        # Test 5: Get assets (will fail if job not complete)
        if job_id:
            print("\n⚠️  Assets test will fail if job not completed yet")
            test_get_assets(job_id)

        # Test 6: Crazy Frog mode
        print("\n⚠️  Skipping Crazy Frog test (takes ~10 minutes)")
        print("To test: Uncomment line below")
        # crazy_frog_job_id = test_crazy_frog_provision()

        print("\n" + "="*80)
        print("✅ API ENDPOINT TESTS COMPLETE")
        print("="*80)

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend at " + BASE_URL)
        print("Make sure the backend is running: python backend/api.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
