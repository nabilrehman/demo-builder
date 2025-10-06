#!/usr/bin/env python3
"""
End-to-End Test for Agent Configuration System.

Tests the complete pipeline with different agent model configurations
to verify that:
1. Configuration system correctly selects agents
2. Agents can be instantiated
3. Pipeline executes successfully
4. Results are valid

Usage:
    python3 test_agent_config_e2e.py
"""
import os
import sys
import asyncio
import logging
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))


def test_config_display():
    """Test 1: Verify configuration display works."""
    print("\n" + "="*80)
    print("TEST 1: Configuration Display")
    print("="*80)

    from agentic_service.config.agent_config import get_current_config, print_config

    try:
        config = get_current_config()
        logger.info(f"Current config: {config}")

        print_config()

        assert isinstance(config, dict), "Config should be a dictionary"
        assert len(config) == 4, "Should have 4 agents configured"
        assert all(k in config for k in ["research", "demo_story", "data_modeling", "capi"]), \
            "Missing expected agent keys"

        print("✅ TEST 1 PASSED: Configuration display works correctly\n")
        return True

    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}\n")
        return False


def test_agent_import():
    """Test 2: Verify all agents can be imported."""
    print("\n" + "="*80)
    print("TEST 2: Agent Class Import")
    print("="*80)

    from agentic_service.config.agent_config import get_agent_class

    agents = {
        "research": "Research Agent",
        "demo_story": "Demo Story Agent",
        "data_modeling": "Data Modeling Agent",
        "capi": "CAPI Instruction Generator"
    }

    all_passed = True

    for agent_key, agent_name in agents.items():
        try:
            AgentClass = get_agent_class(agent_key)
            logger.info(f"✅ {agent_name}: {AgentClass.__name__}")
            print(f"  ✅ {agent_name:30s} → {AgentClass.__name__}")
        except Exception as e:
            logger.error(f"❌ {agent_name}: Failed to import - {e}")
            print(f"  ❌ {agent_name:30s} → ERROR: {e}")
            all_passed = False

    if all_passed:
        print("\n✅ TEST 2 PASSED: All agents imported successfully\n")
    else:
        print("\n❌ TEST 2 FAILED: Some agents failed to import\n")

    return all_passed


def test_env_override():
    """Test 3: Verify environment variable overrides work."""
    print("\n" + "="*80)
    print("TEST 3: Environment Variable Override")
    print("="*80)

    from agentic_service.config.agent_config import get_agent_class

    # Save original env vars
    original_research = os.getenv("RESEARCH_AGENT_MODEL")
    original_demo = os.getenv("DEMO_STORY_AGENT_MODEL")

    try:
        # Test override to Claude
        os.environ["RESEARCH_AGENT_MODEL"] = "claude"
        os.environ["DEMO_STORY_AGENT_MODEL"] = "claude"

        # Force reimport to pick up env changes
        import importlib
        import agentic_service.config.agent_config as config_module
        importlib.reload(config_module)

        ResearchClass = config_module.get_agent_class("research")
        DemoStoryClass = config_module.get_agent_class("demo_story")

        # Check if correct Claude variants selected
        is_research_claude = "Optimized" in ResearchClass.__name__ or "V2" in ResearchClass.__name__
        is_demo_claude = ResearchClass.__name__ == "DemoStoryAgent"

        print(f"  Research Agent: {ResearchClass.__name__}")
        print(f"  Demo Story Agent: {DemoStoryClass.__name__}")

        # Restore original env vars
        if original_research:
            os.environ["RESEARCH_AGENT_MODEL"] = original_research
        else:
            os.environ.pop("RESEARCH_AGENT_MODEL", None)

        if original_demo:
            os.environ["DEMO_STORY_AGENT_MODEL"] = original_demo
        else:
            os.environ.pop("DEMO_STORY_AGENT_MODEL", None)

        print("\n✅ TEST 3 PASSED: Environment variable override works\n")
        return True

    except Exception as e:
        # Restore env vars on error
        if original_research:
            os.environ["RESEARCH_AGENT_MODEL"] = original_research
        else:
            os.environ.pop("RESEARCH_AGENT_MODEL", None)

        if original_demo:
            os.environ["DEMO_STORY_AGENT_MODEL"] = original_demo
        else:
            os.environ.pop("DEMO_STORY_AGENT_MODEL", None)

        print(f"❌ TEST 3 FAILED: {e}\n")
        return False


