#!/usr/bin/env python3
"""
Automated test suite for comparing Claude Sonnet 4.5 vs Gemini 2.5 Pro.
Tests both models on the same research task and validates results.
"""
import asyncio
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_service.agents.research_agent_v2 import CustomerResearchAgentV2
from agentic_service.utils.vertex_llm_client import (
    get_claude_vertex_client,
    get_gemini_pro_vertex_client
)


class ModelComparisonTest:
    """Test suite for comparing Claude and Gemini models."""

    def __init__(self, test_url: str, max_pages: int = 30, max_depth: int = 3):
        self.test_url = test_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.results = {}

    async def test_claude(self) -> Tuple[float, Dict]:
        """Test Claude Sonnet 4.5."""
        print("\n" + "="*80)
        print("  🧪 TESTING: Claude Sonnet 4.5")
        print("="*80 + "\n")

        start_time = time.time()

        # Create agent with Claude client
        agent = CustomerResearchAgentV2(
            max_pages=self.max_pages,
            max_depth=self.max_depth,
            enable_blog=True,
            enable_linkedin=True,
            enable_youtube=True,
            enable_jobs=True,
            enable_google_jobs=True
        )

        # Execute research
        state = {"customer_url": self.test_url}
        result_state = await agent.execute(state)

        duration = time.time() - start_time

        # Validate results
        validation = self._validate_results(result_state, "Claude")

        return duration, result_state, validation

    async def test_gemini(self) -> Tuple[float, Dict]:
        """Test Gemini 2.5 Pro."""
        print("\n" + "="*80)
        print("  🧪 TESTING: Gemini 2.5 Pro")
        print("="*80 + "\n")

        start_time = time.time()

        # Create Gemini client
        gemini_client = get_gemini_pro_vertex_client()

        # Create agent with Gemini client
        agent = CustomerResearchAgentV2(
            max_pages=self.max_pages,
            max_depth=self.max_depth,
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
        state = {"customer_url": self.test_url}
        result_state = await agent.execute(state)

        duration = time.time() - start_time

        # Validate results
        validation = self._validate_results(result_state, "Gemini")

        return duration, result_state, validation

    def _validate_results(self, result_state: Dict, model_name: str) -> Dict:
        """Validate research results."""
        validation = {
            "model": model_name,
            "passed": True,
            "checks": {}
        }

        # Check 1: Business info present
        business_info = result_state.get("customer_info", {})
        validation["checks"]["business_info"] = {
            "passed": bool(business_info.get("company_name")),
            "company_name": business_info.get("company_name"),
            "industry": business_info.get("industry")
        }

        # Check 2: Entities identified
        entities = business_info.get("key_entities", [])
        validation["checks"]["entities"] = {
            "passed": len(entities) > 0,
            "count": len(entities),
            "entities": [e.get("name") if isinstance(e, dict) else e for e in entities]
        }

        # Check 3: Data architecture generated
        v2_intel = result_state.get("v2_intelligence", {})
        architecture = v2_intel.get("data_architecture", {})

        # Handle both 'entities' and 'core_entities' keys
        arch_entities = architecture.get("entities", []) or architecture.get("core_entities", [])

        validation["checks"]["architecture"] = {
            "passed": len(arch_entities) > 0,
            "entities_count": len(arch_entities),
            "has_warehouse_design": bool(architecture.get("warehouse_design")),
            "has_tech_stack": bool(architecture.get("tech_stack")),
            "error": architecture.get("error")
        }

        # Check 4: Use cases identified
        use_cases = business_info.get("primary_use_cases", [])
        validation["checks"]["use_cases"] = {
            "passed": len(use_cases) > 0,
            "count": len(use_cases)
        }

        # Check 5: Website crawl completed
        crawl = v2_intel.get("website_crawl", {})
        validation["checks"]["crawl"] = {
            "passed": crawl.get("pages_crawled", 0) > 0,
            "pages_crawled": crawl.get("pages_crawled", 0)
        }

        # Overall pass/fail
        validation["passed"] = all(
            check.get("passed", False)
            for check in validation["checks"].values()
        )

        return validation

    def _compare_results(self, claude_duration: float, claude_validation: Dict,
                         gemini_duration: float, gemini_validation: Dict) -> Dict:
        """Compare results between models."""
        return {
            "performance": {
                "claude_duration": round(claude_duration, 2),
                "gemini_duration": round(gemini_duration, 2),
                "speedup": round(claude_duration / gemini_duration, 2),
                "time_saved": round(claude_duration - gemini_duration, 2),
                "percent_faster": round((1 - gemini_duration/claude_duration) * 100, 1)
            },
            "quality": {
                "claude_passed": claude_validation["passed"],
                "gemini_passed": gemini_validation["passed"],
                "claude_entities": claude_validation["checks"]["entities"]["count"],
                "gemini_entities": gemini_validation["checks"]["entities"]["count"],
                "claude_arch_entities": claude_validation["checks"]["architecture"]["entities_count"],
                "gemini_arch_entities": gemini_validation["checks"]["architecture"]["entities_count"]
            },
            "cost_estimate": {
                "claude_cost": 0.24,  # Estimated from previous runs
                "gemini_cost": 0.0048,  # Estimated from previous runs
                "cost_savings": 0.2352,
                "cost_ratio": "50x cheaper with Gemini"
            }
        }

    def _print_results(self, comparison: Dict, claude_validation: Dict,
                       gemini_validation: Dict):
        """Print formatted comparison results."""
        print("\n" + "="*80)
        print("  📊 TEST RESULTS")
        print("="*80 + "\n")

        # Performance
        perf = comparison["performance"]
        print("⏱️  PERFORMANCE:")
        print(f"  Claude:  {perf['claude_duration']}s")
        print(f"  Gemini:  {perf['gemini_duration']}s")
        print(f"  Speedup: {perf['speedup']}x ({perf['percent_faster']}% faster)")
        print(f"  Time saved: {perf['time_saved']}s")

        # Cost
        cost = comparison["cost_estimate"]
        print(f"\n💰 COST:")
        print(f"  Claude:  ${cost['claude_cost']}")
        print(f"  Gemini:  ${cost['gemini_cost']}")
        print(f"  Savings: ${cost['cost_savings']} ({cost['cost_ratio']})")

        # Quality
        quality = comparison["quality"]
        print(f"\n🎯 QUALITY:")
        print(f"  Claude validation: {'✅ PASS' if quality['claude_passed'] else '❌ FAIL'}")
        print(f"    - Business entities: {quality['claude_entities']}")
        print(f"    - Architecture entities: {quality['claude_arch_entities']}")
        print(f"  Gemini validation: {'✅ PASS' if quality['gemini_passed'] else '❌ FAIL'}")
        print(f"    - Business entities: {quality['gemini_entities']}")
        print(f"    - Architecture entities: {quality['gemini_arch_entities']}")

        # Detailed validation
        print(f"\n🔍 DETAILED VALIDATION:")
        for model_name, validation in [("Claude", claude_validation), ("Gemini", gemini_validation)]:
            print(f"\n  {model_name}:")
            for check_name, check_result in validation["checks"].items():
                status = "✅" if check_result.get("passed") else "❌"
                print(f"    {status} {check_name}: {check_result}")

        # Overall verdict
        print("\n" + "="*80)
        if claude_validation["passed"] and gemini_validation["passed"]:
            print("  ✅ OVERALL: ALL TESTS PASSED")
            print(f"  🏆 RECOMMENDATION: Use Gemini for {perf['speedup']}x speedup + 50x cost savings")
        elif claude_validation["passed"]:
            print("  ⚠️  OVERALL: Claude passed, Gemini failed")
            print("  🏆 RECOMMENDATION: Use Claude for reliability")
        elif gemini_validation["passed"]:
            print("  ⚠️  OVERALL: Gemini passed, Claude failed")
            print("  🏆 RECOMMENDATION: Investigate Claude issues")
        else:
            print("  ❌ OVERALL: BOTH MODELS FAILED")
        print("="*80 + "\n")

    async def run_comparison(self, save_results: bool = True):
        """Run full comparison test."""
        print("\n" + "="*80)
        print("  🚀 MODEL COMPARISON TEST")
        print("="*80)
        print(f"  Test URL: {self.test_url}")
        print(f"  Config: {self.max_pages} pages, depth {self.max_depth}")
        print("="*80 + "\n")

        # Test Claude
        claude_duration, claude_state, claude_validation = await self.test_claude()

        # Test Gemini
        gemini_duration, gemini_state, gemini_validation = await self.test_gemini()

        # Compare results
        comparison = self._compare_results(
            claude_duration, claude_validation,
            gemini_duration, gemini_validation
        )

        # Print results
        self._print_results(comparison, claude_validation, gemini_validation)

        # Save results
        if save_results:
            results = {
                "metadata": {
                    "test_url": self.test_url,
                    "timestamp": datetime.now().isoformat(),
                    "config": {
                        "max_pages": self.max_pages,
                        "max_depth": self.max_depth
                    }
                },
                "claude": {
                    "duration": claude_duration,
                    "validation": claude_validation,
                    "results": claude_state
                },
                "gemini": {
                    "duration": gemini_duration,
                    "validation": gemini_validation,
                    "results": gemini_state
                },
                "comparison": comparison
            }

            output_file = f"benchmarks/comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"📄 Full results saved to: {output_file}\n")

        return comparison, claude_validation, gemini_validation


async def main():
    """Run comparison test."""
    import argparse

    parser = argparse.ArgumentParser(description="Compare Claude vs Gemini models")
    parser.add_argument("--url", default="https://www.offerup.com", help="URL to test")
    parser.add_argument("--max-pages", type=int, default=30, help="Max pages to crawl")
    parser.add_argument("--max-depth", type=int, default=3, help="Max crawl depth")
    parser.add_argument("--no-save", action="store_true", help="Don't save results")

    args = parser.parse_args()

    test = ModelComparisonTest(
        test_url=args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth
    )

    comparison, claude_val, gemini_val = await test.run_comparison(
        save_results=not args.no_save
    )

    # Exit with appropriate code
    if claude_val["passed"] and gemini_val["passed"]:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed


if __name__ == "__main__":
    asyncio.run(main())
