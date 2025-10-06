#!/bin/bash
JOB_ID="0bc0ad48-b554-4aa3-96eb-d8a9e66cd2ce"

echo "🔍 Monitoring Adidas Job: $JOB_ID"
echo "===================================="

while true; do
  RESPONSE=$(curl -s http://localhost:8000/api/provision/status/$JOB_ID)
  STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null)
  PROGRESS=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('overall_progress', 0))" 2>/dev/null)
  PHASE=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('current_phase', 'N/A'))" 2>/dev/null)
  
  echo "[$(date '+%H:%M:%S')] $STATUS | $PHASE | $PROGRESS%"
  
  if [ "$STATUS" = "completed" ]; then
    echo ""
    echo "✅ Job completed successfully!"
    echo "===================================="
    echo ""
    echo "📊 Testing CAPI Creation & Demo Validator..."
    echo ""
    
    # Extract key data from completed job
    echo "$RESPONSE" | python3 << 'PYTEST'
import sys, json
data = json.load(sys.stdin)

print("🔍 Job Summary:")
print(f"  Customer: {data.get('customer_url')}")
print(f"  Dataset: {data.get('dataset_full_name')}")
print(f"  CAPI Agent ID: {data.get('capi_agent_id')}")
print()

# Check Infrastructure Agent
infra_agent = next((a for a in data.get('agents', []) if 'Infrastructure' in a['name']), {})
print(f"✅ Infrastructure Agent: {infra_agent.get('status')}")
if infra_agent.get('error_message'):
    print(f"   ❌ Error: {infra_agent['error_message']}")
else:
    print(f"   ⏱️  Time: {infra_agent.get('elapsed_seconds')}s")

# Check Demo Validator
validator = next((a for a in data.get('agents', []) if 'Validator' in a['name']), {})
print(f"✅ Demo Validator: {validator.get('status')}")
if validator.get('error_message'):
    print(f"   ❌ Error: {validator['error_message']}")
else:
    print(f"   ⏱️  Time: {validator.get('elapsed_seconds')}s")
    
print()
print("🎯 CRITICAL CHECKS:")
print(f"  1. CAPI Agent Created: {'✅ YES' if data.get('capi_agent_id') else '❌ NO'}")
print(f"  2. BigQuery Dataset: {'✅ YES' if data.get('dataset_full_name') else '❌ NO'}")
print(f"  3. All Agents Completed: {'✅ YES' if all(a['status'] == 'completed' for a in data.get('agents', [])) else '❌ NO'}")

# Check for errors
errors = data.get('errors', [])
if errors:
    print(f"\n⚠️  Errors Found: {len(errors)}")
    for err in errors[:3]:
        print(f"     • {err[:100]}")
else:
    print(f"\n✅ No Errors!")

PYTEST
    
    break
  elif [ "$STATUS" = "failed" ]; then
    echo ""
    echo "❌ Job failed"
    echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('\nErrors:'); [print(f'  • {e}') for e in data.get('errors', [])]"
    break
  fi
  
  sleep 15
done
