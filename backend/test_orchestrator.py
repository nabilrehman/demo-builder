"""
Test Complete Pipeline - End-to-end demo generation.
"""
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.demo_orchestrator import DemoOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_full_pipeline():
    """Test complete demo generation pipeline."""
    load_dotenv()

    logger.info("="*80)
    logger.info("FULL PIPELINE TEST")
    logger.info("="*80)
    logger.info("\nThis will execute all 7 agents in sequence:")
    logger.info("  1. Research Agent")
    logger.info("  2. Demo Story Agent")
    logger.info("  3. Data Modeling Agent")
    logger.info("  4. Synthetic Data Generator")
    logger.info("  5. Infrastructure Agent")
    logger.info("  6. CAPI Instruction Generator")
    logger.info("  7. Demo Validator")
    logger.info("\nExpected time: ~5-8 minutes")

    # Create orchestrator
    orchestrator = DemoOrchestrator()

    # Run pipeline
    customer_url = "https://www.shopify.com"
    project_id = "bq-demos-469816"

    logger.info(f"\nCustomer URL: {customer_url}")
    logger.info(f"Project ID: {project_id}")

    logger.info("\n" + "="*80)
    logger.info("STARTING PIPELINE...")
    logger.info("="*80)

    try:
        final_state = await orchestrator.generate_demo(
            customer_url=customer_url,
            project_id=project_id
        )

        # Display final results
        logger.info("\n" + "="*80)
        logger.info("FINAL RESULTS")
        logger.info("="*80)

        logger.info("\n📂 Generated Files:")
        logger.info(f"  - Schema: /tmp/schema_shopify.json")
        logger.info(f"  - Demo Story: /tmp/demo_story_shopify.json")
        logger.info(f"  - CAPI YAML: {final_state.get('capi_yaml_file', 'N/A')}")
        logger.info(f"  - Demo Report: {final_state.get('demo_documentation', {}).get('report_file', 'N/A')}")
        logger.info(f"  - Validation Report: /tmp/demo_validation_report.md")

        logger.info("\n🗄️ BigQuery:")
        logger.info(f"  - Dataset: {final_state.get('dataset_full_name', 'N/A')}")
        logger.info(f"  - Console: https://console.cloud.google.com/bigquery?project={project_id}&d={final_state.get('dataset_id', '')}")

        table_stats = final_state.get("table_stats", {})
        if table_stats:
            logger.info(f"\n📊 Tables Created:")
            for table_name, stats in table_stats.items():
                logger.info(f"  - {table_name}: {stats['row_count']:,} rows")

        logger.info("\n✅ SUCCESS!")
        logger.info("Demo is ready for presentation!")

        return final_state

    except Exception as e:
        logger.error("\n❌ PIPELINE FAILED")
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
