# Agent Evaluation Framework - Quick Start

## What This Does

Tests the agentic demo generation pipeline across 10 diverse customer sites and evaluates quality of generated demos, queries, and results.

---

## Quick Test (3 Sites, ~25 Minutes)

Tests Snowflake, Stripe, and HubSpot - three different industries to validate the system works beyond e-commerce.

```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/backend
python test_evaluation.py
```

**Expected Output:**
```
[1/3] Testing https://www.snowflake.com...
Stage 1/7: Research Agent • Running...
...
✅ SUCCESS: https://www.snowflake.com
   Time: 612s
   Quality Score: 87/100
   Queries: 14 (4 expert)
   Data: 315,420 rows across 12 tables

[2/3] Testing https://www.stripe.com...
...
```

**Results Saved To:**
- `/tmp/agent_evaluation_TIMESTAMP.json` - Detailed metrics
- `/tmp/agent_evaluation_report_TIMESTAMP.md` - Executive summary

---

## Full Evaluation (10 Sites, ~90 Minutes)

Tests all 10 diverse industries:
1. Shopify (E-commerce)
2. Klick (Healthcare)
3. Snowflake (Data Platform)
4. Stripe (Payments)
5. HubSpot (Marketing)
6. Zendesk (Customer Support)
7. Atlassian (Software Dev)
8. Slack (Enterprise Communication)
9. Airbnb (Travel)
10. DoorDash (Food Delivery)

```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/backend
python agent_evaluation_framework.py
```

**Recommended:** Run overnight or during lunch. Each site takes ~8-12 minutes.

---

## What Gets Evaluated

### Per-Demo Metrics (40+ Dimensions)

**Pipeline Execution:**
- Total time (sec)
- Success/failure rate
- Failed stage (if any)
- Per-agent timing

**Demo Quality Scores (0-100):**
- **Narrative Quality:** Title structure, customer name presence, action words
- **Query Complexity:** Distribution of SIMPLE/MEDIUM/COMPLEX/EXPERT queries
- **Schema Quality:** Table count, fields per table, relationships, no REPEATED fields
- **Data Quality:** Total rows, balanced sizes, realistic volumes
- **Overall Quality:** Weighted average of all components

**Detailed Metrics:**
- Golden queries: count, complexity breakdown, avg question length
- Schema: tables, fields, relationships, REPEATED field detection
- Data: rows, size MB, largest/smallest tables
- CAPI YAML: file size, system_instruction presence, table/relationship counts
- Validation: queries validated, queries failed, SQL errors

---

## Expected Results

### Success Rate
- **Target:** >80% of demos complete successfully
- **Current:** 50% (Shopify ✅, Klick ❌ due to REPEATED field bug)
- **After Fix:** Expected 80-90%

### Failures
**Known Issues:**
- **REPEATED Fields:** Healthcare/consulting demos fail at Infrastructure stage
- **Website Scraping:** Some sites block bots or have aggressive CORS

**Failure Breakdown (Expected):**
```
Infrastructure (REPEATED field): 2-3 demos
Research (scraping blocked): 0-1 demos
Demo Story (timeout): 0 demos
```

### Quality Scores (Successful Demos)
- **Avg Overall Quality:** 75-85/100
- **Avg Narrative Quality:** 80-90/100
- **Avg Query Complexity:** 70-80/100
- **Avg Schema Quality:** 70-85/100

### Performance
- **Avg Generation Time:** 8-12 minutes
- **Fastest Agent:** Research (10-20 sec)
- **Slowest Agent:** Demo Story (4-7 min)

---

## Reading the Reports

### JSON Report (`/tmp/agent_evaluation_TIMESTAMP.json`)

```json
[
  {
    "customer_url": "https://www.shopify.com",
    "company_name": "Shopify",
    "industry": "E-commerce Platform (SaaS)",
    "total_time_seconds": 683.2,
    "success": true,
    "total_queries": 12,
    "expert_queries": 3,
    "total_tables": 15,
    "total_rows": 403200,
    "total_size_mb": 25.51,
    "overall_quality_score": 87,
    "narrative_quality_score": 85,
    "query_complexity_score": 82,
    "schema_quality_score": 90
  },
  ...
]
```

### Markdown Report (`/tmp/agent_evaluation_report_TIMESTAMP.md`)

