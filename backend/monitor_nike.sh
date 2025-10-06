#!/bin/bash
JOB_ID="63c7e982-e372-4849-8226-ebc730053e03"

while true; do
  RESPONSE=$(curl -s http://localhost:8000/api/provision/status/$JOB_ID)
  STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null)
  PROGRESS=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('overall_progress', 0))" 2>/dev/null)
  PHASE=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('current_phase', 'N/A'))" 2>/dev/null)
  
  echo "[$(date '+%H:%M:%S')] Status: $STATUS | Phase: $PHASE | Progress: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ]; then
    echo "✅ Job completed! Capturing snapshot..."
    cd /home/admin_/final_demo/capi/demo-gen-capi/backend
    python -m tests.utils.snapshot_capture $JOB_ID --name nike_20251006
    echo "🎉 Snapshot captured successfully!"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "❌ Job failed"
    break
  fi
  
  sleep 10
done
