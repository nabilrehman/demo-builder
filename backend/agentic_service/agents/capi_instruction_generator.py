"""
CAPI System Instruction Generator - Creates YAML configuration for Conversational Analytics API.

Generates comprehensive system instructions including:
- Agent persona and role
- Table definitions with business context
- Field-level descriptions and semantics
- Relationships and join paths
- Golden queries with exact SQL
- Business glossary
"""
import logging
import os
import json
from typing import Dict
from agentic_service.utils.vertex_llm_client import get_claude_vertex_client
from agentic_service.utils.prompt_templates import SYSTEM_INSTRUCTION_GENERATOR_PROMPT

logger = logging.getLogger(__name__)


class CAPIInstructionGenerator:
    """Agent for generating Conversational Analytics API system instructions."""

    def __init__(self):
        self.client = get_claude_vertex_client()  # Claude 4.5 for complex YAML generation
        logger.info("CAPI Instruction Generator initialized")

    async def execute(self, state: Dict) -> Dict:
        """Execute CAPI system instruction generation phase."""
        logger.info("Generating CAPI system instructions (YAML)")

        try:
            schema = state.get("schema", {})
            demo_story = state.get("demo_story", {})
            dataset_id = state.get("dataset_full_name", "")

            if not schema or not demo_story or not dataset_id:
                raise ValueError("Missing schema, demo_story, or dataset_id")

            # Generate YAML system instructions
            yaml_content = await self._generate_system_instructions(
                demo_story,
                schema,
                dataset_id,
                state
            )

            # Save to file
            output_file = self._save_yaml(yaml_content, state)

            # Update state
            state["capi_system_instructions"] = yaml_content
            state["capi_yaml_file"] = output_file
            state["capi_instructions_generated"] = True

            logger.info(f"✅ CAPI system instructions generated")
            logger.info(f"   YAML file: {output_file}")
            logger.info(f"   Size: {len(yaml_content):,} characters")

            return state

        except Exception as e:
            logger.error(f"CAPI instruction generation failed: {e}", exc_info=True)
            raise

    async def _generate_system_instructions(
        self,
        demo_story: Dict,
        schema: Dict,
        dataset_id: str,
        state: Dict
    ) -> str:
        """Generate YAML system instructions using Claude 4.5."""
        logger.info("Calling Claude 4.5 to generate YAML...")

        # Get crazy frog context from state (empty string if not present)
        crazy_frog_context = state.get("crazy_frog_context", "")

        # Prepare prompt
        prompt = SYSTEM_INSTRUCTION_GENERATOR_PROMPT.format(
            demo_story=json.dumps(demo_story, indent=2),
            schema=json.dumps(schema, indent=2),
            dataset_id=dataset_id,
            crazy_frog_context=crazy_frog_context
        )

        # Generate with high token limit (YAML can be large)
        yaml_content = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for structured output
            max_output_tokens=32000,  # Large YAML files
            system_instruction="""You are a Conversational Analytics API expert. Generate valid,
well-structured YAML that follows Google Cloud documentation exactly. Include comprehensive
field descriptions, relationships, and golden queries with exact SQL."""
        )

        # Clean up markdown code blocks if present
        yaml_content = self._clean_yaml_response(yaml_content)

        return yaml_content

    def _clean_yaml_response(self, response: str) -> str:
        """Remove markdown code blocks from YAML response."""
        if "```yaml" in response:
            start = response.index("```yaml") + len("```yaml")
            end = response.rindex("```")
            return response[start:end].strip()
        elif "```" in response:
            start = response.index("```") + 3
            end = response.rindex("```")
            return response[start:end].strip()
        return response.strip()

    def _save_yaml(self, yaml_content: str, state: Dict) -> str:
        """Save YAML to file."""
        # Generate filename based on company
        customer_info = state.get("customer_info", {})
        company_name = customer_info.get("company_name", "demo").lower().replace(" ", "_")

        output_file = f"/tmp/capi_instructions_{company_name}.yaml"

        with open(output_file, 'w') as f:
            f.write(yaml_content)

        logger.info(f"Saved YAML to {output_file}")
        return output_file

    def _generate_summary_report(self, yaml_content: str, state: Dict) -> Dict:
        """Generate summary report of YAML contents."""
        # Count sections
        summary = {
            "yaml_size_chars": len(yaml_content),
            "yaml_size_lines": len(yaml_content.split('\n')),
            "has_system_instruction": "system_instruction:" in yaml_content,
            "has_tables": "tables:" in yaml_content,
            "has_relationships": "relationships:" in yaml_content,
            "has_glossaries": "glossaries:" in yaml_content,
            "has_golden_queries": "golden_queries:" in yaml_content
        }

        # Count tables
        if "tables:" in yaml_content:
            table_count = yaml_content.count("  - name:")
            summary["table_count"] = table_count

        # Count relationships
        if "relationships:" in yaml_content:
            relationship_count = yaml_content.count("  - name:", yaml_content.index("relationships:"))
            summary["relationship_count"] = relationship_count

        return summary
