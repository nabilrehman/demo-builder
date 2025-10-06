"""
Snapshot Capture Tool - Save agent outputs from completed jobs as test fixtures.

This enables:
- Testing individual agents in isolation
- Skipping expensive agent execution during development
- Regression testing with known-good outputs
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import sys

# Add parent directory to path to import from agentic_service
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_service.utils.job_state_manager import get_job_manager


class SnapshotCapture:
    """Capture and save job state snapshots for testing."""

    def __init__(self, snapshot_dir: str = "tests/fixtures/snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def capture_job_snapshot(self, job_id: str, snapshot_name: str = None) -> Dict[str, Any]:
        """
        Capture complete job state and save as snapshot.

        Args:
            job_id: Job ID to capture
            snapshot_name: Optional name (defaults to company name from job)

        Returns:
            Dict with snapshot metadata
        """
        # Try to get job from API endpoint (works for completed jobs)
        import requests
        try:
            response = requests.get(f"http://localhost:8000/api/provision/status/{job_id}")
            if response.ok:
                job_data = response.json()
                # Convert API response to job-like object
                class JobFromAPI:
                    def __init__(self, data):
                        self.customer_url = data.get("customer_url", "")
                        self.status = data.get("status", "")
                        self._data = data

                    def to_dict(self):
                        return self._data

                job = JobFromAPI(job_data)
            else:
                raise ValueError(f"Job {job_id} not found via API")
        except Exception as api_error:
            # Fallback to JobStateManager (for running jobs)
            job_manager = get_job_manager()
            job = job_manager.get_job(job_id)

            if not job:
                raise ValueError(f"Job {job_id} not found in memory or via API: {api_error}")

        # Generate snapshot name from customer_url or use provided name
        if not snapshot_name:
            # Extract company name from URL or use timestamp
            url = job.customer_url
            company = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].split('.')[0]
            snapshot_name = f"{company}_{datetime.now().strftime('%Y%m%d')}"

        # Create snapshot directory
        snapshot_path = self.snapshot_dir / snapshot_name
        snapshot_path.mkdir(parents=True, exist_ok=True)

        # Convert job to dict
        job_data = job.to_dict()

        # Save complete job state
        self._save_json(
            snapshot_path / "complete_job_state.json",
            {
                "job_id": job_id,
                "snapshot_name": snapshot_name,
                "captured_at": datetime.now().isoformat(),
                "job_data": job_data
            }
        )

        # Extract and save individual agent outputs
        # These are the key inputs for testing agents in isolation
        agent_outputs = self._extract_agent_outputs(job_data)

        for agent_name, output_state in agent_outputs.items():
            self._save_json(
                snapshot_path / f"{agent_name}_output.json",
                {
                    "agent": agent_name,
                    "timestamp": datetime.now().isoformat(),
                    "state": output_state,
                    "description": f"Output state after {agent_name} execution"
                }
            )

        # Save metadata
        metadata = {
            "snapshot_name": snapshot_name,
            "job_id": job_id,
            "customer_url": job.customer_url,
            "status": job.status,
            "captured_at": datetime.now().isoformat(),
            "agents_captured": list(agent_outputs.keys()),
            "dataset_id": job_data.get("metadata", {}).get("datasetId"),
            "agent_id": job_data.get("metadata", {}).get("agentId"),
            "total_tables": job_data.get("metadata", {}).get("totalTables"),
            "total_rows": job_data.get("metadata", {}).get("totalRows")
        }

        self._save_json(snapshot_path / "metadata.json", metadata)

        print(f"✅ Snapshot captured: {snapshot_name}")
        print(f"   Location: {snapshot_path}")
        print(f"   Agents: {len(agent_outputs)}")
        print(f"   Dataset: {metadata.get('dataset_id', 'N/A')}")
        print(f"   CAPI Agent: {metadata.get('agent_id', 'N/A')}")

        return metadata

    def _extract_agent_outputs(self, job_data: Dict) -> Dict[str, Dict]:
        """
        Extract intermediate state after each agent execution.

        This reconstructs the state that would be passed to the next agent.
        """
        # For now, we can only capture the final state
        # In the future, we should modify the orchestrator to save intermediate states

        # Final state includes all outputs
        final_state = {
            "customer_url": job_data.get("customer_url"),
            "project_id": "bq-demos-469816",  # From job
            "customer_info": job_data.get("metadata", {}).get("customer_info", {}),
            "demo_story": {
                "demo_title": job_data.get("demo_title"),
                "golden_queries": job_data.get("golden_queries", []),
                "executive_summary": job_data.get("metadata", {}).get("executive_summary"),
                "business_challenges": job_data.get("metadata", {}).get("business_challenges"),
                "talking_track": job_data.get("metadata", {}).get("talking_track")
            },
            "schema": {"tables": job_data.get("schema", [])},
            "dataset_id": job_data.get("metadata", {}).get("datasetId"),
            "dataset_full_name": job_data.get("metadata", {}).get("datasetFullName"),
            "capi_agent_id": job_data.get("metadata", {}).get("agentId"),
            "capi_yaml_file": job_data.get("metadata", {}).get("yaml_file_path")
        }

        # Save as different agent outputs (in practice, each would have subset of fields)
        return {
            "01_research": {
                "customer_url": final_state["customer_url"],
                "customer_info": final_state["customer_info"],
                "business_domain": final_state.get("customer_info", {}).get("industry", "")
            },
            "02_demo_story": {
                **final_state,
                "demo_story": final_state["demo_story"]
            },
            "03_data_modeling": {
                **final_state,
                "schema": final_state["schema"]
            },
            "04_synthetic_data": {
                **final_state,
                "synthetic_data_files": [],  # Files are generated, not in job state
                "data_generation_complete": True
            },
            "05_infrastructure": {
                **final_state,
                "dataset_id": final_state["dataset_id"],
                "bigquery_provisioned": True
            },
            "06_capi_instructions": {
                **final_state,
                "capi_system_instructions": "",  # YAML content not stored in job state
                "capi_yaml_file": final_state["capi_yaml_file"],
                "capi_instructions_generated": True
            },
            "07_validation": final_state
        }

    def _save_json(self, filepath: Path, data: Any):
        """Save data as formatted JSON."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def create_minimal_template(self, snapshot_name: str):
        """
        Create a minimal template from a snapshot for fast testing.

        This is a hand-curated minimal state that's faster to use than full snapshots.
        """
        snapshot_path = self.snapshot_dir / snapshot_name
        template_path = self.snapshot_dir.parent / "templates" / "minimal_state.json"

        # Load complete job state
        with open(snapshot_path / "complete_job_state.json") as f:
            job_data = json.load(f)["job_data"]

        # Create minimal template (bare minimum to test infrastructure agent)
        minimal = {
            "customer_url": "https://www.example.com",
            "project_id": "test-project",
            "customer_info": {
                "company_name": "Test Company",
                "industry": "Technology"
            },
            "demo_story": {
                "demo_title": "Test Demo",
                "golden_queries": [
                    {
                        "id": "q1",
                        "question": "Show total sales",
                        "complexity": "SIMPLE"
                    }
                ]
            },
            "schema": {
                "tables": [
                    {
                        "name": "customers",
                        "description": "Customer data",
                        "schema": [
                            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
                            {"name": "name", "type": "STRING", "mode": "NULLABLE"}
                        ]
                    }
                ]
            },
            "synthetic_data_files": ["/tmp/test_customers.csv"],
            "capi_system_instructions": "You are a test assistant."
        }

        template_path.parent.mkdir(parents=True, exist_ok=True)
        self._save_json(template_path, minimal)

        print(f"✅ Minimal template created: {template_path}")

        return minimal


def main():
    """CLI for capturing snapshots."""
    import argparse

    parser = argparse.ArgumentParser(description="Capture job snapshots for testing")
    parser.add_argument("job_id", help="Job ID to capture")
    parser.add_argument("--name", help="Snapshot name (defaults to company name)")
    parser.add_argument("--create-template", action="store_true", help="Also create minimal template")

    args = parser.parse_args()

    capture = SnapshotCapture()
    metadata = capture.capture_job_snapshot(args.job_id, args.name)

    if args.create_template:
        capture.create_minimal_template(metadata["snapshot_name"])


if __name__ == "__main__":
    main()