```markdown
# Agent Evaluation Report

**Generated:** 2025-10-04 18:30:00
**Project:** bq-demos-469816

## Executive Summary

- **Total Tests:** 10
- **Successful:** 8 (80%)
- **Failed:** 2 (20%)

### Successful Demos:
- **Avg Generation Time:** 9.2 minutes
- **Avg Quality Score:** 81/100
- **Avg Queries:** 14.3
- **Avg Tables:** 13.1

## Successful Demos

### Shopify (https://www.shopify.com)
**Quality Score:** 87/100
**Industry:** E-commerce Platform (SaaS)
**Generation Time:** 11m 23s
**Golden Queries:** 12 (2 simple, 5 medium, 3 complex, 2 expert)
**Data:** 403,200 rows, 15 tables, 25.51 MB
...
```

---

## Interpreting Scores

### Overall Quality Score (0-100)

**90-100:** Exceptional
- Perfect demo title
- 5+ expert queries
- 15-20 tables with relationships
- 100K-500K realistic rows

**75-89:** Excellent
- Great demo title
- 2-4 expert queries
- 10-15 tables
- 40K-100K rows

**60-74:** Good
- Decent demo title
- 1-2 expert queries
- 5-10 tables
- 20K-40K rows

**<60:** Needs Improvement
- Generic title
- No expert queries
- <5 tables
- <20K rows

### Component Scores

**Narrative Quality (25% weight):**
- Demo title length (50-150 chars ideal)
- Customer name in title (bonus points)
- Action words ("from", "to", "how", etc.)

**Query Complexity (30% weight):**
- EXPERT queries worth 50 points
- COMPLEX queries worth 40 points
- MEDIUM queries worth 25 points
- SIMPLE queries worth 10 points

**Schema Quality (25% weight):**
- Table count (5-20 ideal)
- Fields per table (5-15 ideal)
- Relationships defined (+10 each)
- REPEATED fields penalty (-50)

**Data Quality (20% weight):**
- Total rows (40K-500K ideal)
- Balanced table sizes
- Realistic data volume

---

## Troubleshooting

### "REPEATED field" errors
**Cause:** Gemini generates array/repeated fields; BigQuery CSV loader can't handle them

**Fix:** Update `backend/agentic_service/utils/prompt_templates.py`:
```python
DATA_MODELING_PROMPT = """
...
IMPORTANT CONSTRAINTS:
- NEVER use REPEATED or ARRAY field types
- Use STRING with comma-separated values instead
- Create junction tables for many-to-many relationships
...
"""
```

### "Website scraping failed"
**Cause:** Site blocks bots or requires JavaScript rendering

**Fix:** Add user agent or use Playwright for JS-heavy sites

### "Timeout" errors
**Cause:** LLM API throttling or slow response

**Fix:** Add retry logic with exponential backoff

### "Permission denied" (BigQuery)
**Cause:** Missing IAM roles

**Fix:**
```bash
gcloud projects add-iam-policy-binding bq-demos-469816 \
  --member="user:YOUR_EMAIL" \
  --role="roles/bigquery.admin"
```

---

## Next Steps After Evaluation

1. **Analyze Results:**
   - Which industries have highest quality?
   - Which stages fail most?
   - What's the avg generation time?

2. **Fix Issues:**
   - Address REPEATED field bug
   - Add retry logic for common failures
   - Improve error messages

3. **Optimize:**
   - Can we parallelize agents?
   - Can we cache research results?
   - Can we reduce CAPI YAML generation time?

4. **Scale:**
   - Build CE Dashboard with real-time progress
   - Deploy to Cloud Run
   - Add authentication and job persistence

---

## Advanced: Custom Test Sites

Edit `agent_evaluation_framework.py`:

```python
class AgentEvaluationFramework:
    TEST_SITES = [
        {
            'url': 'https://your-custom-site.com',
            'expected_industry': 'Your Industry',
            'description': 'Brief description'
        },
        # Add more...
    ]
```

Then run:
```bash
python agent_evaluation_framework.py
```

---

## Questions?

Check:
1. **PROGRESS.md** - Comprehensive progress report
2. **SUMMARY.md** - Complete system summary
3. **CE-PROGRESS-MESSAGES.md** - Progress message examples

Or review the logs - they're extremely detailed!
