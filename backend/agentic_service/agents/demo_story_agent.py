"""
Demo Story Agent - Uses Claude Sonnet 4.5 to create compelling demo narrative.

This is the FIRST and MOST IMPORTANT agent. It acts as a Google Cloud Principal
Architect-level Customer Engineer to design the entire demo strategy.

PHASE 1 OPTIMIZATION: Split into 3 parallel LLM calls for 55% speed improvement.
"""
import logging
import asyncio
import time
import os
from typing import Dict

from ..utils.vertex_llm_client import get_claude_vertex_client
from ..utils.prompt_templates import (
    CORE_NARRATIVE_PROMPT,
    GOLDEN_QUERIES_PROMPT,
    DATA_SPECS_PROMPT
)

logger = logging.getLogger(__name__)


class DemoStoryAgent:
    """
    Agent for creating strategic demo narrative.

    This agent is the "sales brain" - it thinks like a Principal Architect CE
    and designs the most compelling story to showcase Conversational Analytics API.

    OPTIMIZATION: Uses parallel execution (3 concurrent LLM calls) to reduce
    execution time from ~5m 30s to ~2m 30s.
    """

    def __init__(self):
        # Use Claude 4.5 for sophisticated strategic thinking
        self.client = get_claude_vertex_client()

        # Read demo complexity configuration from environment
        self.num_queries = int(os.getenv("DEMO_NUM_QUERIES", "6"))
        self.num_scenes = int(os.getenv("DEMO_NUM_SCENES", "4"))
        self.num_entities = int(os.getenv("DEMO_NUM_ENTITIES", "8"))

        logger.info(f"Demo Story Agent initialized with Claude 4.5 (PARALLEL MODE)")
        logger.info(f"  Config: {self.num_queries} queries, {self.num_scenes} scenes, {self.num_entities} entities")

    async def execute(self, state: Dict) -> Dict:
        """Execute demo story creation phase with parallel execution."""
        start_time = time.time()
        logger.info("🚀 Creating demo narrative with PARALLEL execution (3 concurrent Claude 4.5 calls)")

        try:
            # Get customer info from research phase
            customer_info = state.get("customer_info", {})

            if not customer_info:
                raise ValueError("No customer_info found in state. Run Research Agent first.")

            # Create demo story with PARALLEL execution
            demo_story = await self._create_demo_story_parallel(customer_info, state)

            # Update state
            state["demo_story"] = demo_story
            state["demo_title"] = demo_story.get("demo_title")
            state["golden_queries"] = demo_story.get("golden_queries", [])
            state["data_requirements"] = demo_story.get("data_model_requirements", {})
            state["synthetic_data_requirements"] = demo_story.get("synthetic_data_requirements", {})

            elapsed = time.time() - start_time
            logger.info(f"✅ Demo story complete in {elapsed:.1f}s: '{state['demo_title']}'")
            logger.info(f"  - {len(state['golden_queries'])} golden queries")
            logger.info(f"  - {len(demo_story.get('demo_narrative', {}).get('story_arc', []))} story scenes")

            # Log detailed output to CE Dashboard
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]

                # Log demo story completion with title
                job_manager.add_log(
                    job_id,
                    "demo story agent",
                    f"✨ Demo Story Created: '{state['demo_title']}'",
                    "INFO"
                )

                # Log executive summary if available
                exec_summary = demo_story.get("executive_summary", "")
                if exec_summary:
                    summary_preview = exec_summary[:150] + "..." if len(exec_summary) > 150 else exec_summary
                    job_manager.add_log(
                        job_id,
                        "demo story agent",
                        f"  📋 Executive Summary: {summary_preview}",
                        "INFO"
                    )

                # Log story scenes
                story_arc = demo_story.get("demo_narrative", {}).get("story_arc", [])
                if story_arc:
                    job_manager.add_log(
                        job_id,
                        "demo story agent",
                        f"  🎬 Story Scenes: {len(story_arc)} scenes designed",
                        "INFO"
                    )

                # Log golden queries (show first 3 as preview)
                golden_queries = state.get("golden_queries", [])
                if golden_queries:
                    job_manager.add_log(
                        job_id,
                        "demo story agent",
                        f"  💎 Golden Queries Generated: {len(golden_queries)} queries",
                        "INFO"
                    )

                    # Show preview of first 3 queries
                    for i, query in enumerate(golden_queries[:3]):
                        complexity = query.get("complexity", "SIMPLE")
                        question = query.get("question", "")
                        question_preview = question[:80] + "..." if len(question) > 80 else question
                        job_manager.add_log(
                            job_id,
                            "demo story agent",
                            f"    {i+1}. [{complexity}] {question_preview}",
                            "INFO"
                        )

                    if len(golden_queries) > 3:
                        job_manager.add_log(
                            job_id,
                            "demo story agent",
                            f"    ... and {len(golden_queries) - 3} more queries",
                            "INFO"
                        )

                # Log data entities
                key_entities = demo_story.get("data_model_requirements", {}).get("key_entities", [])
                if key_entities:
                    entity_names = ", ".join([e.get("name", "Unknown") for e in key_entities[:5]])
                    job_manager.add_log(
                        job_id,
                        "demo story agent",
                        f"  📊 Data Entities Identified: {entity_names}" + ("..." if len(key_entities) > 5 else ""),
                        "INFO"
                    )

            return state

        except Exception as e:
            logger.error(f"Demo story creation failed: {e}", exc_info=True)
            raise

    async def _create_demo_story_parallel(self, customer_info: Dict, state: Dict) -> Dict:
        """
        Use Claude 4.5 to create strategic demo narrative with PARALLEL execution.

        Splits generation into 3 concurrent tasks:
        1. Core Narrative (~6K tokens, ~60s)
        2. Golden Queries (~20K tokens, ~200s) <- bottleneck
        3. Data Specifications (~8K tokens, ~80s)

        Expected time: ~200s (longest task) vs ~320s (sequential)
        Improvement: ~120s savings (37.5% faster)
        """
        import json

        # Get crazy frog context from state (empty string if not present)
        crazy_frog_context = state.get("crazy_frog_context", "")
        customer_info_json = json.dumps(customer_info, indent=2)

        # Define system instruction for all calls
        system_instruction = """You are a Google Cloud Principal Architect and master sales engineer.

Your expertise:
- Deep understanding of Conversational Analytics API capabilities
- Expert at crafting compelling business value narratives
- Skilled at designing demos that win deals
- Know how to make technology relatable to business executives

Your approach:
- Start with business pain, not technology features
- Design progressive demo flows that build excitement
- Include "wow moments" that make prospects lean forward
- Always tie back to ROI and business outcomes
- Think like a storyteller, not just a technologist

Return ONLY valid JSON - no markdown, no explanations outside the JSON structure."""

        logger.info("  → Launching 3 parallel generation tasks...")

        # Run 3 tasks in parallel
        tasks = [
            self._generate_core_narrative(customer_info_json, crazy_frog_context, system_instruction, self.num_scenes),
            self._generate_golden_queries(customer_info_json, crazy_frog_context, system_instruction, self.num_queries),
            self._generate_data_specs(customer_info_json, crazy_frog_context, system_instruction, self.num_entities)
        ]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Parallel execution failed: {e}")
            raise

        # Check for errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                task_names = ["Core Narrative", "Golden Queries", "Data Specs"]
                raise ValueError(f"{task_names[i]} generation failed: {result}")

        core_narrative, golden_queries_result, data_specs = results

        logger.info("  ✓ All parallel tasks completed successfully")

        # Merge results
        demo_story = {
            **core_narrative,
            "golden_queries": golden_queries_result.get("golden_queries", []),
            **data_specs
        }

        return demo_story

    async def _generate_core_narrative(
        self,
        customer_info_json: str,
        crazy_frog_context: str,
        system_instruction: str,
        num_scenes: int
    ) -> Dict:
        """Generate demo title, summary, challenges, story arc, talking track."""
        start = time.time()
        logger.info(f"    [Task 1/3] Core Narrative: Starting (target: {num_scenes} scenes)...")

        prompt = CORE_NARRATIVE_PROMPT.format(
            customer_info=customer_info_json,
            crazy_frog_context=crazy_frog_context,
            num_scenes=num_scenes
        )

        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=8000,  # Reduced from 32K
            system_instruction=system_instruction
        )

        result = self.client.parse_json_response(response_text)
        elapsed = time.time() - start
        logger.info(f"    [Task 1/3] Core Narrative: Complete in {elapsed:.1f}s")

        return result

    async def _generate_golden_queries(
        self,
        customer_info_json: str,
        crazy_frog_context: str,
        system_instruction: str,
        num_queries: int
    ) -> Dict:
        """Generate golden queries with SQL (configurable count)."""
        start = time.time()
        logger.info(f"    [Task 2/3] Golden Queries: Starting (target: {num_queries} queries)...")

        prompt = GOLDEN_QUERIES_PROMPT.format(
            customer_info=customer_info_json,
            crazy_frog_context=crazy_frog_context,
            num_queries=num_queries
        )

        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=20000,  # Largest allocation for queries
            system_instruction=system_instruction
        )

        result = self.client.parse_json_response(response_text)
        elapsed = time.time() - start
        query_count = len(result.get("golden_queries", []))
        logger.info(f"    [Task 2/3] Golden Queries: Complete in {elapsed:.1f}s ({query_count} queries)")

        return result

    async def _generate_data_specs(
        self,
        customer_info_json: str,
        crazy_frog_context: str,
        system_instruction: str,
        num_entities: int
    ) -> Dict:
        """Generate data model & synthetic data requirements (configurable entity count)."""
        start = time.time()
        logger.info(f"    [Task 3/3] Data Specifications: Starting (target: {num_entities} entities)...")

        prompt = DATA_SPECS_PROMPT.format(
            customer_info=customer_info_json,
            crazy_frog_context=crazy_frog_context,
            num_entities=num_entities
        )

        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=10000,  # Reduced from 32K
            system_instruction=system_instruction
        )

        result = self.client.parse_json_response(response_text)
        elapsed = time.time() - start
        entity_count = len(result.get("data_model_requirements", {}).get("key_entities", []))
        logger.info(f"    [Task 3/3] Data Specifications: Complete in {elapsed:.1f}s ({entity_count} entities)")

        return result
