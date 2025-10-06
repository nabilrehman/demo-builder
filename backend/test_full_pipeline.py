"""
Test script for full agent pipeline.
Research → Demo Story → Data Modeling
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
from agentic_service.agents.demo_story_agent import DemoStoryAgent
from agentic_service.agents.data_modeling_agent import DataModelingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_full_pipeline(url: str):
    """Test the complete 3-agent pipeline."""
    logger.info("="*80)
    logger.info(f"TESTING FULL PIPELINE: {url}")
    logger.info("="*80)

    # Create initial state
    state = {
        "customer_url": url,
        "project_id": os.getenv("PROJECT_ID", "bq-demos-469816"),
        "job_id": "test-full-001"
    }

    # =================================================================
    # PHASE 1: RESEARCH (Claude 4.5)
    # =================================================================
    logger.info("\n" + "="*80)
    logger.info("PHASE 1: CUSTOMER RESEARCH (Claude 4.5)")
    logger.info("="*80)

    research_agent = CustomerResearchAgent()
    state = await research_agent.execute(state)

    logger.info(f"\n✅ Research complete:")
    logger.info(f"   Company: {state['customer_info']['company_name']}")
    logger.info(f"   Domain: {state['business_domain']}")
    logger.info(f"   Industry: {state['industry']}")
    logger.info(f"   Key Entities: {len(state['key_entities'])}")

    # =================================================================
    # PHASE 2: DEMO STORY (Claude 4.5 - Principal Architect mode)
    # =================================================================
    logger.info("\n" + "="*80)
    logger.info("PHASE 2: DEMO STORY CREATION (Claude 4.5 - Principal Architect)")
    logger.info("="*80)

    demo_story_agent = DemoStoryAgent()
    state = await demo_story_agent.execute(state)

    demo_story = state['demo_story']
    logger.info(f"\n✅ Demo story created:")
    logger.info(f"   Title: {demo_story['demo_title']}")
    logger.info(f"   Executive Summary: {demo_story['executive_summary']}")
    logger.info(f"\n   Business Challenges: {len(demo_story['business_challenges'])}")
    for i, challenge in enumerate(demo_story['business_challenges'], 1):
        logger.info(f"      {i}. {challenge['challenge']}")

    logger.info(f"\n   Story Arc: {len(demo_story['demo_narrative']['story_arc'])} scenes")
    for i, scene in enumerate(demo_story['demo_narrative']['story_arc'][:3], 1):
        logger.info(f"      Scene {i}: {scene['scene']}")
        logger.info(f"         → {scene['user_asks']}")

    logger.info(f"\n   Golden Queries: {len(demo_story['golden_queries'])}")
    for i, query in enumerate(demo_story['golden_queries'][:5], 1):
        logger.info(f"      Q{i} [{query['complexity']}]: {query['question']}")
        logger.info(f"          Chart: {query['expected_chart_type']} | Value: {query['business_value'][:60]}...")

    # =================================================================
    # PHASE 3: DATA MODELING (Gemini - driven by demo story)
    # =================================================================
    logger.info("\n" + "="*80)
    logger.info("PHASE 3: DATA MODELING (Gemini - Story-Driven)")
    logger.info("="*80)

    # Update the data modeling agent to use demo story
    modeling_agent = DataModelingAgent()
    state = await modeling_agent.execute(state)

    schema = state['schema']
    logger.info(f"\n✅ Schema designed:")
    logger.info(f"   Tables: {len(schema['tables'])}")

    for table in schema['tables']:
        logger.info(f"\n   📊 {table['name']}")
        logger.info(f"      Purpose: {table.get('purpose_in_demo', 'N/A')[:80]}...")
        logger.info(f"      Fields: {len(table['schema'])}")
        logger.info(f"      Rows: {table.get('record_count', 0):,}")
        if table.get('enables_queries'):
            logger.info(f"      Enables queries: {table['enables_queries']}")

    # =================================================================
    # SAVE OUTPUTS
    # =================================================================
    company_name = state['customer_info']['company_name'].lower().replace(' ', '_')

    # Save demo story
    story_file = f"/tmp/demo_story_{company_name}.json"
    with open(story_file, 'w') as f:
        json.dump(demo_story, f, indent=2)
    logger.info(f"\n📄 Demo story saved: {story_file}")

    # Save schema
    schema_file = f"/tmp/schema_{company_name}.json"
    with open(schema_file, 'w') as f:
        json.dump(schema, f, indent=2)
    logger.info(f"📄 Schema saved: {schema_file}")

    # Save complete state
    state_file = f"/tmp/state_{company_name}.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2, default=str)
    logger.info(f"📄 Complete state saved: {state_file}")

    return state


async def main():
    """Main test function."""
    load_dotenv()

    test_url = "https://www.shopify.com"

    try:
        state = await test_full_pipeline(test_url)

        logger.info("\n" + "="*80)
        logger.info("✅ FULL PIPELINE SUCCESS!")
        logger.info("="*80)
        logger.info(f"\nDemo Title: {state['demo_title']}")
        logger.info(f"Golden Queries: {len(state['golden_queries'])}")
        logger.info(f"Tables Created: {len(state['schema']['tables'])}")
        logger.info("\nNext steps:")
        logger.info("  1. Generate synthetic data")
        logger.info("  2. Provision BigQuery infrastructure")
        logger.info("  3. Create CAPI agent")
        logger.info("  4. Test golden queries")

    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