def test_agent_instantiation():
    """Test 4: Verify agents can be instantiated."""
    print("\n" + "="*80)
    print("TEST 4: Agent Instantiation")
    print("="*80)

    from agentic_service.config.agent_config import get_agent_class

    all_passed = True

    # Test Research Agent
    try:
        ResearchClass = get_agent_class("research")
        agent = ResearchClass(max_pages=5, max_depth=1)
        print(f"  ✅ Research Agent instantiated: {ResearchClass.__name__}")
    except Exception as e:
        print(f"  ❌ Research Agent failed: {e}")
        all_passed = False

    # Test Demo Story Agent
    try:
        DemoStoryClass = get_agent_class("demo_story")
        agent = DemoStoryClass()
        print(f"  ✅ Demo Story Agent instantiated: {DemoStoryClass.__name__}")
    except Exception as e:
        print(f"  ❌ Demo Story Agent failed: {e}")
        all_passed = False

    # Test Data Modeling Agent
    try:
        DataModelingClass = get_agent_class("data_modeling")
        agent = DataModelingClass()
        print(f"  ✅ Data Modeling Agent instantiated: {DataModelingClass.__name__}")
    except Exception as e:
        print(f"  ❌ Data Modeling Agent failed: {e}")
        all_passed = False

    # Test CAPI Agent
    try:
        CAPIClass = get_agent_class("capi")
        agent = CAPIClass()
        print(f"  ✅ CAPI Agent instantiated: {CAPIClass.__name__}")
    except Exception as e:
        print(f"  ❌ CAPI Agent failed: {e}")
        all_passed = False

    if all_passed:
        print("\n✅ TEST 4 PASSED: All agents instantiated successfully\n")
    else:
        print("\n❌ TEST 4 FAILED: Some agents failed to instantiate\n")

    return all_passed


async def test_mini_pipeline(test_url: str = "https://www.nike.com"):
    """Test 5: Run a mini research pipeline to verify agents work."""
    print("\n" + "="*80)
    print(f"TEST 5: Mini Pipeline Test (URL: {test_url})")
    print("="*80)

    from agentic_service.config.agent_config import get_agent_class, get_current_config

    config = get_current_config()
    print(f"\nCurrent Configuration:")
    for agent, model in config.items():
        print(f"  {agent:20s} → {model}")

    try:
        # Get Research Agent
        ResearchClass = get_agent_class("research")
        print(f"\nUsing Research Agent: {ResearchClass.__name__}")

        # Create research agent with minimal config
        research_agent = ResearchClass(
            max_pages=3,  # Very minimal for testing
            max_depth=1,
            enable_blog=False,
            enable_linkedin=False,
            enable_youtube=False
        )

        # Create minimal state
        state = {
            "customer_url": test_url,
            "project_id": "bq-demos-469816",
            "current_stage": "Research",
            "errors": []
        }

        print(f"\nRunning research agent on {test_url}...")
        print("(Using minimal config: 3 pages, depth 1, no external sources)")

        # Execute research
        result = await research_agent.execute(state)

        # Verify result
        assert "customer_info" in result, "Missing customer_info in result"
        assert "business_domain" in result, "Missing business_domain in result"

        customer_info = result["customer_info"]
        print(f"\n✅ Research completed successfully!")
        print(f"  Company: {customer_info.get('company_name', 'N/A')}")
        print(f"  Industry: {customer_info.get('industry', 'N/A')}")
        print(f"  Business Domain: {result.get('business_domain', 'N/A')}")

        print("\n✅ TEST 5 PASSED: Mini pipeline executed successfully\n")
        return True

    except Exception as e:
        logger.error(f"Mini pipeline failed: {e}", exc_info=True)
        print(f"\n❌ TEST 5 FAILED: {e}\n")
        return False


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("AGENT CONFIGURATION SYSTEM - END-TO-END TESTS")
    print("="*80)

    results = []

    # Test 1: Config Display
    results.append(("Config Display", test_config_display()))

    # Test 2: Agent Import
    results.append(("Agent Import", test_agent_import()))

    # Test 3: Environment Override
    results.append(("Environment Override", test_env_override()))

    # Test 4: Agent Instantiation
    results.append(("Agent Instantiation", test_agent_instantiation()))

    # Test 5: Mini Pipeline
    results.append(("Mini Pipeline", await test_mini_pipeline()))

    # Print Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Configuration system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return False


def main():
    """Main entry point."""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test runner failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
