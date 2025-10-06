"""
Example Test: Infrastructure Agent with Fixtures

This demonstrates how to test the Infrastructure Agent in isolation using
saved snapshots, without running the entire pipeline.

Benefits:
- Test in 30s instead of 8-12 minutes
- Reproducible tests with known inputs
- Fast iteration on bug fixes
"""
import pytest
import asyncio
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.utils.fixture_loader import FixtureLoader
from agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized


class TestInfrastructureAgentWithFixtures:
    """Test Infrastructure Agent using saved snapshots."""

    @pytest.fixture
    def fixture_loader(self):
        """Initialize fixture loader."""
        return FixtureLoader(
            snapshot_dir="tests/fixtures/snapshots",
            template_dir="tests/fixtures/templates"
        )

    @pytest.mark.asyncio
    async def test_infrastructure_with_synthetic_data_snapshot(self, fixture_loader):
        """
        Test Infrastructure Agent using output from Synthetic Data Generator.

        This loads the state after agent 04 (Synthetic Data Generator) completes,
        and tests that Infrastructure Agent can:
        1. Create BigQuery dataset
        2. Create tables
        3. Load data
        4. Create CAPI Data Agent successfully (THE FIX WE'RE TESTING!)
        """
        # Load state from snapshot (after Synthetic Data Generator)
        # Replace "nike_20251006" with actual snapshot name once captured
        state = fixture_loader.load_snapshot("nike_20251006", "04_synthetic_data")

        # Add test project context
        state["project_id"] = "bq-demos-469816"

        # Initialize Infrastructure Agent
        agent = InfrastructureAgentOptimized()

        # Execute the agent
        result = await agent.execute(state)

        # Assertions: Verify Infrastructure Agent succeeded
        assert result["bigquery_provisioned"] == True, "BigQuery should be provisioned"
        assert "dataset_id" in result, "Dataset ID should be set"
        assert "table_stats" in result, "Table stats should be returned"

        # CRITICAL: Verify CAPI agent was created (this was the bug!)
        assert result.get("capi_agent_id"), "CAPI agent ID should NOT be empty"
        assert result["capi_agent_created"] == True, "CAPI agent should be created"

        print(f"✅ Infrastructure Agent Test Passed!")
        print(f"   Dataset: {result['dataset_id']}")
        print(f"   Tables: {len(result['table_stats'])}")
        print(f"   CAPI Agent: {result['capi_agent_id']}")

    @pytest.mark.asyncio
    async def test_infrastructure_with_minimal_template(self, fixture_loader):
        """
        Test Infrastructure Agent with minimal template (fast test).

        This uses a hand-curated minimal state for quick sanity checks.
        """
        # Load minimal template
        state = fixture_loader.load_template("minimal_state")

        # Initialize Infrastructure Agent
        agent = InfrastructureAgentOptimized()

        # Execute the agent
        result = await agent.execute(state)

        # Basic assertions
        assert result["bigquery_provisioned"] == True
        assert result.get("capi_agent_id"), "CAPI agent should be created"

        print(f"✅ Minimal Template Test Passed!")
        print(f"   CAPI Agent: {result['capi_agent_id']}")

    def test_list_available_fixtures(self, fixture_loader):
        """Verify fixture loader can list available snapshots."""
        snapshots = fixture_loader.list_snapshots()
        templates = fixture_loader.list_templates()

        print(f"📸 Available Snapshots: {snapshots}")
        print(f"📋 Available Templates: {templates}")

        # If we have snapshots, verify structure
        if snapshots:
            snapshot_name = snapshots[0]
            agent_outputs = fixture_loader.list_agent_outputs(snapshot_name)
            print(f"   Agent outputs in {snapshot_name}: {agent_outputs}")


def main():
    """Run tests manually (without pytest)."""
    loader = FixtureLoader()

    # Show available fixtures
    loader.print_summary()

    # Run a quick test if fixtures exist
    snapshots = loader.list_snapshots()
    if snapshots:
        print(f"\n🧪 Running quick test with {snapshots[0]}...")

        test = TestInfrastructureAgentWithFixtures()
        asyncio.run(test.test_infrastructure_with_synthetic_data_snapshot(loader))
    else:
        print("\n⚠️  No snapshots available yet. Run a successful job and capture it:")
        print("   python -m tests.utils.snapshot_capture <job_id> --name nike_20251006")


if __name__ == "__main__":
    main()
