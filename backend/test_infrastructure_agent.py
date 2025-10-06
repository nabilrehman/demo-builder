"""
Test Infrastructure Agent - BigQuery provisioning.
"""
import asyncio
import logging
import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.infrastructure_agent import InfrastructureAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_infrastructure():
    """Test BigQuery infrastructure provisioning."""
    load_dotenv()

    # Load existing data from previous tests
    schema_file = "/tmp/schema_shopify.json"
    demo_story_file = "/tmp/demo_story_shopify.json"

    if not os.path.exists(schema_file):
        logger.error(f"Schema file not found: {schema_file}")
        logger.info("Run test_full_pipeline.py first to generate schema")
        return

    with open(schema_file) as f:
        schema = json.load(f)

    with open(demo_story_file) as f:
        demo_story = json.load(f)

    # Find synthetic data files
    data_dir = "/tmp/synthetic_data"
    if not os.path.exists(data_dir):
        logger.error(f"Synthetic data directory not found: {data_dir}")
        logger.info("Run test_synthetic_data.py first to generate data")
        return

    synthetic_data_files = [
        os.path.join(data_dir, f) for f in os.listdir(data_dir)
        if f.endswith('.csv')
    ]

    # Create state
    state = {
        "schema": schema,
        "demo_story": demo_story,
        "customer_info": {
            "company_name": "Shopify",
            "industry": "E-commerce Platform"
        },
        "synthetic_data_files": synthetic_data_files,
        "project_id": "bq-demos-469816"
    }

    logger.info("="*80)
    logger.info("INFRASTRUCTURE AGENT TEST")
    logger.info("="*80)
    logger.info(f"\nProject: {state['project_id']}")
    logger.info(f"Company: {state['customer_info']['company_name']}")
    logger.info(f"Data files: {len(synthetic_data_files)}")

    # Provision infrastructure
    logger.info("\n" + "="*80)
    logger.info("Provisioning BigQuery infrastructure...")
    logger.info("="*80)

    agent = InfrastructureAgent()
    state = await agent.execute(state)

    # Display results
    logger.info("\n" + "="*80)
    logger.info("PROVISIONING RESULTS")
    logger.info("="*80)

    dataset_id = state.get("dataset_id")
    dataset_full_name = state.get("dataset_full_name")
    table_stats = state.get("table_stats", {})
    demo_docs = state.get("demo_documentation", {})

    logger.info(f"\n✅ Dataset Created: {dataset_full_name}")
    logger.info(f"\nBigQuery Console:")
    logger.info(f"https://console.cloud.google.com/bigquery?project=bq-demos-469816&d={dataset_id}")

    logger.info("\n" + "="*80)
    logger.info("TABLE STATISTICS")
    logger.info("="*80)

    for table_name, stats in table_stats.items():
        logger.info(f"\n📊 {table_name}")
        logger.info(f"   Rows: {stats['row_count']:,}")
        logger.info(f"   Size: {stats['size_mb']:.2f} MB")
        logger.info(f"   Full Name: {stats['full_name']}")

    total_rows = sum(s['row_count'] for s in table_stats.values())
    total_size = sum(s['size_mb'] for s in table_stats.values())

    logger.info("\n" + "="*80)
    logger.info("SUMMARY")
    logger.info("="*80)
    logger.info(f"Total Tables: {len(table_stats)}")
    logger.info(f"Total Rows: {total_rows:,}")
    logger.info(f"Total Size: {total_size:.2f} MB")

    # Display demo report info
    report_file = demo_docs.get("report_file")
    if report_file and os.path.exists(report_file):
        logger.info("\n" + "="*80)
        logger.info("DEMO REPORT GENERATED")
        logger.info("="*80)
        logger.info(f"Report: {report_file}")

        # Show first few lines of report
        with open(report_file) as f:
            lines = f.readlines()[:20]
        logger.info("\nFirst 20 lines of report:")
        logger.info("".join(lines))

    # Display golden queries
    golden_queries = demo_docs.get("golden_queries", [])
    if golden_queries:
        logger.info("\n" + "="*80)
        logger.info("GOLDEN QUERIES (First 3)")
        logger.info("="*80)
        for i, query in enumerate(golden_queries[:3], 1):
            logger.info(f"\n{i}. {query.get('question', '')}")
            logger.info(f"   Complexity: {query.get('complexity', '')}")
            logger.info(f"   Business Value: {query.get('business_value', '')}")

    return state


if __name__ == "__main__":
    asyncio.run(test_infrastructure())
