"""
Test Demo Validator - Validates golden queries execute successfully.
"""
import asyncio
import logging
import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.demo_validator import DemoValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_validator():
    """Test demo validation."""
    load_dotenv()

    # Load demo story with golden queries
    demo_story_file = "/tmp/demo_story_shopify.json"

    if not os.path.exists(demo_story_file):
        logger.error(f"Demo story file not found: {demo_story_file}")
        logger.info("Run test_full_pipeline.py first to generate demo story")
        return

    with open(demo_story_file) as f:
        demo_story = json.load(f)

    # Create state
    state = {
        "demo_story": demo_story,
        "dataset_full_name": "bq-demos-469816.shopify_capi_demo_20251004",
        "project_id": "bq-demos-469816"
    }

    golden_queries = demo_story.get("golden_queries", [])

    logger.info("="*80)
    logger.info("DEMO VALIDATOR TEST")
    logger.info("="*80)
    logger.info(f"\nDataset: {state['dataset_full_name']}")
    logger.info(f"Golden Queries: {len(golden_queries)}")
    logger.info(f"Testing first 5 queries for speed")

    # Show queries to be tested
    logger.info("\n" + "="*80)
    logger.info("QUERIES TO VALIDATE")
    logger.info("="*80)
    for i, query in enumerate(golden_queries[:5], 1):
        logger.info(f"\n{i}. {query.get('question', '')}")
        logger.info(f"   Complexity: {query.get('complexity', '')}")
        has_sql = "✓" if query.get('expected_sql') else "✗"
        logger.info(f"   Has SQL: {has_sql}")

    # Validate
    logger.info("\n" + "="*80)
    logger.info("RUNNING VALIDATION")
    logger.info("="*80)

    validator = DemoValidator()
    state = await validator.execute(state)

    # Display results
    logger.info("\n" + "="*80)
    logger.info("VALIDATION RESULTS")
    logger.info("="*80)

    validation_results = state.get("validation_results", {})

    logger.info(f"\nTotal Queries: {validation_results.get('total_queries', 0)}")
    logger.info(f"SQL Validated: {validation_results.get('sql_validated', 0)} ✅")
    logger.info(f"SQL Failed: {validation_results.get('sql_failed', 0)} ❌")

    success_rate = 0
    if validation_results.get('total_queries', 0) > 0:
        success_rate = (validation_results.get('sql_validated', 0) /
                       validation_results.get('total_queries', 0)) * 100

    logger.info(f"Success Rate: {success_rate:.1f}%")

    # Show individual results
    sql_results = validation_results.get("sql_results", [])
    if sql_results:
        logger.info("\n" + "="*80)
        logger.info("INDIVIDUAL QUERY RESULTS")
        logger.info("="*80)

        for result in sql_results:
            status = "✅" if result['sql_success'] else "❌"
            logger.info(f"\n{status} Query {result['sequence']}: {result['question'][:60]}...")
            logger.info(f"   Complexity: {result['complexity']}")
            if result['sql_success']:
                logger.info(f"   Rows: {result['row_count']:,}")
                logger.info(f"   Time: {result['execution_time_ms']:.0f}ms")
            else:
                logger.info(f"   Error: {result['sql_error'][:100]}...")

    # Check for report
    report_file = "/tmp/demo_validation_report.md"
    if os.path.exists(report_file):
        logger.info("\n" + "="*80)
        logger.info("VALIDATION REPORT")
        logger.info("="*80)
        logger.info(f"Report saved: {report_file}")

        # Show first 30 lines
        with open(report_file) as f:
            lines = f.readlines()[:30]
        logger.info("\nFirst 30 lines:")
        logger.info("".join(lines))

    # Assessment
    logger.info("\n" + "="*80)
    logger.info("ASSESSMENT")
    logger.info("="*80)

    if success_rate == 100:
        logger.info("✅ PERFECT: All queries validated successfully!")
        logger.info("   Demo is ready for presentation")
    elif success_rate >= 80:
        logger.info("✅ GOOD: Most queries work")
        logger.info("   Review failed queries and fix SQL")
    else:
        logger.info("⚠️  NEEDS WORK: Many queries failing")
        logger.info("   Review schema and SQL generation logic")

    return state


if __name__ == "__main__":
    asyncio.run(test_validator())
