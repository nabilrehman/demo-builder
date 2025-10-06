#!/usr/bin/env python3
"""Monitor provisioning job progress."""

import requests
import time
import sys
from datetime import datetime

# Update for new job and URL
JOB_ID = "4f367227-8b27-4693-8f4e-8f38fe4e89bd"
URL = f"https://demo-gen-capi-549403515075.us-east5.run.app/api/provision/status/{JOB_ID}"

def monitor():
    max_checks = 30  # 15 minutes max
    check_interval = 30  # seconds

    for i in range(1, max_checks + 1):
        print(f"\n{'='*60}")
        print(f"Check {i}/{max_checks} at {datetime.now().strftime('%H:%M:%S')}")
        print('='*60)

        try:
            response = requests.get(URL, timeout=10)
            data = response.json()

            status = data.get('status', 'unknown')
            phase = data.get('current_phase', 'N/A')
            progress = data.get('overall_progress', 0)

            print(f"Status: {status}")
            print(f"Phase: {phase}")
            print(f"Progress: {progress}%")

            # Agent summary
            agents = data.get('agents', [])
            print(f"\nAgent Status:")
            for j, agent in enumerate(agents, 1):
                name = agent.get('name', 'Unknown')
                agent_status = agent.get('status', 'unknown')
                emoji = "✅" if agent_status == "completed" else "⏳" if agent_status == "running" else "⏸️"
                print(f"  {emoji} {j}. {name}: {agent_status}")

            # Recent logs
            logs = data.get('recent_logs', [])
            if logs:
                print(f"\nRecent Logs (last 5):")
                for log in logs[-5:]:
                    phase_name = log.get('phase', 'N/A')
                    message = log.get('message', '')
                    print(f"  [{phase_name}] {message}")

            # Check if done
            if status == "completed":
                print("\n🎉 PROVISIONING COMPLETED!")
                print(f"\nDataset: {data.get('dataset_name', 'N/A')}")
                print(f"Tables Created: {len(data.get('tables', []))}")

                # Show golden queries
                golden_queries = data.get('golden_queries', [])
                if golden_queries:
                    print(f"\nGolden Queries: {len(golden_queries)}")
                    for idx, q in enumerate(golden_queries[:3], 1):
                        title = q.get('title', 'Untitled')
                        print(f"  {idx}. {title}")

                return True
            elif status == "failed":
                print("\n❌ PROVISIONING FAILED!")
                error = data.get('error', 'Unknown error')
                print(f"Error: {error}")
                return False

        except Exception as e:
            print(f"⚠️  Error fetching status: {e}")

        if i < max_checks:
            print(f"\n⏳ Waiting {check_interval}s...")
            time.sleep(check_interval)

    print("\n⏰ Monitoring timeout reached (15 minutes)")
    print("Provisioning may still be running. Check manually:")
    print(f"curl {URL}")
    return None

if __name__ == "__main__":
    success = monitor()
    sys.exit(0 if success else 1)
