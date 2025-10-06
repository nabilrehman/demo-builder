#!/usr/bin/env python3
"""
Isolated Test Script for Research Agent V2.
Tests the enhanced research agent with multi-source intelligence gathering.
"""
import asyncio
import logging
import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.research_agent_v2 import CustomerResearchAgentV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_section(title: str, width: int = 80):
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


async def test_research_agent_v2(
    url: str,
    max_pages: int = 50,
    max_depth: int = 3,
    enable_blog: bool = True,
    enable_linkedin: bool = True,
    enable_youtube: bool = True,
    output_file: str = None
):
    """
    Test the V2 research agent.

    Args:
        url: Website URL to analyze
        max_pages: Maximum pages to crawl
        max_depth: Maximum crawl depth
        enable_blog: Enable blog scraping
        enable_linkedin: Enable LinkedIn scraping
        enable_youtube: Enable YouTube scraping
        output_file: Optional output JSON file path
    """
    print_section("🔍 RESEARCH AGENT V2 - ISOLATED TEST")

    logger.info(f"Testing Research Agent V2 with URL: {url}")
    logger.info(f"Configuration:")
    logger.info(f"  - Max Pages: {max_pages}")
    logger.info(f"  - Max Depth: {max_depth}")
    logger.info(f"  - Blog Scraping: {enable_blog}")
    logger.info(f"  - LinkedIn: {enable_linkedin}")
    logger.info(f"  - YouTube: {enable_youtube}")

    # Create initial state
    state = {
        "customer_url": url,
        "project_id": os.getenv("PROJECT_ID", "bq-demos-469816"),
        "job_id": "test-v2-001",
        "crazy_frog_context": ""  # No crazy frog for basic test
    }

    # Initialize V2 agent
    print_subsection("Initializing Agent V2")
    agent = CustomerResearchAgentV2(
        max_pages=max_pages,
        max_depth=max_depth,
        enable_blog=enable_blog,
        enable_linkedin=enable_linkedin,
        enable_youtube=enable_youtube
    )

    # Execute research
    start_time = datetime.now()

    try:
        print_subsection("Executing V2 Research")
        result = await agent.execute(state)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Display results
        print_section("📊 RESEARCH RESULTS")

        # Business Analysis
        print_subsection("Business Analysis")
        customer_info = result.get('customer_info', {})
        print(f"Company Name:     {customer_info.get('company_name', 'N/A')}")
        print(f"Industry:         {customer_info.get('industry', 'N/A')}")
        print(f"Business Domain:  {customer_info.get('business_domain', 'N/A')}")
        print(f"Company Type:     {customer_info.get('company_type', 'N/A')}")
        print(f"Business Model:   {customer_info.get('business_model', 'N/A')}")

        # Key Entities
        print_subsection("Key Business Entities")
        entities = customer_info.get('key_entities', [])
        print(f"Total Entities Identified: {len(entities)}")
        for i, entity in enumerate(entities[:10], 1):
            if isinstance(entity, dict):
                print(f"  {i}. {entity.get('name', 'Unknown')}: {entity.get('description', '')}")
            else:
                print(f"  {i}. {entity}")
        if len(entities) > 10:
            print(f"  ... and {len(entities) - 10} more")

        # Data Products
        data_products = customer_info.get('data_products', [])
        if data_products:
            print_subsection("Data Products Detected")
            for product in data_products:
                if isinstance(product, dict):
                    print(f"  • {product.get('name', 'Unknown')}: {product.get('description', '')}")
                else:
                    print(f"  • {product}")

        # Technologies
        technologies = customer_info.get('technologies_detected', [])
        if technologies:
            print_subsection("Technologies Detected")
            print(f"  {', '.join(technologies)}")

        # Primary Use Cases
        use_cases = customer_info.get('primary_use_cases', [])
        if use_cases:
            print_subsection("Primary Analytics Use Cases")
            for i, uc in enumerate(use_cases, 1):
                print(f"  {i}. {uc}")

        # V2-Specific Intelligence
        v2_intel = result.get('v2_intelligence', {})

        # Website Crawl Stats
        crawl_data = v2_intel.get('website_crawl', {})
        if crawl_data:
            print_subsection("Website Crawl Statistics")
            print(f"Pages Crawled:    {crawl_data.get('pages_crawled', 0)}")
            print(f"Total Words:      {crawl_data.get('total_content_words', 0):,}")
            categories = crawl_data.get('categories', {})
            if categories:
                print(f"Categories Found: {len(categories)}")
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    print(f"  • {cat}: {count} pages")

        # Blog Data
        blog_data = v2_intel.get('blog_data', {})
        if blog_data and blog_data.get('found'):
            print_subsection("Blog/News Intelligence")
            print(f"Blog URL:         {blog_data.get('blog_url', 'N/A')}")
            print(f"Articles Found:   {blog_data.get('articles_count', 0)}")
            techs = blog_data.get('technologies_mentioned', [])
            if techs:
                print(f"Technologies:     {', '.join(techs[:15])}")
                if len(techs) > 15:
                    print(f"                  ... and {len(techs) - 15} more")
            topics = blog_data.get('topics', [])
            if topics:
                print(f"Topics:           {', '.join(topics)}")

        # LinkedIn Data
        linkedin_data = v2_intel.get('linkedin_data', {})
        if linkedin_data and linkedin_data.get('found'):
            print_subsection("LinkedIn Intelligence")
            print(f"LinkedIn URL:     {linkedin_data.get('linkedin_url', 'N/A')}")
            if linkedin_data.get('note'):
                print(f"Note:             {linkedin_data['note']}")

        # YouTube Data
        youtube_data = v2_intel.get('youtube_data', {})
        if youtube_data and youtube_data.get('found'):
            print_subsection("YouTube Intelligence")
            print(f"YouTube URL:      {youtube_data.get('youtube_url', 'N/A')}")
            print(f"Videos Found:     {youtube_data.get('videos_count', 0)}")
            if youtube_data.get('note'):
                print(f"Note:             {youtube_data['note']}")

        # Data Architecture Inference
        architecture = v2_intel.get('data_architecture', {})
        if architecture and not architecture.get('error'):
            print_subsection("🏗️  Data Architecture Inference")

            # Core Entities
            core_entities = architecture.get('core_entities', [])
            print(f"Core Database Entities: {len(core_entities)}")
            for i, entity in enumerate(core_entities[:8], 1):
                name = entity.get('table_name', 'unknown')
                desc = entity.get('description', '')
                rows = entity.get('estimated_rows', 'N/A')
                print(f"  {i}. {name} ({rows} rows)")
                print(f"     {desc}")
                print(f"     Type: {entity.get('entity_type', 'N/A')}, "
                      f"Update: {entity.get('update_frequency', 'N/A')}")
            if len(core_entities) > 8:
                print(f"  ... and {len(core_entities) - 8} more entities")

            # Warehouse Design
            warehouse = architecture.get('warehouse_design', {})
            if warehouse:
                print(f"\nWarehouse Architecture: {warehouse.get('architecture_pattern', 'N/A')}")
                fact_tables = warehouse.get('fact_tables', [])
                dim_tables = warehouse.get('dimension_tables', [])
                print(f"  • Fact Tables: {len(fact_tables)}")
                for fact in fact_tables[:3]:
                    print(f"    - {fact.get('name', 'unknown')}: {fact.get('grain', '')}")
                print(f"  • Dimension Tables: {len(dim_tables)}")
                for dim in dim_tables[:3]:
                    print(f"    - {dim.get('name', 'unknown')} ({dim.get('type', 'SCD Type 1')})")

            # Tech Stack
            tech_stack = architecture.get('tech_stack', {})
            if tech_stack:
                print("\nInferred Technology Stack:")
                dw = tech_stack.get('data_warehouse', {})
                if dw:
                    print(f"  • Data Warehouse: {dw.get('platform', 'N/A')}")
                    print(f"    Rationale: {dw.get('rationale', 'N/A')}")

                cloud = tech_stack.get('cloud_provider', {})
                if cloud:
                    print(f"  • Cloud Provider: {cloud.get('primary', 'N/A')}")

                streaming = tech_stack.get('streaming', {})
                if streaming and streaming.get('platform') != 'None':
                    print(f"  • Streaming: {streaming.get('platform', 'N/A')}")

            # Scale Estimates
            scale = architecture.get('scale_estimates', {})
            if scale:
                print("\nScale Estimates:")
                print(f"  • Daily Data Volume: {scale.get('daily_data_volume_gb', 'N/A')} GB")
                print(f"  • Warehouse Size: {scale.get('total_warehouse_size_tb', 'N/A')} TB")
                print(f"  • Concurrent Users: {scale.get('concurrent_users', 'N/A')}")

        # Summary
        print_section("⏱️  EXECUTION SUMMARY")
        print(f"Total Execution Time: {duration:.2f} seconds")
        print(f"Status: ✅ SUCCESS")

        # Save to file if requested
        if output_file:
            output_data = {
                'metadata': {
                    'test_url': url,
                    'timestamp': datetime.now().isoformat(),
                    'duration_seconds': duration,
                    'configuration': {
                        'max_pages': max_pages,
                        'max_depth': max_depth,
                        'enable_blog': enable_blog,
                        'enable_linkedin': enable_linkedin,
                        'enable_youtube': enable_youtube
                    }
                },
                'business_analysis': customer_info,
                'v2_intelligence': v2_intel
            }

            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            print(f"\n📄 Results saved to: {output_file}")

        return result

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        print_section("❌ TEST FAILED")
        print(f"Error: {str(e)}")
        raise


