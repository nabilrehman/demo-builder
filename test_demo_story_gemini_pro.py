"""
Test script for Demo Story Agent with Gemini 2.5 Pro.
Benchmarks Gemini 2.5 Pro vs Claude Sonnet 4.5 for demo story generation.
"""
import asyncio
import logging
import time
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.agentic_service.agents.demo_story_agent import DemoStoryAgent
from backend.agentic_service.agents.demo_story_agent_gemini_pro import DemoStoryAgentGeminiPro

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Sample customer info for testing
SAMPLE_CUSTOMER_INFO = {
    "company_name": "OfferUp",
    "industry": "Online Classifieds & Marketplace",
    "business_domain": "C2C Marketplace Platform",
    "company_type": "E-commerce",
    "business_model": "Peer-to-peer marketplace connecting buyers and sellers",
    "key_products_services": [
        "Mobile marketplace app",
        "Web platform",
        "Shipping services",
        "Payment processing"
    ],
    "target_customers": [
        "Individual sellers",
        "Small businesses",
        "Bargain hunters",
        "Local buyers"
    ],
    "key_entities": [
        {"name": "users", "description": "Platform users (buyers and sellers)"},
        {"name": "listings", "description": "Item listings for sale"},
        {"name": "transactions", "description": "Purchase transactions"},
        {"name": "messages", "description": "User-to-user messages"},
        {"name": "reviews", "description": "Buyer/seller reviews"}
    ],
    "value_proposition": "Safe, local buying and selling made easy"
}


async def test_claude_agent():
    """Test Claude Sonnet 4.5 agent."""
    print("\n" + "="*80)
    print("🐢 TESTING CLAUDE SONNET 4.5")
    print("="*80 + "\n")

    agent = DemoStoryAgent()

    state = {
        "customer_info": SAMPLE_CUSTOMER_INFO,
        "crazy_frog_context": ""
    }

    start_time = time.time()
    result_state = await agent.execute(state)
    elapsed = time.time() - start_time

    demo_story = result_state.get("demo_story", {})
    golden_queries = result_state.get("golden_queries", [])

    print(f"\n⏱️  CLAUDE SONNET 4.5: {elapsed:.2f} seconds")
    print(f"📊 Demo Title: {result_state.get('demo_title', 'N/A')}")
    print(f"   Golden Queries: {len(golden_queries)}")
    print(f"   Story Scenes: {len(demo_story.get('demo_narrative', {}).get('story_arc', []))}")
    print(f"   Data Entities: {len(demo_story.get('data_model_requirements', {}).get('key_entities', []))}")

    return elapsed, demo_story, golden_queries


async def test_gemini_pro_agent():
    """Test Gemini 2.5 Pro agent."""
    print("\n" + "="*80)
    print("⚡ TESTING GEMINI 2.5 PRO")
    print("="*80 + "\n")

    agent = DemoStoryAgentGeminiPro()

    state = {
        "customer_info": SAMPLE_CUSTOMER_INFO,
        "crazy_frog_context": ""
    }

    start_time = time.time()
    result_state = await agent.execute(state)
    elapsed = time.time() - start_time

    demo_story = result_state.get("demo_story", {})
    golden_queries = result_state.get("golden_queries", [])

    print(f"\n⏱️  GEMINI 2.5 PRO: {elapsed:.2f} seconds")
    print(f"📊 Demo Title: {result_state.get('demo_title', 'N/A')}")
    print(f"   Golden Queries: {len(golden_queries)}")
    print(f"   Story Scenes: {len(demo_story.get('demo_narrative', {}).get('story_arc', []))}")
    print(f"   Data Entities: {len(demo_story.get('data_model_requirements', {}).get('key_entities', []))}")

    return elapsed, demo_story, golden_queries


async def main():
    """Run both tests and compare."""
    print("\n" + "="*80)
    print(f"🔬 DEMO STORY AGENT BENCHMARK: Gemini 2.5 Pro vs Claude Sonnet 4.5")
    print(f"🏢 Test Company: {SAMPLE_CUSTOMER_INFO['company_name']}")
    print("="*80)

    try:
        # Test Gemini 2.5 Pro first
        gemini_time, gemini_story, gemini_queries = await test_gemini_pro_agent()

        # Test Claude (for comparison)
        claude_time, claude_story, claude_queries = await test_claude_agent()

        # Results
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS")
        print("="*80 + "\n")

        print(f"Claude Sonnet 4.5:  {claude_time:.2f}s → {len(claude_queries)} queries, {len(claude_story.get('demo_narrative', {}).get('story_arc', []))} scenes")
        print(f"Gemini 2.5 Pro:     {gemini_time:.2f}s → {len(gemini_queries)} queries, {len(gemini_story.get('demo_narrative', {}).get('story_arc', []))} scenes")
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
            "company": SAMPLE_CUSTOMER_INFO["company_name"],
            "claude_sonnet_45": {
                "time_seconds": claude_time,
                "golden_queries": len(claude_queries),
                "story_scenes": len(claude_story.get("demo_narrative", {}).get("story_arc", [])),
                "data_entities": len(claude_story.get("data_model_requirements", {}).get("key_entities", []))
            },
            "gemini_25_pro": {
                "time_seconds": gemini_time,
                "golden_queries": len(gemini_queries),
                "story_scenes": len(gemini_story.get("demo_narrative", {}).get("story_arc", [])),
                "data_entities": len(gemini_story.get("data_model_requirements", {}).get("key_entities", []))
            },
            "comparison": {
                "faster_model": "Gemini 2.5 Pro" if gemini_time < claude_time else "Claude Sonnet 4.5",
                "speedup": claude_time / gemini_time if gemini_time > 0 else 0,
                "time_difference_seconds": abs(claude_time - gemini_time)
            }
        }

        with open("benchmarks/benchmark_demo_story_gemini_pro_vs_claude.json", "w") as f:
            json.dump(results, f, indent=2)

        print("📝 Results saved to: benchmarks/benchmark_demo_story_gemini_pro_vs_claude.json")
        print()

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
