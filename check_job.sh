#!/bin/bash
JOB_ID="27ddb089-43ca-4c84-83fe-10950a7b5664"

curl -s http://localhost:8000/api/provision/status/$JOB_ID | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Status: {data[\"status\"]}')
print(f'Phase: {data[\"current_phase\"]}')
print(f'Progress: {data[\"overall_progress\"]}%')
print(f'Dataset: {data.get(\"dataset_id\", \"Not yet created\")}')
print(f'Agent: {data.get(\"demo_agent_id\", \"Not yet created\")}')
print(f'\nLast log: {data.get(\"recent_logs\", [{}])[-1].get(\"message\", \"N/A\")}')

if data['status'] == 'completed':
    print(f'\n✅ READY TO TEST!')
    print(f'\n📋 Copy this URL:')
    print(f'https://8080-cs-XXXXXX.cs-us-central1-pits.cloudshell.dev/analytics-dashboard?dataset_id={data.get(\"dataset_id\")}&agent_id={data.get(\"demo_agent_id\")}&job_id={data[\"job_id\"]}')
"
