"""
Fixture Loader - Load saved snapshots for testing agents in isolation.

This enables:
- Testing individual agents without running predecessors
- Fast iteration on agent fixes (30s vs 8-12min full pipeline)
- Regression testing with known-good states
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class FixtureLoader:
    """Load saved state snapshots for testing."""

    def __init__(self, snapshot_dir: str = "tests/fixtures/snapshots", template_dir: str = "tests/fixtures/templates"):
        self.snapshot_dir = Path(snapshot_dir)
        self.template_dir = Path(template_dir)

    def load_snapshot(self, snapshot_name: str, agent_output: str) -> Dict[str, Any]:
        """
        Load specific agent output from a snapshot.

        Args:
            snapshot_name: Name of the snapshot (e.g., "shopify_20251006")
            agent_output: Agent output to load (e.g., "04_synthetic_data")

        Returns:
            Dict with agent output state

        Example:
            >>> loader = FixtureLoader()
            >>> state = loader.load_snapshot("shopify_20251006", "04_synthetic_data")
            >>> # Now test Infrastructure Agent with this state
            >>> agent = InfrastructureAgent()
            >>> result = await agent.execute(state)
        """
        snapshot_path = self.snapshot_dir / snapshot_name / f"{agent_output}_output.json"

        if not snapshot_path.exists():
            raise FileNotFoundError(
                f"Snapshot not found: {snapshot_path}\n"
                f"Available snapshots: {self.list_snapshots()}\n"
                f"Available outputs for {snapshot_name}: {self.list_agent_outputs(snapshot_name)}"
            )

        with open(snapshot_path) as f:
            data = json.load(f)

        return data["state"]

    def load_template(self, template_name: str = "minimal_state") -> Dict[str, Any]:
        """
        Load a pre-built template for generic testing.

        Templates are hand-curated minimal states for fast testing.

        Args:
            template_name: Template to load (default: "minimal_state")

        Returns:
            Dict with template state
        """
        template_path = self.template_dir / f"{template_name}.json"

        if not template_path.exists():
            raise FileNotFoundError(
                f"Template not found: {template_path}\n"
                f"Available templates: {self.list_templates()}"
            )

        with open(template_path) as f:
            return json.load(f)

    def load_complete_job(self, snapshot_name: str) -> Dict[str, Any]:
        """Load complete job state (all agent outputs)."""
        job_path = self.snapshot_dir / snapshot_name / "complete_job_state.json"

        if not job_path.exists():
            raise FileNotFoundError(f"Job state not found: {job_path}")

        with open(job_path) as f:
            return json.load(f)

    def load_metadata(self, snapshot_name: str) -> Dict[str, Any]:
        """Load snapshot metadata."""
        metadata_path = self.snapshot_dir / snapshot_name / "metadata.json"

        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")

        with open(metadata_path) as f:
            return json.load(f)

    def list_snapshots(self) -> list:
        """List all available snapshots."""
        if not self.snapshot_dir.exists():
            return []

        return [d.name for d in self.snapshot_dir.iterdir() if d.is_dir()]

    def list_agent_outputs(self, snapshot_name: str) -> list:
        """List all agent outputs in a snapshot."""
        snapshot_path = self.snapshot_dir / snapshot_name

        if not snapshot_path.exists():
            return []

        return [
            f.stem.replace("_output", "")
            for f in snapshot_path.glob("*_output.json")
        ]

    def list_templates(self) -> list:
        """List all available templates."""
        if not self.template_dir.exists():
            return []

        return [f.stem for f in self.template_dir.glob("*.json")]

    def print_summary(self):
        """Print summary of available fixtures."""
        print("📦 Available Test Fixtures")
        print("\n📸 Snapshots:")
        for snapshot in self.list_snapshots():
            metadata = self.load_metadata(snapshot)
            print(f"  • {snapshot}")
            print(f"    - Customer: {metadata.get('customer_url', 'N/A')}")
            print(f"    - Dataset: {metadata.get('dataset_id', 'N/A')}")
            print(f"    - Agents: {', '.join(metadata.get('agents_captured', []))}")

        print("\n📋 Templates:")
        for template in self.list_templates():
            print(f"  • {template}")


# Convenience function for quick access
def load_fixture(snapshot_or_template: str, agent_output: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick fixture loading.

    Args:
        snapshot_or_template: Snapshot name or template name
        agent_output: Agent output (if loading snapshot)

    Examples:
        >>> load_fixture("minimal_state")  # Load template
        >>> load_fixture("shopify_20251006", "04_synthetic_data")  # Load snapshot
    """
    loader = FixtureLoader()

    if agent_output:
        return loader.load_snapshot(snapshot_or_template, agent_output)
    else:
        return loader.load_template(snapshot_or_template)
