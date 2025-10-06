"""
Test script for CAPI Instruction Generator with Gemini 2.5 Pro.
Benchmarks Gemini 2.5 Pro vs Claude Sonnet 4.5 for YAML generation.
"""
import asyncio
import logging
import time
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.agentic_service.agents.capi_instruction_generator_optimized import CAPIInstructionGeneratorOptimized
from backend.agentic_service.agents.capi_instruction_generator_gemini_pro import CAPIInstructionGeneratorGeminiPro

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Sample schema for testing
SAMPLE_SCHEMA = {
    "tables": [
        {
            "name": "users",
            "description": "Platform users (buyers and sellers)",
            "columns": [
                {"name": "user_id", "type": "INT64", "description": "Unique user identifier"},
                {"name": "username", "type": "STRING", "description": "User's display name"},
                {"name": "email", "type": "STRING", "description": "User email address"},
                {"name": "created_at", "type": "TIMESTAMP", "description": "Account creation timestamp"},
                {"name": "user_type", "type": "STRING", "description": "User type (buyer, seller, both)"}
            ]
        },
        {
            "name": "listings",
            "description": "Item listings for sale",
            "columns": [
                {"name": "listing_id", "type": "INT64", "description": "Unique listing identifier"},
                {"name": "seller_id", "type": "INT64", "description": "User ID of seller"},
                {"name": "title", "type": "STRING", "description": "Listing title"},
                {"name": "description", "type": "STRING", "description": "Item description"},
                {"name": "price", "type": "FLOAT64", "description": "Listing price"},
                {"name": "category", "type": "STRING", "description": "Item category"},
                {"name": "created_at", "type": "TIMESTAMP", "description": "Listing creation timestamp"}
            ]
        },
        {
            "name": "transactions",
            "description": "Purchase transactions",
            "columns": [
                {"name": "transaction_id", "type": "INT64", "description": "Unique transaction identifier"},
                {"name": "listing_id", "type": "INT64", "description": "Listing purchased"},
                {"name": "buyer_id", "type": "INT64", "description": "User ID of buyer"},
                {"name": "seller_id", "type": "INT64", "description": "User ID of seller"},
                {"name": "amount", "type": "FLOAT64", "description": "Transaction amount"},
                {"name": "status", "type": "STRING", "description": "Transaction status"},
                {"name": "created_at", "type": "TIMESTAMP", "description": "Transaction timestamp"}
            ]
        }
    ]
}


# Sample demo story for testing
SAMPLE_DEMO_STORY = {
    "demo_title": "OfferUp: From Data Bottlenecks to Conversational Commerce Intelligence",
    "executive_summary": "See how OfferUp transforms marketplace analytics with natural language queries.",
    "business_challenges": [
        "Data access limited to technical teams",
        "Slow insights delay decision making",
        "Analytics bottleneck limits growth"
    ],
    "demo_narrative": {
        "story_arc": [
            {
                "scene_number": 1,
                "scene_title": "The Problem: Data Bottleneck",
                "duration_minutes": 2,
                "description": "Marketplace team struggles with data access"
            },
            {
                "scene_number": 2,
                "scene_title": "The Solution: CAPI in Action",
                "duration_minutes": 5,
                "description": "Natural language queries unlock insights"
            }
        ]
    },
    "golden_queries": [
        {
            "question": "What are our top-selling categories this month?",
            "complexity": "SIMPLE",
            "business_value": "Category performance insights"
        },
        {
            "question": "Show me the average transaction value by user segment",
            "complexity": "MEDIUM",
            "business_value": "Revenue analysis by segment"
        },
        {
            "question": "Which sellers have the highest buyer satisfaction scores?",
            "complexity": "MEDIUM",
            "business_value": "Seller quality metrics"
        }
    ],
    "data_model_requirements": {
        "key_entities": [
            {"name": "users", "description": "Platform users"},
            {"name": "listings", "description": "Item listings"},
            {"name": "transactions", "description": "Purchase transactions"}
        ]
    }
}


