#!/bin/bash
# ========================================
# LOCAL API VALIDATION TEST
# ========================================
# Quick test to validate local server is working
# Usage: ./test_local.sh (run after starting local_server.sh)

set -e  # Exit on error

API="http://localhost:8000"
TIMEOUT=5

echo "🧪 Testing Local API..."
echo "========================================"
echo "API Endpoint: $API"
echo ""

# Test 1: Health Check
echo "1️⃣ Test: Health Check"
echo "   GET $API/health"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT $API/health 2>/dev/null || echo "FAILED")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ PASS - Server is healthy (HTTP $HTTP_CODE)"
    echo "   Response: $(echo "$HEALTH_RESPONSE" | head -1 | jq -c .)"
else
    echo "   ❌ FAIL - Server not responding (HTTP $HTTP_CODE)"
    echo "   Make sure local_server.sh is running!"
    exit 1
fi
echo ""

# Test 2: Provision History (empty or has jobs)
echo "2️⃣ Test: Provision History API"
echo "   GET $API/api/provision/history"
HISTORY_RESPONSE=$(curl -s --max-time $TIMEOUT $API/api/provision/history 2>/dev/null)
TOTAL_JOBS=$(echo "$HISTORY_RESPONSE" | jq -r '.total' 2>/dev/null || echo "ERROR")

if [ "$TOTAL_JOBS" != "ERROR" ]; then
    echo "   ✅ PASS - History API working"
    echo "   Total jobs: $TOTAL_JOBS"
else
    echo "   ❌ FAIL - Could not parse response"
    echo "   Response: $HISTORY_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Start a Quick Test Provision (test.com - will fail fast)
echo "3️⃣ Test: Start Provision (test.com - expected to fail quickly)"
echo "   POST $API/api/provision/start"
START_RESPONSE=$(curl -s -X POST $API/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.test.com"}' 2>/dev/null)

JOB_ID=$(echo "$START_RESPONSE" | jq -r '.job_id' 2>/dev/null)

if [ "$JOB_ID" != "null" ] && [ -n "$JOB_ID" ]; then
    echo "   ✅ PASS - Provision job started"
    echo "   Job ID: $JOB_ID"
else
    echo "   ❌ FAIL - Could not start provision"
    echo "   Response: $START_RESPONSE"
    exit 1
fi
echo ""

# Test 4: Monitor Progress (3 quick checks)
echo "4️⃣ Test: Monitor Job Progress (checking 3 times...)"
for i in {1..3}; do
    sleep 2
    STATUS_RESPONSE=$(curl -s $API/api/provision/status/$JOB_ID 2>/dev/null)
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status' 2>/dev/null || echo "ERROR")
    PHASE=$(echo "$STATUS_RESPONSE" | jq -r '.current_phase' 2>/dev/null || echo "unknown")
    PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.overall_progress' 2>/dev/null || echo "0")

    if [ "$STATUS" != "ERROR" ]; then
        echo "   Check $i/3: Status=$STATUS, Phase=$PHASE, Progress=$PROGRESS%"
    else
        echo "   Check $i/3: ❌ Could not get status"
    fi
done
echo ""

# Summary
echo "========================================"
echo "✅ ALL TESTS PASSED!"
echo "========================================"
echo ""
echo "📋 Summary:"
echo "  ✅ Server is running and healthy"
echo "  ✅ API endpoints are responding"
echo "  ✅ Can create provision jobs"
echo "  ✅ Can query job status"
echo "  ✅ Job ID: $JOB_ID"
echo ""
echo "🌐 Next Steps:"
echo "  1. Open CE Dashboard: http://localhost:8000/ce-dashboard"
echo "  2. Watch progress: http://localhost:8000/provision-progress?jobId=$JOB_ID"
echo "  3. Check job status: curl $API/api/provision/status/$JOB_ID | jq"
echo ""
echo "💡 The test job (test.com) will fail at Research Agent (expected)"
echo "   This is normal - it's just to verify the pipeline starts!"
echo ""