async def main():
    """Main test function."""
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test Research Agent V2')
    parser.add_argument('--url', type=str, help='Website URL to analyze')
    parser.add_argument('--max-pages', type=int, default=50, help='Maximum pages to crawl')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum crawl depth')
    parser.add_argument('--no-blog', action='store_true', help='Disable blog scraping')
    parser.add_argument('--no-linkedin', action='store_true', help='Disable LinkedIn scraping')
    parser.add_argument('--no-youtube', action='store_true', help='Disable YouTube scraping')
    parser.add_argument('--output', type=str, help='Output JSON file path')

    args = parser.parse_args()

    # Determine URL to test
    test_url = args.url

    if not test_url:
        # Default test URLs
        test_urls = [
            "https://www.nike.com",
            # "https://www.shopify.com",
            # "https://www.airbnb.com",
        ]
        test_url = test_urls[0]
        print(f"No URL provided, using default: {test_url}")

    # Generate output filename if not provided
    output_file = args.output
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = test_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].replace('.', '_')
        output_file = f"research_v2_results_{domain}_{timestamp}.json"

    try:
        await test_research_agent_v2(
            url=test_url,
            max_pages=args.max_pages,
            max_depth=args.max_depth,
            enable_blog=not args.no_blog,
            enable_linkedin=not args.no_linkedin,
            enable_youtube=not args.no_youtube,
            output_file=output_file
        )
        print("\n✅ Test completed successfully!\n")

    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