async def test_claude_agent():
    """Test Claude Sonnet 4.5 agent."""
    print("\n" + "="*80)
    print("🐢 TESTING CLAUDE SONNET 4.5")
    print("="*80 + "\n")

    agent = CAPIInstructionGeneratorOptimized()

    state = {
        "schema": SAMPLE_SCHEMA,
        "demo_story": SAMPLE_DEMO_STORY,
        "dataset_full_name": "bq-demos-469816.demo_offerup",
        "crazy_frog_context": "",
        "customer_info": {
            "company_name": "OfferUp"
        }
    }

    start_time = time.time()
    result_state = await agent.execute(state)
    elapsed = time.time() - start_time

    yaml_content = result_state.get("capi_system_instructions", "")
    yaml_summary = result_state.get("capi_yaml_summary", {})

    print(f"\n⏱️  CLAUDE SONNET 4.5: {elapsed:.2f} seconds")
    print(f"📊 YAML Size: {len(yaml_content):,} characters")
    print(f"   Lines: {yaml_summary.get('yaml_size_lines', 'N/A')}")
    print(f"   Tables: {yaml_summary.get('table_count', 'N/A')}")
    print(f"   Has Golden Queries: {yaml_summary.get('has_golden_queries', False)}")

    return elapsed, yaml_content, yaml_summary


async def test_gemini_pro_agent():
    """Test Gemini 2.5 Pro agent."""
    print("\n" + "="*80)
    print("⚡ TESTING GEMINI 2.5 PRO")
    print("="*80 + "\n")

    agent = CAPIInstructionGeneratorGeminiPro()

    state = {
        "schema": SAMPLE_SCHEMA,
        "demo_story": SAMPLE_DEMO_STORY,
        "dataset_full_name": "bq-demos-469816.demo_offerup",
        "crazy_frog_context": "",
        "customer_info": {
            "company_name": "OfferUp"
        }
    }

    start_time = time.time()
    result_state = await agent.execute(state)
    elapsed = time.time() - start_time

    yaml_content = result_state.get("capi_system_instructions", "")
    yaml_summary = result_state.get("capi_yaml_summary", {})

    print(f"\n⏱️  GEMINI 2.5 PRO: {elapsed:.2f} seconds")
    print(f"📊 YAML Size: {len(yaml_content):,} characters")
    print(f"   Lines: {yaml_summary.get('yaml_size_lines', 'N/A')}")
    print(f"   Tables: {yaml_summary.get('table_count', 'N/A')}")
    print(f"   Has Golden Queries: {yaml_summary.get('has_golden_queries', False)}")

    return elapsed, yaml_content, yaml_summary


async def main():
    """Run both tests and compare."""
    print("\n" + "="*80)
    print(f"🔬 CAPI INSTRUCTION GENERATOR BENCHMARK: Gemini 2.5 Pro vs Claude Sonnet 4.5")
    print(f"📋 Test Dataset: OfferUp (3 tables)")
    print("="*80)

    try:
        # Test Gemini 2.5 Pro first
        gemini_time, gemini_yaml, gemini_summary = await test_gemini_pro_agent()

        # Test Claude (for comparison)
        claude_time, claude_yaml, claude_summary = await test_claude_agent()

        # Results
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS")
        print("="*80 + "\n")

        print(f"Claude Sonnet 4.5:  {claude_time:.2f}s → {len(claude_yaml):,} chars, {claude_summary.get('yaml_size_lines', 'N/A')} lines")
        print(f"Gemini 2.5 Pro:     {gemini_time:.2f}s → {len(gemini_yaml):,} chars, {gemini_summary.get('yaml_size_lines', 'N/A')} lines")
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
            "test_dataset": "OfferUp (3 tables)",
            "claude_sonnet_45": {
                "time_seconds": claude_time,
                "yaml_size_chars": len(claude_yaml),
                "yaml_size_lines": claude_summary.get("yaml_size_lines", 0),
                "table_count": claude_summary.get("table_count", 0),
                "has_golden_queries": claude_summary.get("has_golden_queries", False)
            },
            "gemini_25_pro": {
                "time_seconds": gemini_time,
                "yaml_size_chars": len(gemini_yaml),
                "yaml_size_lines": gemini_summary.get("yaml_size_lines", 0),
                "table_count": gemini_summary.get("table_count", 0),
                "has_golden_queries": gemini_summary.get("has_golden_queries", False)
            },
            "comparison": {
                "faster_model": "Gemini 2.5 Pro" if gemini_time < claude_time else "Claude Sonnet 4.5",
                "speedup": claude_time / gemini_time if gemini_time > 0 else 0,
                "time_difference_seconds": abs(claude_time - gemini_time)
            }
        }

        with open("benchmarks/benchmark_capi_instruction_gemini_pro_vs_claude.json", "w") as f:
            json.dump(results, f, indent=2)

        print("📝 Results saved to: benchmarks/benchmark_capi_instruction_gemini_pro_vs_claude.json")
        print()

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
