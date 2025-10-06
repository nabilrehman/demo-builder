"""
Test script for Data Modeling Agent with Gemini 2.5 Pro.
Benchmarks Gemini 2.5 Pro vs Claude Sonnet 4.5 for schema generation.
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
from backend.agentic_service.agents.data_modeling_agent_gemini_pro import DataModelingAgentGeminiPro

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
        },
        {
            "sequence": 3,
            "question": "Which users have the highest transaction volume?",
            "expected_sql": "SELECT user_id, COUNT(*) as transactions FROM transactions GROUP BY user_id ORDER BY transactions DESC"
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


async def test_claude_agent():
    """Test Claude Sonnet 4.5 agent."""
    print("\n" + "="*80)
    print("🐢 TESTING CLAUDE SONNET 4.5")
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

    print(f"\n⏱️  CLAUDE SONNET 4.5: {elapsed:.2f} seconds")
    print(f"📊 Tables Generated: {len(tables)}")
    if tables:
        print(f"   Sample: {tables[0].get('name')} ({len(tables[0].get('schema', []))} fields)")

    return elapsed, len(tables)


async def test_gemini_pro_agent():
    """Test Gemini 2.5 Pro agent."""
    print("\n" + "="*80)
    print("⚡ TESTING GEMINI 2.5 PRO")
    print("="*80 + "\n")

    agent = DataModelingAgentGeminiPro()

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

    print(f"\n⏱️  GEMINI 2.5 PRO: {elapsed:.2f} seconds")
    print(f"📊 Tables Generated: {len(tables)}")
    if tables:
        print(f"   Sample: {tables[0].get('name')} ({len(tables[0].get('schema', []))} fields)")

    return elapsed, len(tables)


async def main():
    """Run both tests and compare."""
    print("\n" + "="*80)
    print("🔬 DATA MODELING AGENT BENCHMARK: Gemini 2.5 Pro vs Claude Sonnet 4.5")
    print("="*80)

    try:
        # Test Gemini 2.5 Pro first
        gemini_time, gemini_tables = await test_gemini_pro_agent()

        # Test Claude (for comparison)
        claude_time, claude_tables = await test_claude_agent()

        # Results
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS")
        print("="*80 + "\n")

        print(f"Claude Sonnet 4.5:  {claude_time:.2f}s → {claude_tables} tables")
        print(f"Gemini 2.5 Pro:     {gemini_time:.2f}s → {gemini_tables} tables")
        print()

        # Calculate comparison
        if gemini_time < claude_time:
            speedup = claude_time / gemini_time
            time_saved = claude_time - gemini_time
            print(f"⚡ Gemini 2.5 Pro is {speedup:.2f}x faster")
            print(f"⏱️  Time Saved: {time_saved:.2f} seconds")
        else:
            slowdown = gemini_time / claude_time
            time_lost = gemini_time - claude_time
            print(f"🐢 Gemini 2.5 Pro is {slowdown:.2f}x slower")
            print(f"⏱️  Time Lost: {time_lost:.2f} seconds")

        print()

        # Determine winner
        if gemini_time < claude_time * 0.9:  # At least 10% faster
            print(f"✅ WINNER: Gemini 2.5 Pro")
        elif claude_time < gemini_time * 0.9:  # Claude at least 10% faster
            print(f"✅ WINNER: Claude Sonnet 4.5")
        else:
            print(f"🤝 TIE: Performance is similar")

        print()

        # Save results
        results = {
            "claude_sonnet_45": {
                "time_seconds": claude_time,
                "tables_generated": claude_tables
            },
            "gemini_25_pro": {
                "time_seconds": gemini_time,
                "tables_generated": gemini_tables
            },
            "comparison": {
                "faster_model": "Gemini 2.5 Pro" if gemini_time < claude_time else "Claude Sonnet 4.5",
                "speedup": claude_time / gemini_time if gemini_time > 0 else 0,
                "time_difference_seconds": abs(claude_time - gemini_time)
            }
        }

        with open("benchmark_gemini_pro_vs_claude.json", "w") as f:
            json.dump(results, f, indent=2)

        print("📝 Results saved to: benchmark_gemini_pro_vs_claude.json")
        print()

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
