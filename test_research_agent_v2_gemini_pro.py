"""
Test script for Research Agent V2 with Gemini 2.5 Pro.
Benchmarks Gemini 2.5 Pro vs Claude Sonnet 4.5 for research phase.
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
from backend.agentic_service.agents.research_agent_v2_gemini_pro import CustomerResearchAgentV2GeminiPro

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_claude_agent(url: str):
    """Test Claude Sonnet 4.5 agent."""
    print("\n" + "="*80)
    print("🐢 TESTING CLAUDE SONNET 4.5")
    print("="*80 + "\n")

    agent = CustomerResearchAgentV2Optimized()

    state = {
        "customer_url": url,
        "crazy_frog_context": ""
    }

    start_time = time.time()
    result_state = await agent.execute(state)
    elapsed = time.time() - start_time

    customer_info = result_state.get("customer_info", {})
    v2_intelligence = result_state.get("v2_intelligence", {})

    print(f"\n⏱️  CLAUDE SONNET 4.5: {elapsed:.2f} seconds")
    print(f"📊 Company: {customer_info.get('company_name', 'Unknown')}")
    print(f"   Industry: {customer_info.get('industry', 'Unknown')}")
    print(f"   Key Entities: {len(customer_info.get('key_entities', []))}")

    architecture = v2_intelligence.get("data_architecture", {})
    print(f"   Data Entities: {len(architecture.get('core_entities', []))}")

    return elapsed, customer_info, architecture


async def test_gemini_pro_agent(url: str):
    """Test Gemini 2.5 Pro agent."""
    print("\n" + "="*80)
    print("⚡ TESTING GEMINI 2.5 PRO")
    print("="*80 + "\n")

    agent = CustomerResearchAgentV2GeminiPro()

    state = {
        "customer_url": url,
        "crazy_frog_context": ""
    }

    start_time = time.time()
    result_state = await agent.execute(state)
    elapsed = time.time() - start_time

    customer_info = result_state.get("customer_info", {})
    v2_intelligence = result_state.get("v2_intelligence", {})

    print(f"\n⏱️  GEMINI 2.5 PRO: {elapsed:.2f} seconds")
    print(f"📊 Company: {customer_info.get('company_name', 'Unknown')}")
    print(f"   Industry: {customer_info.get('industry', 'Unknown')}")
    print(f"   Key Entities: {len(customer_info.get('key_entities', []))}")

    architecture = v2_intelligence.get("data_architecture", {})
    print(f"   Data Entities: {len(architecture.get('core_entities', []))}")

    return elapsed, customer_info, architecture


async def main():
    """Run both tests and compare."""
    # Test URL
    test_url = "https://www.offerup.com"

    print("\n" + "="*80)
    print(f"🔬 RESEARCH AGENT V2 BENCHMARK: Gemini 2.5 Pro vs Claude Sonnet 4.5")
    print(f"🌐 Test URL: {test_url}")
    print("="*80)

    try:
        # Test Gemini 2.5 Pro first
        gemini_time, gemini_info, gemini_arch = await test_gemini_pro_agent(test_url)

        # Test Claude (for comparison)
        claude_time, claude_info, claude_arch = await test_claude_agent(test_url)

        # Results
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS")
        print("="*80 + "\n")

        print(f"Claude Sonnet 4.5:  {claude_time:.2f}s → {len(claude_info.get('key_entities', []))} entities, {len(claude_arch.get('core_entities', []))} data entities")
        print(f"Gemini 2.5 Pro:     {gemini_time:.2f}s → {len(gemini_info.get('key_entities', []))} entities, {len(gemini_arch.get('core_entities', []))} data entities")
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
            "test_url": test_url,
            "claude_sonnet_45": {
                "time_seconds": claude_time,
                "company_name": claude_info.get("company_name", "Unknown"),
                "industry": claude_info.get("industry", "Unknown"),
                "key_entities": len(claude_info.get("key_entities", [])),
                "data_entities": len(claude_arch.get("core_entities", []))
            },
            "gemini_25_pro": {
                "time_seconds": gemini_time,
                "company_name": gemini_info.get("company_name", "Unknown"),
                "industry": gemini_info.get("industry", "Unknown"),
                "key_entities": len(gemini_info.get("key_entities", [])),
                "data_entities": len(gemini_arch.get("core_entities", []))
            },
            "comparison": {
                "faster_model": "Gemini 2.5 Pro" if gemini_time < claude_time else "Claude Sonnet 4.5",
                "speedup": claude_time / gemini_time if gemini_time > 0 else 0,
                "time_difference_seconds": abs(claude_time - gemini_time)
            }
        }

        with open("benchmarks/benchmark_research_v2_gemini_pro_vs_claude.json", "w") as f:
            json.dump(results, f, indent=2)

        print("📝 Results saved to: benchmarks/benchmark_research_v2_gemini_pro_vs_claude.json")
        print()

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
