"""
Test Complete Pipeline for Klick.com - New customer demo.
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


async def test_klick_demo():
    """Test complete demo generation pipeline for Klick.com."""
    load_dotenv()

    logger.info("="*80)
    logger.info("KLICK.COM DEMO GENERATION")
    logger.info("="*80)
    logger.info("\nGenerating complete demo for new customer: Klick.com")
    logger.info("\nPipeline stages:")
    logger.info("  1. Research Agent - Analyze klick.com")
    logger.info("  2. Demo Story Agent - Create demo narrative")
    logger.info("  3. Data Modeling Agent - Design schema")
    logger.info("  4. Synthetic Data Generator - Generate data")
    logger.info("  5. Infrastructure Agent - Provision BigQuery")
    logger.info("  6. CAPI Instruction Generator - Create YAML")
    logger.info("  7. Demo Validator - Validate queries")
    logger.info("\nExpected time: ~5-8 minutes")

    # Create orchestrator
    orchestrator = DemoOrchestrator()

    # Run pipeline for Klick
    customer_url = "https://www.klick.com"
    project_id = "bq-demos-469816"

    logger.info(f"\n{'='*80}")
    logger.info("STARTING KLICK.COM DEMO GENERATION...")
    logger.info("="*80)

    try:
        final_state = await orchestrator.generate_demo(
            customer_url=customer_url,
            project_id=project_id
        )

        # Display final results
        logger.info("\n" + "="*80)
        logger.info("KLICK.COM DEMO COMPLETE!")
        logger.info("="*80)

        customer_info = final_state.get("customer_info", {})
        demo_story = final_state.get("demo_story", {})
        dataset_id = final_state.get("dataset_id", "")

        logger.info(f"\n📋 CUSTOMER PROFILE")
        logger.info(f"Company: {customer_info.get('company_name', 'N/A')}")
        logger.info(f"Industry: {customer_info.get('industry', 'N/A')}")
        logger.info(f"Use Cases: {', '.join(customer_info.get('use_cases', [])[:3])}")

        logger.info(f"\n🎯 DEMO NARRATIVE")
        logger.info(f"Title: {demo_story.get('demo_title', 'N/A')}")
        logger.info(f"Executive Summary: {demo_story.get('executive_summary', 'N/A')[:150]}...")

        logger.info(f"\n🗄️ BIGQUERY DATASET")
        logger.info(f"Dataset: {final_state.get('dataset_full_name', 'N/A')}")
        logger.info(f"Console: https://console.cloud.google.com/bigquery?project={project_id}&d={dataset_id}")

        table_stats = final_state.get("table_stats", {})
        if table_stats:
            total_rows = sum(s['row_count'] for s in table_stats.values())
            total_size = sum(s['size_mb'] for s in table_stats.values())
            logger.info(f"\n📊 DATA STATISTICS")
            logger.info(f"Tables: {len(table_stats)}")
            logger.info(f"Total Rows: {total_rows:,}")
            logger.info(f"Total Size: {total_size:.2f} MB")

        logger.info(f"\n📄 GENERATED ARTIFACTS")
        logger.info(f"Schema: /tmp/schema_klick.json")
        logger.info(f"Demo Story: /tmp/demo_story_klick.json")
        logger.info(f"CAPI YAML: {final_state.get('capi_yaml_file', 'N/A')}")
        demo_docs = final_state.get("demo_documentation", {})
        logger.info(f"Demo Report: {demo_docs.get('report_file', 'N/A')}")

        logger.info(f"\n💡 GOLDEN QUERIES")
        golden_queries = demo_story.get("golden_queries", [])
        logger.info(f"Total: {len(golden_queries)}")
        if golden_queries:
            logger.info(f"\nFirst 3 queries:")
            for i, query in enumerate(golden_queries[:3], 1):
                logger.info(f"  {i}. [{query.get('complexity', '')}] {query.get('question', '')[:80]}...")

        validation_results = final_state.get("validation_results", {})
        logger.info(f"\n✅ VALIDATION RESULTS")
        logger.info(f"Queries Tested: {validation_results.get('total_queries', 0)}")
        logger.info(f"SQL Validated: {validation_results.get('sql_validated', 0)}")

        logger.info(f"\n🎬 NEXT STEPS")
        logger.info("1. Review the demo report for complete demo flow")
        logger.info("2. Use the CAPI YAML to create a Conversational Analytics agent")
        logger.info("3. Test golden queries in the CAPI interface")
        logger.info("4. Customize the demo story for your sales call")
        logger.info("5. Present to Klick!")

        logger.info(f"\n{'='*80}")
        logger.info("✅ KLICK.COM DEMO READY FOR PRESENTATION!")
        logger.info("="*80)

        return final_state

    except Exception as e:
        logger.error("\n❌ KLICK.COM DEMO GENERATION FAILED")
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_klick_demo())
