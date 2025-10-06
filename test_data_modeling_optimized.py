"""
Test script for Data Modeling Agent Optimized.
Benchmarks Gemini 2.0 Flash vs Claude Sonnet 4.5 for schema generation.
"""
import asyncio
import logging
import time
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.agentic_service.agents.data_modeling_agent import DataModelingAgent
from backend.agentic_service.agents.data_modeling_agent_optimized import DataModelingAgentOptimized

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Sample demo story for testing
SAMPLE_DEMO_STORY = {
    "demo_title": "OfferUp Marketplace Analytics",
    "executive_summary": "Enable OfferUp to analyze marketplace performance through natural language",
    "golden_queries": [
        {
            "sequence": 1,
            "question": "What are our top 10 selling categories this month?",
            "expected_sql": "SELECT category, COUNT(*) as sales FROM listings GROUP BY category ORDER BY sales DESC LIMIT 10"
        },
        {
            "sequence": 2,
            "question": "Show me average listing price by category and location",
            "expected_sql": "SELECT category, location, AVG(price) FROM listings GROUP BY category, location"
        }
    ],
    "data_specs": {
        "key_entities": [
            {"entity_name": "users", "purpose": "Track user accounts"},
            {"entity_name": "listings", "purpose": "Track marketplace listings"},
            {"entity_name": "transactions", "purpose": "Track sales"}
        ]
    }
}

SAMPLE_CUSTOMER_INFO = {
    "company_name": "OfferUp",
    "industry": "E-commerce Marketplace",
    "business_domain": "C2C Marketplace",
    "key_entities": [
        {"name": "users", "description": "User accounts"},
        {"name": "listings", "description": "Product listings"},
        {"name": "transactions", "description": "Sales transactions"}
    ]
}


async def test_original_agent():
    """Test original Claude-based agent."""
    print("\n" + "="*80)
    print("🐢 TESTING ORIGINAL AGENT (Claude Sonnet 4.5)")
    print("="*80 + "\n")

    agent = DataModelingAgent()

    state = {
        "customer_info": SAMPLE_CUSTOMER_INFO,
        "demo_story": SAMPLE_DEMO_STORY,
        "crazy_frog_context": ""
    }

    start_time = time.time()
    result_state = await agent.execute(state)
    elapsed = time.time() - start_time

    schema = result_state.get("schema", {})
    tables = schema.get("tables", [])

    print(f"\n⏱️  ORIGINAL: {elapsed:.2f} seconds")
    print(f"📊 Tables Generated: {len(tables)}")
    if tables:
        print(f"   Sample: {tables[0].get('name')} ({len(tables[0].get('schema', []))} fields)")

    return elapsed, len(tables)


async def test_optimized_agent():
    """Test optimized Gemini-based agent."""
    print("\n" + "="*80)
    print("⚡ TESTING OPTIMIZED AGENT (Gemini 2.0 Flash)")
    print("="*80 + "\n")

    agent = DataModelingAgentOptimized()

    state = {
        "customer_info": SAMPLE_CUSTOMER_INFO,
        "demo_story": SAMPLE_DEMO_STORY,
        "crazy_frog_context": ""
    }

    start_time = time.time()
    result_state = await agent.execute(state)
    elapsed = time.time() - start_time

    schema = result_state.get("schema", {})
    tables = schema.get("tables", [])

    print(f"\n⏱️  OPTIMIZED: {elapsed:.2f} seconds")
    print(f"📊 Tables Generated: {len(tables)}")
    if tables:
        print(f"   Sample: {tables[0].get('name')} ({len(tables[0].get('schema', []))} fields)")

    return elapsed, len(tables)


async def main():
    """Run both tests and compare."""
    print("\n" + "="*80)
    print("🔬 DATA MODELING AGENT OPTIMIZATION BENCHMARK")
    print("="*80)

    try:
        # Test optimized first (faster)
        optimized_time, optimized_tables = await test_optimized_agent()

        # Test original (slower)
        original_time, original_tables = await test_original_agent()

        # Results
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS")
        print("="*80 + "\n")

        print(f"Original (Claude):  {original_time:.2f}s → {original_tables} tables")
        print(f"Optimized (Gemini): {optimized_time:.2f}s → {optimized_tables} tables")
        print()

        speedup = original_time / optimized_time if optimized_time > 0 else 0
        time_saved = original_time - optimized_time

        print(f"⚡ Speedup: {speedup:.2f}x faster")
        print(f"⏱️  Time Saved: {time_saved:.2f} seconds")

        if speedup >= 3:
            print(f"✅ SUCCESS - Achieved {speedup:.1f}x speedup (target: 3x)")
        elif speedup >= 2:
            print(f"⚠️  GOOD - Achieved {speedup:.1f}x speedup (target: 3x)")
        else:
            print(f"❌ NEEDS IMPROVEMENT - Only {speedup:.1f}x speedup")

        print()

        # Save results
        results = {
            "original": {
                "model": "Claude Sonnet 4.5",
                "time_seconds": original_time,
                "tables_generated": original_tables
            },
            "optimized": {
                "model": "Gemini 2.0 Flash",
                "time_seconds": optimized_time,
                "tables_generated": optimized_tables
            },
            "improvement": {
                "speedup": speedup,
                "time_saved_seconds": time_saved
            }
        }

        with open("benchmark_data_modeling.json", "w") as f:
            json.dump(results, f, indent=2)

        print("📝 Results saved to: benchmark_data_modeling.json")
        print()

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
