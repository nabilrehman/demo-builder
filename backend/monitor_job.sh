#!/bin/bash
# Monitor provision job with detailed logging

JOB_ID=$1

if [ -z "$JOB_ID" ]; then
    echo "Usage: $0 <job_id>"
    exit 1
fi

for i in {1..20}; do
    echo "========================================"
    echo "Check $i/20"
    echo "========================================"

    curl -s http://localhost:8000/api/provision/status/$JOB_ID | python3 << 'PYTHON_SCRIPT'
import sys, json
data = json.load(sys.stdin)

print(f"Status: {data['status']} | Phase: {data['current_phase']} | Progress: {data['overall_progress']}%\n")

print("Recent Logs:")
for log in data['recent_logs'][-8:]:
    print(f"  [{log['level']}] {log['message']}")

print("\nAgents:")
for agent in data['agents']:
    if agent['status'] == 'completed':
        icon = '✅'
    elif agent['status'] == 'running':
        icon = '🔄'
    elif agent['status'] == 'failed':
        icon = '❌'
    else:
        icon = '⏸️'
    print(f"  {icon} {agent['name']}: {agent['status']} ({agent['progress_percentage']}%)")

if data.get('errors'):
    print(f"\n⚠️  Errors: {len(data['errors'])}")
PYTHON_SCRIPT

    if [ $i -lt 20 ]; then
        sleep 15
        echo ""
    fi
done
