"""
Test script for Data Modeling Agent.
"""
import asyncio
import logging
import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.research_agent import CustomerResearchAgent
from agentic_service.agents.data_modeling_agent import DataModelingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_full_pipeline(url: str):
    """Test Research Agent -> Data Modeling Agent pipeline."""
    logger.info(f"Testing full pipeline with URL: {url}")

    # Create initial state
    state = {
        "customer_url": url,
        "project_id": os.getenv("PROJECT_ID", "bq-demos-469816"),
        "job_id": "test-002"
    }

    # Phase 1: Research
    logger.info("\n" + "="*80)
    logger.info("PHASE 1: RESEARCH (Claude)")
    logger.info("="*80)

    research_agent = CustomerResearchAgent()
    state = await research_agent.execute(state)

    logger.info(f"\n✅ Research complete:")
    logger.info(f"   Company: {state.get('customer_info', {}).get('company_name')}")
    logger.info(f"   Domain: {state.get('business_domain')}")
    logger.info(f"   Entities: {len(state.get('key_entities', []))}")

    # Phase 2: Data Modeling
    logger.info("\n" + "="*80)
    logger.info("PHASE 2: DATA MODELING (Gemini)")
    logger.info("="*80)

    modeling_agent = DataModelingAgent()
    state = await modeling_agent.execute(state)

    logger.info(f"\n✅ Schema design complete:")
    logger.info(f"   Tables: {len(state.get('tables', []))}")

    # Show table details
    schema = state.get('schema', {})
    for table in schema.get('tables', []):
        logger.info(f"\n   📊 Table: {table['name']}")
        logger.info(f"      Description: {table.get('description', 'N/A')}")
        logger.info(f"      Fields: {len(table.get('schema', []))}")
        logger.info(f"      Sample rows: {table.get('record_count', 0)}")

        # Show first few fields
        for field in table.get('schema', [])[:3]:
            logger.info(f"         - {field['name']}: {field['type']} ({field['mode']})")

    # Save full schema
    output_file = f"/tmp/schema_{state.get('customer_info', {}).get('company_name', 'test').lower()}.json"
    with open(output_file, 'w') as f:
        json.dump(schema, f, indent=2)

    logger.info(f"\n📄 Full schema saved to: {output_file}")

    return state


async def main():
    """Main test function."""
    # Load environment variables
    load_dotenv()

    # Test URL
    test_url = "https://www.shopify.com"

    try:
        await test_full_pipeline(test_url)
        logger.info("\n" + "="*80)
        logger.info("✅ FULL PIPELINE TEST PASSED!")
        logger.info("="*80)
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
