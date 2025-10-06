#!/bin/bash

JOB_ID="089da078-68cf-429b-96e5-2b611dda7dbd"
SNAPSHOT_NAME="lululemon_20251006"

echo "========================================="
echo "🔍 Monitoring Lululemon Job for Completion"
echo "========================================="
echo "Job ID: $JOB_ID"
echo "Will capture snapshot: $SNAPSHOT_NAME"
echo ""

while true; do
  STATUS=$(curl -s http://localhost:8000/api/provision/status/$JOB_ID)
  JOB_STATUS=$(echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'running'))" 2>/dev/null)
  PROGRESS=$(echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('overall_progress', 0))" 2>/dev/null)
  PHASE=$(echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('current_phase', 'Unknown'))" 2>/dev/null)

  echo "[$(date +%H:%M:%S)] Status: $JOB_STATUS | Phase: $PHASE | Progress: $PROGRESS%"

  # Check if completed
  if [[ "$JOB_STATUS" == "completed" ]]; then
    echo ""
    echo "✅ JOB COMPLETED! Capturing snapshot immediately..."
    echo ""

    # Capture snapshot IMMEDIATELY while still in memory
    cd /home/admin_/final_demo/capi/demo-gen-capi/backend
    python -m tests.utils.snapshot_capture $JOB_ID --name $SNAPSHOT_NAME --create-template

    if [ $? -eq 0 ]; then
      echo ""
      echo "✅ Snapshot captured successfully!"
      echo ""
      echo "Verifying snapshot data..."
      ls -lah tests/fixtures/snapshots/$SNAPSHOT_NAME/
      echo ""
      echo "Running verification tests..."
      python test_snapshot_verification.py
    else
      echo "❌ Snapshot capture failed!"
    fi

    break
  fi

  # Check if failed
  if [[ "$JOB_STATUS" == "failed" ]]; then
    echo ""
    echo "❌ JOB FAILED - Cannot capture snapshot"
    echo ""
    echo "Recent logs:"
    echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  [{log.get('phase', 'N/A')}] {log['message']}\") for log in data.get('recent_logs', [])[-10:]]"
    break
  fi

  sleep 15
done

echo ""
echo "========================================="
echo "Monitoring complete"
echo "========================================="
