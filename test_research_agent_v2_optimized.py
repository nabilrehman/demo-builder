"""
Test script for Research Agent V2 Optimized.
Benchmarks performance against offerup.com.
"""
import asyncio
import logging
import time
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.agentic_service.agents.research_agent_v2_optimized import CustomerResearchAgentV2Optimized

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_research_agent_optimized():
    """Test the optimized research agent."""

    print("=" * 80)
    print("🚀 TESTING OPTIMIZED RESEARCH AGENT V2")
    print("=" * 80)
    print()

    # Test URL
    test_url = "https://www.offerup.com"

    # Initialize optimized agent
    agent = CustomerResearchAgentV2Optimized(
        max_pages=30,
        max_depth=3,
        max_concurrent=15,
        enable_blog=True,
        enable_linkedin=True,
        enable_youtube=True,
        enable_jobs=True,
        enable_google_jobs=True
    )

    # Create test state
    state = {
        'customer_url': test_url,
        'crazy_frog_context': ''
    }

    print(f"🎯 Target: {test_url}")
    print(f"⚙️  Configuration:")
    print(f"   • Max Pages: 30")
    print(f"   • Max Depth: 3")
    print(f"   • Max Concurrent: 15")
    print(f"   • All scrapers enabled")
    print()
    print("⏱️  Starting execution...")
    print()

    # Execute and time
    start_time = time.time()

    try:
        result_state = await agent.execute(state)

        elapsed_time = time.time() - start_time

        print()
        print("=" * 80)
        print("✅ EXECUTION COMPLETE")
        print("=" * 80)
        print()
        print(f"⏱️  Total Time: {elapsed_time:.2f} seconds")
        print()

        # Display results
        customer_info = result_state.get('customer_info', {})
        v2_intelligence = result_state.get('v2_intelligence', {})

        print("📊 RESULTS SUMMARY:")
        print("-" * 80)
        print()

        # Business Analysis
        print("🏢 BUSINESS ANALYSIS:")
        print(f"   • Industry: {customer_info.get('industry', 'N/A')}")
        print(f"   • Business Domain: {customer_info.get('business_domain', 'N/A')}")
        print(f"   • Company Description: {customer_info.get('company_description', 'N/A')[:100]}...")
        print(f"   • Key Entities: {len(customer_info.get('key_entities', []))} identified")
        print()

        # Intelligence Gathering Results
        print("🔍 INTELLIGENCE GATHERED:")

        # Website Crawl
        crawl_data = v2_intelligence.get('website_crawl', {})
        if crawl_data:
            print(f"   • Website Crawl:")
            print(f"     - Pages Crawled: {crawl_data.get('pages_crawled', 0)}")
            print(f"     - Categories: {', '.join(crawl_data.get('categories', {}).keys())}")
            print(f"     - Total Words: {crawl_data.get('total_content_words', 0):,}")

        # Blog Data
        blog_data = v2_intelligence.get('blog_data', {})
        if blog_data and blog_data.get('found'):
            print(f"   • Blog:")
            print(f"     - Articles Found: {blog_data.get('articles_count', 0)}")
            print(f"     - Technologies: {', '.join(blog_data.get('technologies_mentioned', [])[:5])}")

        # LinkedIn Data
        linkedin_data = v2_intelligence.get('linkedin_data', {})
        if linkedin_data and linkedin_data.get('found'):
            print(f"   • LinkedIn:")
            print(f"     - URL: {linkedin_data.get('linkedin_url', 'N/A')}")

        # YouTube Data
        youtube_data = v2_intelligence.get('youtube_data', {})
        if youtube_data and youtube_data.get('found'):
            print(f"   • YouTube:")
            print(f"     - URL: {youtube_data.get('youtube_url', 'N/A')}")
            print(f"     - Videos: {youtube_data.get('videos_count', 0)}")

        # Jobs Data
        jobs_data = v2_intelligence.get('jobs_data', {})
        if jobs_data and jobs_data.get('found'):
            print(f"   • Jobs:")
            print(f"     - Total Jobs: {jobs_data.get('total_jobs_found', 0)}")
            print(f"     - Data Jobs: {jobs_data.get('data_jobs_count', 0)}")
            tech_stack = jobs_data.get('tech_stack_detected', {})
            if tech_stack:
                print(f"     - Tech Stack Categories: {', '.join(tech_stack.keys())}")

        # Data Architecture
        architecture = v2_intelligence.get('data_architecture', {})
        if architecture:
            print(f"   • Data Architecture:")
            print(f"     - Core Entities: {len(architecture.get('core_entities', []))}")
            warehouse = architecture.get('warehouse_design', {})
            if warehouse:
                print(f"     - Fact Tables: {len(warehouse.get('fact_tables', []))}")
                print(f"     - Dimension Tables: {len(warehouse.get('dimension_tables', []))}")

        print()
        print("=" * 80)
        print("⚡ PERFORMANCE ANALYSIS")
        print("=" * 80)
        print()
        print(f"🎯 Target Time: < 30 seconds")
        print(f"⏱️  Actual Time: {elapsed_time:.2f} seconds")

        if elapsed_time < 30:
            print(f"✅ SUCCESS - {((300 - elapsed_time) / 300 * 100):.1f}% faster than original (5 min)")
            speedup = 300 / elapsed_time
            print(f"⚡ Speedup: {speedup:.1f}x faster")
        elif elapsed_time < 60:
            print(f"⚠️  GOOD - Still 5x faster than original, but above 30s target")
        else:
            print(f"❌ NEEDS IMPROVEMENT - Still slower than target")

        print()

        # Save results to file
        output_file = "test_results_research_agent_v2_optimized.json"
        with open(output_file, 'w') as f:
            json.dump({
                'execution_time_seconds': elapsed_time,
                'target_url': test_url,
                'customer_info': customer_info,
                'v2_intelligence': {
                    'website_crawl_summary': {
                        'pages_crawled': crawl_data.get('pages_crawled', 0) if crawl_data else 0,
                        'categories': list(crawl_data.get('categories', {}).keys()) if crawl_data else [],
                        'total_words': crawl_data.get('total_content_words', 0) if crawl_data else 0
                    },
                    'blog_found': blog_data.get('found', False) if blog_data else False,
                    'linkedin_found': linkedin_data.get('found', False) if linkedin_data else False,
                    'youtube_found': youtube_data.get('found', False) if youtube_data else False,
                    'jobs_found': jobs_data.get('found', False) if jobs_data else False,
                    'jobs_count': jobs_data.get('total_jobs_found', 0) if jobs_data else 0,
                    'architecture_entities': len(architecture.get('core_entities', [])) if architecture else 0
                }
            }, f, indent=2)

        print(f"📝 Full results saved to: {output_file}")
        print()

        return elapsed_time, result_state

    except Exception as e:
        elapsed_time = time.time() - start_time
        print()
        print("=" * 80)
        print("❌ EXECUTION FAILED")
        print("=" * 80)
        print()
        print(f"⏱️  Time before failure: {elapsed_time:.2f} seconds")
        print(f"❌ Error: {str(e)}")
        print()
        logger.error(f"Test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(test_research_agent_optimized())
