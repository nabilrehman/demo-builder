"""
Data Modeling Agent - Uses Claude Sonnet 4.5 to design BigQuery schema.
"""
import logging
from typing import Dict

from ..utils.vertex_llm_client import get_claude_vertex_client
from ..utils.prompt_templates import DATA_MODELING_PROMPT

logger = logging.getLogger(__name__)


class DataModelingAgent:
    """Agent for designing BigQuery database schema."""

    def __init__(self):
        # Use Claude Sonnet 4.5 for reliable JSON schema generation
        self.client = get_claude_vertex_client()
        logger.info("Data Modeling Agent initialized with Claude Sonnet 4.5")

    async def execute(self, state: Dict) -> Dict:
        """Execute data modeling phase."""
        logger.info("Designing BigQuery schema with Claude Sonnet 4.5 (story-driven)")

        try:
            # Get inputs
            customer_info = state.get("customer_info", {})
            demo_story = state.get("demo_story", {})

            if not demo_story:
                raise ValueError("No demo_story found in state. Run Demo Story Agent first.")

            # Design schema with Gemini (driven by demo narrative)
            schema = await self._design_schema(customer_info, demo_story, state)

            # Update state
            state["schema"] = schema
            state["tables"] = [table["name"] for table in schema.get("tables", [])]

            logger.info(f"Schema design complete. Created {len(state['tables'])} tables")

            # Log to CE Dashboard
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]

                tables = schema.get("tables", [])
                job_manager.add_log(
                    job_id,
                    "data modeling agent",
                    f"📐 Schema Design Complete: {len(tables)} tables designed",
                    "INFO"
                )

                # Show first 5 tables with field counts
                for i, table in enumerate(tables[:5]):
                    table_name = table.get("name", "Unknown")
                    field_count = len(table.get("schema", []))
                    job_manager.add_log(
                        job_id,
                        "data modeling agent",
                        f"  • {table_name}: {field_count} fields",
                        "INFO"
                    )

                if len(tables) > 5:
                    job_manager.add_log(
                        job_id,
                        "data modeling agent",
                        f"  ... and {len(tables) - 5} more tables",
                        "INFO"
                    )

            return state

        except Exception as e:
            logger.error(f"Data modeling failed: {e}", exc_info=True)
            raise

    async def _design_schema(self, customer_info: Dict, demo_story: Dict, state: Dict) -> Dict:
        """Use Gemini to design BigQuery schema driven by demo narrative."""
        import json

        # Get crazy frog context from state (empty string if not present)
        crazy_frog_context = state.get("crazy_frog_context", "")

        # Build prompt with demo story context
        prompt = DATA_MODELING_PROMPT.format(
            demo_story=json.dumps(demo_story, indent=2),
            customer_info=json.dumps(customer_info, indent=2),
            crazy_frog_context=crazy_frog_context
        )

        # Claude Sonnet 4.5 is excellent at structured schema generation
        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.3,  # Lower for consistent schema design
            max_output_tokens=16384,  # Maximum for Claude on Vertex - needed for complex schemas
            system_instruction="You are a database architect expert at designing BigQuery schemas. Always return valid JSON only. Ensure all JSON strings are properly terminated."
        )

        return self.client.parse_json_response(response_text)
