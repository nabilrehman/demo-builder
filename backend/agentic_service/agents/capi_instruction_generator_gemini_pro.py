"""
CAPI System Instruction Generator - GEMINI 2.5 PRO VERSION.
Creates YAML configuration for Conversational Analytics API with Gemini 2.5 Pro.

OPTIMIZATION: Uses Gemini 2.5 Pro instead of Claude Sonnet 4.5 for faster inference.
Expected: 1.5-2x faster YAML generation due to Gemini's faster response times.

NOTE: This agent's primary operation is a single large LLM call to generate
comprehensive YAML. Cannot be parallelized because the YAML must be a unified,
cohesive document.
"""
import logging
import os
import json
import asyncio
from typing import Dict
from agentic_service.utils.vertex_llm_client import get_gemini_pro_vertex_client
from agentic_service.utils.prompt_templates import SYSTEM_INSTRUCTION_GENERATOR_PROMPT

logger = logging.getLogger(__name__)


class CAPIInstructionGeneratorGeminiPro:
    """GEMINI 2.5 PRO: Agent for generating Conversational Analytics API system instructions."""

    def __init__(self):
        self.client = get_gemini_pro_vertex_client()  # Gemini 2.5 Pro for fast YAML generation
        logger.info("CAPI Instruction Generator initialized with Gemini 2.5 Pro")

    async def execute(self, state: Dict) -> Dict:
        """Execute CAPI system instruction generation phase with Gemini 2.5 Pro."""
        import time

        logger.info("🚀 Generating CAPI system instructions (YAML) with Gemini 2.5 Pro")
        start_time = time.time()

        try:
            schema = state.get("schema", {})
            demo_story = state.get("demo_story", {})
            dataset_id = state.get("dataset_full_name", "")

            if not schema or not demo_story or not dataset_id:
                raise ValueError("Missing schema, demo_story, or dataset_id")

            # Log to CE Dashboard - start
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]
                job_manager.add_log(
                    job_id,
                    "capi instruction generator gemini pro",
                    f"📝 Generating CAPI YAML system instructions with Gemini 2.5 Pro...",
                    "INFO"
                )

            # Generate YAML system instructions
            yaml_content = await self._generate_system_instructions(
                demo_story,
                schema,
                dataset_id,
                state
            )

            # Save to file (async I/O)
            output_file = await self._save_yaml_async(yaml_content, state)

            # Generate summary report (can run in parallel with state update)
            summary = self._generate_summary_report(yaml_content, state)

            elapsed = time.time() - start_time

            # Update state
            state["capi_system_instructions"] = yaml_content
            state["capi_yaml_file"] = output_file
            state["capi_instructions_generated"] = True
            state["capi_yaml_summary"] = summary

            logger.info(f"✅ CAPI system instructions generated in {elapsed:.2f}s")
            logger.info(f"   YAML file: {output_file}")
            logger.info(f"   Size: {len(yaml_content):,} characters")
            logger.info(f"   Lines: {len(yaml_content.split(chr(10))):,}")

            # Log to CE Dashboard - completion
            if "job_manager" in state and "job_id" in state:
                job_manager.add_log(
                    job_id,
                    "capi instruction generator gemini pro",
                    f"✅ CAPI YAML Generated: {len(yaml_content):,} chars in {elapsed:.2f}s",
                    "INFO"
                )

                # Show summary details
                if summary.get("table_count"):
                    job_manager.add_log(
                        job_id,
                        "capi instruction generator gemini pro",
                        f"  📊 Tables Documented: {summary['table_count']}",
                        "INFO"
                    )

                if summary.get("has_golden_queries"):
                    job_manager.add_log(
                        job_id,
                        "capi instruction generator gemini pro",
                        f"  💎 Golden Queries Included: Yes",
                        "INFO"
                    )

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
        """Generate YAML system instructions using Gemini 2.5 Pro."""
        logger.info("Calling Gemini 2.5 Pro to generate YAML...")

        # Get crazy frog context from state (empty string if not present)
        crazy_frog_context = state.get("crazy_frog_context", "")

        # Get job manager for live logging
        job_manager = state.get("job_manager")
        job_id = state.get("job_id")

        if job_manager and job_id:
            job_manager.add_log(
                job_id,
                "capi instruction generator gemini pro",
                f"  🧠 Analyzing schema and demo story with Gemini 2.5 Pro...",
                "INFO"
            )

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
field descriptions, relationships, and golden queries with exact SQL.

Return ONLY the YAML content - no markdown code blocks, no explanations."""
        )

        # Clean up markdown code blocks if present
        yaml_content = self._clean_yaml_response(yaml_content)

        if job_manager and job_id:
            job_manager.add_log(
                job_id,
                "capi instruction generator gemini pro",
                f"  ✓ YAML generation complete ({len(yaml_content):,} characters)",
                "INFO"
            )

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

    async def _save_yaml_async(self, yaml_content: str, state: Dict) -> str:
        """Save YAML to file with async I/O."""
        # Generate filename based on company
        customer_info = state.get("customer_info", {})
        company_name = customer_info.get("company_name", "demo").lower().replace(" ", "_")

        output_file = f"/tmp/capi_instructions_{company_name}.yaml"

        # Async file write
        await asyncio.to_thread(self._write_file, output_file, yaml_content)

        logger.info(f"Saved YAML to {output_file}")
        return output_file

    def _write_file(self, filepath: str, content: str):
        """Synchronous file write (runs in thread pool)."""
        with open(filepath, 'w') as f:
            f.write(content)

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
