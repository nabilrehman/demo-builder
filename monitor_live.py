#!/usr/bin/env python3
"""Live monitoring of provisioning with company name display."""

import requests
import time
import sys
from datetime import datetime

# Read job ID from file
with open('/tmp/current_job_id.txt', 'r') as f:
    JOB_ID = f.read().strip()

URL = f"https://demo-gen-capi-549403515075.us-east5.run.app/api/provision/status/{JOB_ID}"

def monitor():
    max_checks = 40  # 20 minutes max (more time for full pipeline)
    check_interval = 30  # seconds

    print(f"\n{'='*70}")
    print(f"🎬 MONITORING PROVISIONING JOB: {JOB_ID}")
    print(f"{'='*70}\n")

    for i in range(1, max_checks + 1):
        print(f"{'─'*70}")
        print(f"📊 Check {i}/{max_checks} at {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'─'*70}")

        status = "unknown"  # Initialize before try block

        try:
            response = requests.get(URL, timeout=30)
            data = response.json()

            status = data.get('status', 'unknown')
            phase = data.get('current_phase', 'N/A')
            progress = data.get('overall_progress', 0)
            company_name = data.get('company_name', 'Unknown')

            # Show company name prominently
            print(f"\n🏢 Company: {company_name}")
            print(f"📍 Status: {status}")
            print(f"⚙️  Phase: {phase}")
            print(f"📈 Progress: {progress}%")

            # Agent summary with emojis
            agents = data.get('agents', [])
            print(f"\n🤖 Agent Status:")
            for j, agent in enumerate(agents, 1):
                name = agent.get('name', 'Unknown')
                agent_status = agent.get('status', 'unknown')

                # Emoji based on status
                if agent_status == "completed":
                    emoji = "✅"
                elif agent_status == "running":
                    emoji = "⏳"
                elif agent_status == "failed":
                    emoji = "❌"
                else:
                    emoji = "⏸️"

                print(f"   {emoji} {j}. {name}: {agent_status}")

            # Recent logs (last 3)
            logs = data.get('recent_logs', [])
            if logs:
                print(f"\n📝 Recent Logs:")
                for log in logs[-3:]:
                    phase_name = log.get('phase', 'N/A')
                    message = log.get('message', '')
                    # Truncate long messages
                    if len(message) > 80:
                        message = message[:77] + "..."
                    print(f"   [{phase_name}] {message}")

            # Check if done
            if status == "completed":
                print(f"\n{'='*70}")
                print("🎉 PROVISIONING COMPLETED!")
                print(f"{'='*70}")
                print(f"\n🏢 Company: {company_name}")
                print(f"📊 Dataset: {data.get('dataset_full_name', 'N/A')}")

                # Show golden queries
                golden_queries = data.get('golden_queries', [])
                if golden_queries:
                    print(f"💎 Golden Queries: {len(golden_queries)}")
                    for idx, q in enumerate(golden_queries[:3], 1):
                        title = q.get('title', 'Untitled')
                        print(f"   {idx}. {title}")

                return True
            elif status == "failed":
                print(f"\n{'='*70}")
                print("❌ PROVISIONING FAILED!")
                print(f"{'='*70}")
                errors = data.get('errors', [])
                if errors:
                    print(f"\n⚠️  Errors:")
                    for error in errors:
                        print(f"   • {error}")
                return False

        except Exception as e:
            print(f"⚠️  Error fetching status: {e}")

        if i < max_checks and status not in ["completed", "failed"]:
            print(f"\n⏳ Waiting {check_interval}s...\n")
            time.sleep(check_interval)

    print(f"\n{'='*70}")
    print("⏰ Monitoring timeout reached (20 minutes)")
    print(f"{'='*70}")
    print("Provisioning may still be running. Check manually:")
    print(f"curl {URL}")
    return None

if __name__ == "__main__":
    success = monitor()
    sys.exit(0 if success else 1)
