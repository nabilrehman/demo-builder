#!/bin/bash

JOB_ID="c4fda613-c6dc-44c7-8955-d15ce8f28e00"
SNAPSHOT_NAME="stripe_20251006"

echo "🔍 Monitoring job $JOB_ID..."
echo ""

while true; do
  STATUS=$(curl -s http://localhost:8000/api/provision/status/$JOB_ID)
  
  JOB_STATUS=$(echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null)
  PHASE=$(echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('current_phase', 'Unknown'))" 2>/dev/null)
  PROGRESS=$(echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('overall_progress', 0))" 2>/dev/null)
  
  echo "[$(date +%H:%M:%S)] Status: $JOB_STATUS | Phase: $PHASE | Progress: $PROGRESS%"
  
  # If Infrastructure Agent phase, show CAPI creation logs
  if [[ "$PHASE" == *"Infrastructure"* ]]; then
    echo "  🔧 Infrastructure Agent running - checking for CAPI creation..."
    echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); logs=[l for l in data.get('recent_logs',[]) if 'CAPI' in l.get('message','')]; [print(f\"    {l['message']}\") for l in logs[-3:]]" 2>/dev/null
  fi
  
  # If completed successfully, capture snapshot immediately
  if [[ "$JOB_STATUS" == "completed" ]]; then
    echo ""
    echo "✅ JOB COMPLETED! Capturing snapshot immediately..."
    python -m tests.utils.snapshot_capture $JOB_ID --name $SNAPSHOT_NAME --create-template
    
    if [ $? -eq 0 ]; then
      echo ""
      echo "🎉 Snapshot captured successfully!"
      echo ""
      echo "📦 Running test to verify framework..."
      pytest tests/test_infrastructure_agent_with_fixtures.py::TestInfrastructureAgentWithFixtures::test_list_available_fixtures -v
    else
      echo "❌ Snapshot capture failed"
    fi
    
    break
  fi
  
  # If failed, stop monitoring
  if [[ "$JOB_STATUS" == "failed" ]]; then
    echo ""
    echo "❌ JOB FAILED"
    echo "Last logs:"
    echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  {l['message']}\") for l in data.get('recent_logs',[])[-5:]]"
    break
  fi
  
  sleep 15
done
