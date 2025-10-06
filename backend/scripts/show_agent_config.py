#!/usr/bin/env python3
"""
Agent Configuration Display Script.

Shows the current agent model configuration (Gemini vs Claude)
for each agent in the pipeline.

Usage:
    python3 scripts/show_agent_config.py

    # Or with specific env file
    source backend/local.env && python3 scripts/show_agent_config.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentic_service.config.agent_config import (
    print_config,
    get_current_config,
    BENCHMARK_RESULTS,
)


def show_detailed_config():
    """Show detailed configuration with benchmark info."""
    config = get_current_config()

    print("\n" + "="*80)
    print("AGENT MODEL CONFIGURATION - DETAILED VIEW")
    print("="*80)

    for agent, model in config.items():
        env_var = f"{agent.upper()}_AGENT_MODEL"
        env_value = os.getenv(env_var)

        # Header
        print(f"\n🤖 {agent.upper().replace('_', ' ')} AGENT")
        print("-" * 80)

        # Current selection
        if env_value:
            print(f"   Selected Model: {model.upper()} (from ${env_var})")
        else:
            print(f"   Selected Model: {model.upper()} (default)")

        # Benchmark info
        if agent in BENCHMARK_RESULTS:
            benchmark = BENCHMARK_RESULTS[agent]

            # Show info for selected model
            if model in benchmark:
                model_info = benchmark[model]

                if "time_seconds" in model_info:
                    print(f"   ⏱️  Time: {model_info['time_seconds']:.1f}s")

                if "speedup" in model_info:
                    print(f"   ⚡ Speedup: {model_info['speedup']}")

                if "pros" in model_info:
                    print(f"   ✅ Pros: {', '.join(model_info['pros'])}")

                if "cons" in model_info:
                    print(f"   ⚠️  Cons: {', '.join(model_info['cons'])}")

            # Show recommendation
            if "recommendation" in benchmark:
                print(f"   💡 Recommendation: {benchmark['recommendation']}")

            # Show benchmark file
            if "benchmark_file" in benchmark:
                print(f"   📊 Benchmark: {benchmark['benchmark_file']}")

    print("\n" + "="*80)
    print("CONFIGURATION SUMMARY")
    print("="*80)

    # Count models
    gemini_count = sum(1 for m in config.values() if m == "gemini")
    claude_count = sum(1 for m in config.values() if m == "claude")

    print(f"   Gemini Agents: {gemini_count}/4")
    print(f"   Claude Agents: {claude_count}/4")

    # Estimate pipeline speed
    if gemini_count >= 3:
        print(f"   🚀 Pipeline Mode: SPEED (estimated ~3-4 minutes)")
    elif claude_count >= 3:
        print(f"   🎯 Pipeline Mode: QUALITY (estimated ~5-6 minutes)")
    else:
        print(f"   ⚖️  Pipeline Mode: BALANCED (estimated ~4-5 minutes)")

    print("="*80)

    # Show how to change
    print("\n💡 TO CHANGE CONFIGURATION:")
    print("   export RESEARCH_AGENT_MODEL=<gemini|claude>")
    print("   export DEMO_STORY_AGENT_MODEL=<gemini|claude>")
    print("   export DATA_MODELING_AGENT_MODEL=<gemini|claude>")
    print("   export CAPI_AGENT_MODEL=<gemini|claude>")
    print("\n   Or update backend/.env file")
    print("="*80 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Show agent model configuration"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed configuration with benchmark info"
    )

    args = parser.parse_args()

    if args.detailed:
        show_detailed_config()
    else:
        print_config()


if __name__ == "__main__":
    main()
