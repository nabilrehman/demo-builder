#!/usr/bin/env python3
"""
Test Research Agent V2 with Gemini 2.5 Pro via Vertex AI.
Comparison test against Claude Sonnet 4.5.
"""
import asyncio
import sys
import os
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_service.agents.research_agent_v2 import CustomerResearchAgentV2
from agentic_service.utils.vertex_llm_client import get_gemini_pro_vertex_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_research_agent_gemini(
    url: str,
    max_pages: int = 30,
    max_depth: int = 3,
    output_file: str = None
):
    """
    Test Research Agent V2 with Gemini 2.5 Pro.

    Args:
        url: URL to research
        max_pages: Maximum pages to crawl
        max_depth: Maximum crawl depth
        output_file: Optional output file for results
    """
    logger.info("=" * 80)
    logger.info("  🔍 RESEARCH AGENT V2 - GEMINI 2.5 PRO TEST")
    logger.info("=" * 80)
    logger.info("")

    logger.info(f"Testing Research Agent V2 with URL: {url}")
    logger.info(f"Configuration:")
    logger.info(f"  - Model: Gemini 2.5 Pro (Vertex AI)")
    logger.info(f"  - Max Pages: {max_pages}")
    logger.info(f"  - Max Depth: {max_depth}")
    logger.info(f"  - Blog Scraping: True")
    logger.info(f"  - LinkedIn: True")
    logger.info(f"  - YouTube: True")

    # Initialize Research Agent V2 with Gemini
    logger.info("")
    logger.info("─" * 60)
    logger.info("  Initializing Agent V2 with Gemini 2.5 Pro")
    logger.info("─" * 60)

    # Create Gemini client
    gemini_client = get_gemini_pro_vertex_client()

    # Create agent with Gemini client
    agent = CustomerResearchAgentV2(
        max_pages=max_pages,
        max_depth=max_depth,
        enable_blog=True,
        enable_linkedin=True,
        enable_youtube=True,
        enable_jobs=True,
        enable_google_jobs=True
    )

    # Override the default Claude client with Gemini
    agent.client = gemini_client
    agent.data_architect.llm_client = gemini_client

    # Execute research
    logger.info("")
    logger.info("─" * 60)
    logger.info("  Executing V2 Research with Gemini")
    logger.info("─" * 60)

    start_time = datetime.now()

    state = {
        "customer_url": url
    }

    result_state = await agent.execute(state)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Print results
    logger.info("")
    logger.info("=" * 80)
    logger.info("  📊 RESEARCH RESULTS (GEMINI 2.5 PRO)")
    logger.info("=" * 80)
    logger.info("")

    business_info = result_state.get("customer_info", {})

    logger.info("─" * 60)
    logger.info("  Business Analysis")
    logger.info("─" * 60)
    logger.info(f"Company Name:     {business_info.get('company_name', 'N/A')}")
    logger.info(f"Industry:         {business_info.get('industry', 'N/A')}")
    logger.info(f"Business Domain:  {business_info.get('business_domain', 'N/A')}")
    logger.info(f"Company Type:     {business_info.get('company_type', 'N/A')}")
    logger.info(f"Business Model:   {business_info.get('business_model', 'N/A')}")

    logger.info("")
    logger.info("─" * 60)
    logger.info("  Key Business Entities")
    logger.info("─" * 60)
    entities = business_info.get('key_entities', [])
    logger.info(f"Total Entities Identified: {len(entities)}")
    for i, entity in enumerate(entities[:8], 1):
        if isinstance(entity, dict):
            logger.info(f"  {i}. {entity.get('name', 'N/A')}: {entity.get('description', 'N/A')}")
        else:
            logger.info(f"  {i}. {entity}")

    logger.info("")
    logger.info("─" * 60)
    logger.info("  Data Products Detected")
    logger.info("─" * 60)
    data_products = business_info.get('data_products', [])
    for product in data_products[:3]:
        if isinstance(product, dict):
            logger.info(f"  • {product.get('name', 'N/A')}: {product.get('description', 'N/A')}")

    logger.info("")
    logger.info("─" * 60)
    logger.info("  Technologies Detected")
    logger.info("─" * 60)
    techs = business_info.get('technologies_detected', [])
    logger.info(f"  {', '.join(techs) if techs else 'None detected'}")

    logger.info("")
    logger.info("─" * 60)
    logger.info("  Primary Analytics Use Cases")
    logger.info("─" * 60)
    use_cases = business_info.get('primary_use_cases', [])
    for i, use_case in enumerate(use_cases[:9], 1):
        logger.info(f"  {i}. {use_case}")

    logger.info("")
    logger.info("─" * 60)
    logger.info("  Website Crawl Statistics")
    logger.info("─" * 60)
    v2_intel = result_state.get("v2_intelligence", {})
    crawl_data = v2_intel.get("website_crawl", {})
    logger.info(f"Pages Crawled:    {crawl_data.get('pages_crawled', 0)}")
    logger.info(f"Total Words:      {crawl_data.get('total_content_words', 0):,}")
    logger.info(f"Categories Found: {len(crawl_data.get('categories', {}))}")
    for cat, count in crawl_data.get('categories', {}).items():
        logger.info(f"  • {cat}: {count} pages")

    logger.info("")
    logger.info("=" * 80)
    logger.info("  ⏱️  EXECUTION SUMMARY (GEMINI 2.5 PRO)")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Total Execution Time: {duration:.2f} seconds")
    logger.info(f"Status: ✅ SUCCESS")

    # Save results if output file specified
    if output_file:
        output_data = {
            "metadata": {
                "test_url": url,
                "model": "gemini-2.5-pro",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "configuration": {
                    "max_pages": max_pages,
                    "max_depth": max_depth,
                    "enable_blog": True,
                    "enable_linkedin": True,
                    "enable_youtube": True
                }
            },
            "business_analysis": business_info,
            "v2_intelligence": v2_intel
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"\n📄 Results saved to: {output_file}")

    logger.info("")
    logger.info("✅ Gemini test completed successfully!")

    return duration, result_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Research Agent V2 with Gemini 2.5 Pro")
    parser.add_argument("--url", required=True, help="URL to research")
    parser.add_argument("--max-pages", type=int, default=30, help="Maximum pages to crawl")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum crawl depth")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()

    asyncio.run(test_research_agent_gemini(
        args.url,
        args.max_pages,
        args.max_depth,
        args.output
    ))
