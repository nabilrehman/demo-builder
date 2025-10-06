"""
Test script for Research Agent.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_research_agent(url: str):
    """Test the research agent with a URL."""
    logger.info(f"Testing Research Agent with URL: {url}")

    # Create initial state
    state = {
        "customer_url": url,
        "project_id": os.getenv("PROJECT_ID", "bq-demos-469816"),
        "job_id": "test-001"
    }

    # Initialize agent
    agent = CustomerResearchAgent()

    # Execute
    try:
        result = await agent.execute(state)

        logger.info("\n" + "="*80)
        logger.info("RESEARCH RESULTS:")
        logger.info("="*80)
        logger.info(f"\nCompany Name: {result.get('customer_info', {}).get('company_name')}")
        logger.info(f"Business Domain: {result.get('business_domain')}")
        logger.info(f"Industry: {result.get('industry')}")
        logger.info(f"\nKey Entities ({len(result.get('key_entities', []))}):")
        for entity in result.get('key_entities', []):
            logger.info(f"  - {entity}")

        logger.info(f"\nFull Analysis:")
        logger.info(json.dumps(result.get('customer_info'), indent=2))

        return result

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise


async def main():
    """Main test function."""
    # Load environment variables
    load_dotenv()

    # Test URLs (you can modify these)
    test_urls = [
        "https://www.shopify.com",  # E-commerce platform
        # "https://www.salesforce.com",  # CRM/SaaS
        # "https://www.airbnb.com",  # Marketplace
    ]

    for url in test_urls:
        logger.info(f"\n{'='*80}\n")
        logger.info(f"Testing with: {url}")
        logger.info(f"\n{'='*80}\n")

        try:
            await test_research_agent(url)
            logger.info("\n✅ Test passed!\n")
        except Exception as e:
            logger.error(f"\n❌ Test failed: {e}\n")

        # Small delay between tests
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
