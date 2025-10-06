"""
Data Modeling Agent - Gemini 2.5 Pro VERSION.
Uses Gemini 2.5 Pro via Vertex AI for schema generation.
"""
import logging
from typing import Dict

from ..utils.vertex_llm_client import get_gemini_pro_vertex_client
from ..utils.prompt_templates import DATA_MODELING_PROMPT

logger = logging.getLogger(__name__)


class DataModelingAgentGeminiPro:
    """Agent for designing BigQuery database schema using Gemini 2.5 Pro."""

    def __init__(self):
        # Use Gemini 2.5 Pro via Vertex AI for schema generation
        self.client = get_gemini_pro_vertex_client()
        logger.info("Data Modeling Agent initialized with Gemini 2.5 Pro (Vertex AI)")

    async def execute(self, state: Dict) -> Dict:
        """Execute data modeling phase with Gemini 2.5 Pro."""
        import time

        logger.info("🚀 Designing BigQuery schema with Gemini 2.5 Pro")
        start_time = time.time()

        try:
            # Get inputs
            customer_info = state.get("customer_info", {})
            demo_story = state.get("demo_story", {})

            if not demo_story:
                raise ValueError("No demo_story found in state. Run Demo Story Agent first.")

            # Log to SSE stream
            job_manager = state.get("job_manager")
            job_id = state.get("job_id")

            golden_queries = state.get("golden_queries", [])
            if job_manager and job_id:
                job_manager.add_log(
                    job_id,
                    "data modeling agent",
                    f"📐 Designing BigQuery schema with Gemini 2.5 Pro...",
                    "INFO"
                )
                job_manager.add_log(
                    job_id,
                    "data modeling agent",
                    f"  → Schema must support {len(golden_queries)} golden queries",
                    "INFO"
                )

            # Design schema with Gemini 2.5 Pro
            schema = await self._design_schema(customer_info, demo_story, state)

            elapsed = time.time() - start_time

            # Update state
            state["schema"] = schema
            state["tables"] = [table["name"] for table in schema.get("tables", [])]

            logger.info(f"✅ Schema design complete in {elapsed:.2f}s. Created {len(state['tables'])} tables")

            # Log to CE Dashboard
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]

                tables = schema.get("tables", [])
                job_manager.add_log(
                    job_id,
                    "data modeling agent gemini pro",
                    f"📐 Schema Design Complete (Gemini 2.5 Pro): {len(tables)} tables in {elapsed:.2f}s",
                    "INFO"
                )

                # Show first 5 tables with field counts
                for i, table in enumerate(tables[:5]):
                    table_name = table.get("name", "Unknown")
                    field_count = len(table.get("schema", []))
                    job_manager.add_log(
                        job_id,
                        "data modeling agent gemini pro",
                        f"  • {table_name}: {field_count} fields",
                        "INFO"
                    )

                if len(tables) > 5:
                    job_manager.add_log(
                        job_id,
                        "data modeling agent gemini pro",
                        f"  ... and {len(tables) - 5} more tables",
                        "INFO"
                    )

            return state

        except Exception as e:
            logger.error(f"Data modeling failed: {e}", exc_info=True)
            raise

    async def _design_schema(self, customer_info: Dict, demo_story: Dict, state: Dict) -> Dict:
        """Use Gemini 2.5 Pro to design BigQuery schema."""
        import json

        # Get crazy frog context from state (empty string if not present)
        crazy_frog_context = state.get("crazy_frog_context", "")

        # Build prompt with demo story context
        prompt = DATA_MODELING_PROMPT.format(
            demo_story=json.dumps(demo_story, indent=2),
            customer_info=json.dumps(customer_info, indent=2),
            crazy_frog_context=crazy_frog_context
        )

        # Gemini 2.5 Pro for high-quality schema generation
        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.3,  # Lower for consistent schema design
            max_output_tokens=8192,
            system_instruction=(
                "You are a database architect expert at designing BigQuery schemas. "
                "Always return valid JSON only. Ensure all JSON strings are properly terminated. "
                "Design comprehensive, well-structured schemas with proper relationships and data types."
            )
        )

        schema = self.client.parse_json_response(response_text)

        # DEFENSIVE LAYER 2: Validate and fix REPEATED fields immediately after generation
        schema = self._validate_and_fix_schema(schema, state)

        return schema

    def _validate_and_fix_schema(self, schema: Dict, state: Dict) -> Dict:
        """
        DEFENSIVE VALIDATION: Check for REPEATED fields and convert them to NULLABLE STRING.

        This is a second defensive layer - the first is in Infrastructure Agent.
        We fix REPEATED fields here so they never even reach the Infrastructure Agent.
        """
        tables = schema.get("tables", [])
        total_repeated_fixed = 0

        for table in tables:
            table_name = table.get("name", "unknown")
            fields = table.get("schema", [])
            repeated_fields_in_table = []

            for field in fields:
                field_name = field.get("name", "")
                field_mode = field.get("mode", "NULLABLE")
                field_type = field.get("type", "STRING")

                if field_mode == "REPEATED":
                    repeated_fields_in_table.append(field_name)

                    # Convert to NULLABLE
                    field["mode"] = "NULLABLE"

                    # If it's an array type, convert to STRING
                    if field_type.startswith("ARRAY"):
                        field["type"] = "STRING"
                        field["description"] = f"[Array stored as comma-separated string] {field.get('description', '')}"

                    logger.warning(
                        f"🛡️  [Data Modeling Agent] REPEATED field detected: '{table_name}.{field_name}' - Converting to NULLABLE STRING"
                    )
                    total_repeated_fixed += 1

            # Log to SSE if any fields were fixed
            if repeated_fields_in_table and "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]
                job_manager.add_log(
                    job_id,
                    "data modeling agent",
                    f"🛡️  Fixed {len(repeated_fields_in_table)} REPEATED fields in table '{table_name}': {', '.join(repeated_fields_in_table)}",
                    "INFO"
                )

        if total_repeated_fixed > 0:
            logger.warning(
                f"🛡️  [Data Modeling Agent] Total REPEATED fields fixed: {total_repeated_fixed} across {len(tables)} tables"
            )

            # Log summary to SSE
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]
                job_manager.add_log(
                    job_id,
                    "data modeling agent",
                    f"✅ Schema validated: {total_repeated_fixed} REPEATED fields auto-converted to NULLABLE STRING",
                    "INFO"
                )

        return schema
