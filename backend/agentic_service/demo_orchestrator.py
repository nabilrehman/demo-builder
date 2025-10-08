"""
LangGraph Orchestrator - Coordinates all agents in the demo generation pipeline.

Pipeline Flow:
1. Research Agent (V1 or V2) → Analyze customer website
2. Demo Story Agent → Create compelling demo narrative
3. Data Modeling Agent → Design BigQuery schema
4. Synthetic Data Generator → Generate realistic data
5. Infrastructure Agent → Provision BigQuery resources
6. CAPI Instruction Generator → Create YAML system instructions
7. Demo Validator → Validate queries work

State is passed between agents and updated at each step.
"""
import logging
import os
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END

# Agent imports moved to _build_graph() and run_demo_orchestrator()
# to support dynamic model selection via config

logger = logging.getLogger(__name__)

# Agent index mapping for progress tracking
AGENT_INDEX_MAP = {
    "Research": 0,
    "Demo Story": 1,
    "Data Modeling": 2,
    "Synthetic Data": 3,
    "Infrastructure": 4,
    "CAPI Instructions": 5,
    "Validation": 6
}


class DemoGenerationState(TypedDict):
    """State shared across all agents."""
    # Input
    customer_url: str
    project_id: str

    # Research Agent output
    customer_info: Dict
    business_domain: str

    # Demo Story Agent output
    demo_story: Dict
    demo_title: str  # FIX: Added so LangGraph persists it
    golden_queries: list  # FIX: Added so LangGraph persists it
    data_requirements: Dict  # FIX: Added so LangGraph persists it
    synthetic_data_requirements: Dict  # FIX: Added so LangGraph persists it

    # Data Modeling Agent output
    schema: Dict

    # Synthetic Data Generator output
    synthetic_data_files: list
    table_file_metadata: list  # FIX: Added for code-based data generator (stores table names + row counts)
    data_generation_complete: bool

    # Infrastructure Agent output
    dataset_id: str
    dataset_full_name: str
    capi_agent_id: str  # FIX: Added to schema so LangGraph persists it
    table_stats: Dict
    demo_documentation: Dict
    bigquery_provisioned: bool

    # CAPI Instruction Generator output
    capi_system_instructions: str
    capi_yaml_file: str
    capi_instructions_generated: bool

    # Demo Validator output
    validation_results: Dict
    validation_complete: bool

    # Progress tracking
    current_stage: str
    errors: list


class DemoOrchestrator:
    """Orchestrates the complete demo generation pipeline using LangGraph."""

    def __init__(self):
        self.graph = self._build_graph()
        logger.info("Demo Orchestrator initialized")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        # Import config system and non-LLM agents
        from agentic_service.config.agent_config import get_agent_class
        from agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized
        from agentic_service.agents.demo_validator_optimized import DemoValidatorOptimized

        # ====================================================================
        # 🔧 SYNTHETIC DATA GENERATOR SELECTION
        # ====================================================================
        # Choose between CODE-BASED (default) or LLM-BASED data generation
        USE_CODE_GENERATOR = os.getenv("USE_CODE_DATA_GENERATOR", "true").lower() == "true"

        if USE_CODE_GENERATOR:
            from agentic_service.agents.synthetic_data_generator_code import SyntheticDataGeneratorCode
            SyntheticDataGenerator = SyntheticDataGeneratorCode
            logger.info("✅ Using CODE-BASED data generator (Claude generates Python code)")
        else:
            from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown
            SyntheticDataGenerator = SyntheticDataGeneratorMarkdown
            logger.info("✅ Using LLM-BASED data generator (Gemini generates markdown tables)")

            # Check for LLM-only enforcement (legacy)
            FORCE_LLM = os.getenv("FORCE_LLM_DATA_GENERATION", "true").lower() == "true"
            if FORCE_LLM:
                logger.info("🔒 FORCE_LLM_DATA_GENERATION=true - Faker fallback is DISABLED")

        # ====================================================================
        # LLM-BASED AGENTS (model selection via config)
        # ====================================================================

        # Get agent classes from config (checks env vars, then defaults)
        ResearchAgentClass = get_agent_class("research")
        DemoStoryAgentClass = get_agent_class("demo_story")
        DataModelingAgentClass = get_agent_class("data_modeling")
        CAPIAgentClass = get_agent_class("capi")

        # Read V2 configuration from environment (for research agent params)
        max_pages = int(os.getenv('V2_MAX_PAGES', '30'))
        max_depth = int(os.getenv('V2_MAX_DEPTH', '2'))
        enable_blog = os.getenv('V2_ENABLE_BLOG', 'false').lower() == 'true'
        enable_linkedin = os.getenv('V2_ENABLE_LINKEDIN', 'false').lower() == 'true'
        enable_youtube = os.getenv('V2_ENABLE_YOUTUBE', 'false').lower() == 'true'

        # Initialize LLM agents
        research_agent = ResearchAgentClass(
            max_pages=max_pages,
            max_depth=max_depth,
            enable_blog=enable_blog,
            enable_linkedin=enable_linkedin,
            enable_youtube=enable_youtube
        )
        demo_story_agent = DemoStoryAgentClass()
        data_modeling_agent = DataModelingAgentClass()
        capi_instruction_generator = CAPIAgentClass()

        # ====================================================================
        # NON-LLM AGENTS (always use optimized versions)
        # ====================================================================

        synthetic_data_generator = SyntheticDataGenerator()  # CODE or LLM-based (selected above)
        infrastructure_agent = InfrastructureAgentOptimized()  # Parallel loading
        demo_validator = DemoValidatorOptimized()  # Parallel validation

        logger.info("🚀 Pipeline initialized with config-based agent selection")

        # Create state graph
        workflow = StateGraph(DemoGenerationState)

        # Add nodes (agents)
        # NOTE: Node names must not conflict with state keys, so we append _node
        workflow.add_node("research_node", self._wrap_agent(research_agent, "Research"))
        workflow.add_node("demo_story_node", self._wrap_agent(demo_story_agent, "Demo Story"))
        workflow.add_node("data_modeling_node", self._wrap_agent(data_modeling_agent, "Data Modeling"))
        workflow.add_node("synthetic_data_node", self._wrap_agent(synthetic_data_generator, "Synthetic Data"))
        workflow.add_node("infrastructure_node", self._wrap_agent(infrastructure_agent, "Infrastructure"))
        workflow.add_node("capi_instructions_node", self._wrap_agent(capi_instruction_generator, "CAPI Instructions"))
        workflow.add_node("validation_node", self._wrap_agent(demo_validator, "Validation"))

        # Define edges (flow)
        workflow.set_entry_point("research_node")
        workflow.add_edge("research_node", "demo_story_node")
        workflow.add_edge("demo_story_node", "data_modeling_node")
        workflow.add_edge("data_modeling_node", "synthetic_data_node")
        workflow.add_edge("synthetic_data_node", "infrastructure_node")
        workflow.add_edge("infrastructure_node", "capi_instructions_node")
        workflow.add_edge("capi_instructions_node", "validation_node")
        workflow.add_edge("validation_node", END)

        return workflow.compile()

    def _wrap_agent(self, agent, stage_name: str):
        """Wrap agent execution with progress tracking."""
        async def wrapped(state: Dict) -> Dict:
            logger.info(f"\n{'='*80}")
            logger.info(f"STAGE: {stage_name}")
            logger.info(f"{'='*80}")

            state["current_stage"] = stage_name

            try:
                # Execute agent
                updated_state = await agent.execute(state)

                logger.info(f"✅ {stage_name} complete")
                return updated_state

            except Exception as e:
                logger.error(f"❌ {stage_name} failed: {e}", exc_info=True)

                # Track error
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append({
                    "stage": stage_name,
                    "error": str(e)
                })

                # Re-raise to stop pipeline
                raise

        return wrapped

    async def generate_demo(self, customer_url: str, project_id: str = None) -> Dict:
        """
        Generate complete demo from customer URL.

        Args:
            customer_url: Customer website URL to analyze
            project_id: GCP project ID (optional, defaults to env var)

        Returns:
            Final state with all generated artifacts
        """
        logger.info("="*80)
        logger.info("DEMO GENERATION PIPELINE STARTED")
        logger.info("="*80)
        logger.info(f"Customer URL: {customer_url}")
        logger.info(f"Project ID: {project_id or 'from environment'}")

        # Initialize state
        initial_state = {
            "customer_url": customer_url,
            "project_id": project_id or "bq-demos-469816",
            "current_stage": "Initializing",
            "errors": [],
            "crazy_frog_context": ""  # Default empty string for prompt formatting
        }

        # Execute pipeline
        try:
            final_state = await self.graph.ainvoke(initial_state)

            logger.info("\n" + "="*80)
            logger.info("DEMO GENERATION COMPLETE!")
            logger.info("="*80)

            self._print_summary(final_state)

            return final_state

        except Exception as e:
            logger.error(f"\n{'='*80}")
            logger.error("DEMO GENERATION FAILED")
            logger.error(f"{'='*80}")
            logger.error(f"Error: {e}")

            if "errors" in initial_state:
                logger.error("\nError details:")
                for error in initial_state["errors"]:
                    logger.error(f"  - {error['stage']}: {error['error']}")

            raise

    def _print_summary(self, state: Dict):
        """Print summary of generated demo."""
        customer_info = state.get("customer_info", {})
        demo_story = state.get("demo_story", {})
        schema = state.get("schema", {})
        dataset_id = state.get("dataset_full_name", "")
        validation_results = state.get("validation_results", {})

        logger.info("\n📊 DEMO SUMMARY")
        logger.info(f"\nCompany: {customer_info.get('company_name', 'N/A')}")
        logger.info(f"Industry: {customer_info.get('industry', 'N/A')}")
        logger.info(f"Demo Title: {demo_story.get('demo_title', 'N/A')}")

        logger.info(f"\n📈 DATA")
        logger.info(f"Dataset: {dataset_id}")
        logger.info(f"Tables: {len(schema.get('tables', []))}")

        table_stats = state.get("table_stats", {})
        if table_stats:
            total_rows = sum(s['row_count'] for s in table_stats.values())
            total_size = sum(s['size_mb'] for s in table_stats.values())
            logger.info(f"Total Rows: {total_rows:,}")
            logger.info(f"Total Size: {total_size:.2f} MB")

        logger.info(f"\n💡 GOLDEN QUERIES")
        golden_queries = demo_story.get("golden_queries", [])
        logger.info(f"Count: {len(golden_queries)}")

        logger.info(f"\n📄 ARTIFACTS")
        logger.info(f"CAPI YAML: {state.get('capi_yaml_file', 'N/A')}")
        demo_docs = state.get("demo_documentation", {})
        logger.info(f"Demo Report: {demo_docs.get('report_file', 'N/A')}")

        logger.info(f"\n✅ VALIDATION")
        logger.info(f"Queries Tested: {validation_results.get('total_queries', 0)}")
        logger.info(f"SQL Validated: {validation_results.get('sql_validated', 0)}")

        logger.info(f"\n🎯 NEXT STEPS")
        logger.info("1. Review demo documentation")
        logger.info("2. Create CAPI agent using generated YAML")
        logger.info("3. Test golden queries in CAPI interface")
        logger.info("4. Customize and present to customer!")


# ============================================================================
# API Integration Function
# ============================================================================

async def run_demo_orchestrator(
    customer_url: str,
    project_id: str,
    job_id: str,
    job_manager,
    crazy_frog_context: Dict = None
) -> Dict:
    """
    Run the demo orchestrator with job state manager integration.

    This function wraps the orchestrator to provide real-time progress updates
    to the job state manager, enabling SSE streaming to frontend.

    Args:
        customer_url: Customer website URL
        project_id: GCP project ID
        job_id: Unique job ID from job state manager
        job_manager: JobStateManager instance for progress tracking
        crazy_frog_context: Optional Crazy Frog context for enhanced prompts

    Returns:
        Dict with status, results, and errors
    """
    logger.info(f"Starting demo orchestrator for job {job_id}")

    try:
        # Initialize orchestrator
        orchestrator = DemoOrchestrator()

        # Create custom wrapper for progress tracking
        def create_progress_wrapper(agent, stage_name: str, agent_index: int):
            """Create a wrapper that updates job manager during execution."""
            async def wrapped(state: Dict) -> Dict:
                logger.info(f"\n{'='*80}")
                logger.info(f"STAGE {agent_index + 1}/7: {stage_name}")
                logger.info(f"{'='*80}")

                # Update job manager - agent started
                job_manager.update_current_phase(job_id, stage_name)
                job_manager.update_agent_status(job_id, agent_index, "running", 0)
                job_manager.add_log(
                    job_id,
                    stage_name.lower(),
                    f"Starting {stage_name}...",
                    "INFO"
                )

                state["current_stage"] = stage_name
                state["job_id"] = job_id
                state["job_manager"] = job_manager

                try:
                    # Execute agent
                    updated_state = await agent.execute(state)

                    # Update job manager - agent completed
                    job_manager.update_agent_status(job_id, agent_index, "completed", 100)
                    job_manager.add_log(
                        job_id,
                        stage_name.lower(),
                        f"✅ {stage_name} completed successfully",
                        "INFO"
                    )

                    # After Research Agent completes, extract and store company name
                    if agent_index == 0 and "customer_info" in updated_state:
                        company_name = updated_state["customer_info"].get("company_name", "Unknown Company")
                        job = job_manager.get_job(job_id)
                        if job:
                            job.company_name = company_name
                            logger.info(f"📋 Company name set: {company_name}")

                    logger.info(f"✅ {stage_name} complete")
                    return updated_state

                except Exception as e:
                    logger.error(f"❌ {stage_name} failed: {e}", exc_info=True)

                    # Update job manager - agent failed
                    job_manager.update_agent_status(
                        job_id,
                        agent_index,
                        "failed",
                        0,
                        str(e)
                    )
                    job_manager.add_log(
                        job_id,
                        stage_name.lower(),
                        f"❌ {stage_name} failed: {str(e)}",
                        "ERROR"
                    )
                    job_manager.add_error(job_id, f"{stage_name}: {str(e)}")

                    # Track error in state
                    if "errors" not in state:
                        state["errors"] = []
                    state["errors"].append({
                        "stage": stage_name,
                        "error": str(e)
                    })

                    # Re-raise to stop pipeline
                    raise

            return wrapped

        # Import config system and non-LLM agents
        from agentic_service.config.agent_config import get_agent_class
        from agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized
        from agentic_service.agents.demo_validator_optimized import DemoValidatorOptimized

        # ====================================================================
        # 🔧 SYNTHETIC DATA GENERATOR SELECTION
        # ====================================================================
        USE_CODE_GENERATOR = os.getenv("USE_CODE_DATA_GENERATOR", "true").lower() == "true"

        if USE_CODE_GENERATOR:
            from agentic_service.agents.synthetic_data_generator_code import SyntheticDataGeneratorCode
            SyntheticDataGenerator = SyntheticDataGeneratorCode
            logger.info("✅ Using CODE-BASED data generator (Claude generates Python code)")
        else:
            from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown
            SyntheticDataGenerator = SyntheticDataGeneratorMarkdown
            logger.info("✅ Using LLM-BASED data generator (Gemini generates markdown tables)")

        # ====================================================================
        # LLM-BASED AGENTS (model selection via config)
        # ====================================================================

        # Get agent classes from config (checks env vars, then defaults)
        ResearchAgentClass = get_agent_class("research")
        DemoStoryAgentClass = get_agent_class("demo_story")
        DataModelingAgentClass = get_agent_class("data_modeling")
        CAPIAgentClass = get_agent_class("capi")

        # Read V2 configuration from environment (for research agent params)
        max_pages = int(os.getenv('V2_MAX_PAGES', '30'))
        max_depth = int(os.getenv('V2_MAX_DEPTH', '2'))
        enable_blog = os.getenv('V2_ENABLE_BLOG', 'false').lower() == 'true'
        enable_linkedin = os.getenv('V2_ENABLE_LINKEDIN', 'false').lower() == 'true'
        enable_youtube = os.getenv('V2_ENABLE_YOUTUBE', 'false').lower() == 'true'

        # Initialize LLM agents
        research_agent = ResearchAgentClass(
            max_pages=max_pages,
            max_depth=max_depth,
            enable_blog=enable_blog,
            enable_linkedin=enable_linkedin,
            enable_youtube=enable_youtube
        )
        demo_story_agent = DemoStoryAgentClass()
        data_modeling_agent = DataModelingAgentClass()
        capi_instruction_generator = CAPIAgentClass()

        # ====================================================================
        # NON-LLM AGENTS (always use optimized versions)
        # ====================================================================

        synthetic_data_generator = SyntheticDataGenerator()  # CODE or LLM-based (selected above)
        infrastructure_agent = InfrastructureAgentOptimized()
        demo_validator = DemoValidatorOptimized()

        logger.info("🚀 Pipeline initialized with config-based agent selection")

        # Create state graph with progress wrappers
        workflow = StateGraph(DemoGenerationState)

        # Add nodes with progress tracking
        # NOTE: Node names must not conflict with state keys, so we append _node
        workflow.add_node("research_node", create_progress_wrapper(research_agent, "Research Agent", 0))
        workflow.add_node("demo_story_node", create_progress_wrapper(demo_story_agent, "Demo Story Agent", 1))
        workflow.add_node("data_modeling_node", create_progress_wrapper(data_modeling_agent, "Data Modeling Agent", 2))
        workflow.add_node("synthetic_data_node", create_progress_wrapper(synthetic_data_generator, "Synthetic Data Generator", 3))
        workflow.add_node("infrastructure_node", create_progress_wrapper(infrastructure_agent, "Infrastructure Agent", 4))
        workflow.add_node("capi_instructions_node", create_progress_wrapper(capi_instruction_generator, "CAPI Instruction Generator", 5))
        workflow.add_node("validation_node", create_progress_wrapper(demo_validator, "Demo Validator", 6))

        # Define edges (flow)
        workflow.set_entry_point("research_node")
        workflow.add_edge("research_node", "demo_story_node")
        workflow.add_edge("demo_story_node", "data_modeling_node")
        workflow.add_edge("data_modeling_node", "synthetic_data_node")
        workflow.add_edge("synthetic_data_node", "infrastructure_node")
        workflow.add_edge("infrastructure_node", "capi_instructions_node")
        workflow.add_edge("capi_instructions_node", "validation_node")
        workflow.add_edge("validation_node", END)

        # Compile graph
        graph = workflow.compile()

        # Initialize state with ALL TypedDict fields for proper state propagation
        initial_state = {
            "customer_url": customer_url,
            "project_id": project_id,
            "current_stage": "Initializing",
            "errors": [],
            "crazy_frog_context": "",  # Default empty string for default mode
            # Pre-initialize all state fields to ensure LangGraph state propagation
            "customer_info": {},  # Will be populated by Research Agent
            "business_domain": "",
            "demo_story": {},
            "demo_title": "",  # FIX: Initialize so LangGraph tracks it
            "golden_queries": [],  # FIX: Initialize so LangGraph tracks it
            "data_requirements": {},  # FIX: Initialize so LangGraph tracks it
            "synthetic_data_requirements": {},  # FIX: Initialize so LangGraph tracks it
            "schema": {},
            "synthetic_data_files": [],
            "data_generation_complete": False,
            "dataset_id": "",
            "dataset_full_name": "",
            "capi_agent_id": "",
            "table_stats": {},
            "demo_documentation": {},
            "bigquery_provisioned": False,
            "capi_system_instructions": "",
            "capi_yaml_file": "",
            "capi_instructions_generated": False,
            "validation_results": {},
            "validation_complete": False
        }

        # Add Crazy Frog context if provided
        if crazy_frog_context:
            from agentic_service.utils.prompt_enhancer import build_crazy_frog_context_block
            from agentic_service.models.crazy_frog_request import CrazyFrogProvisioningRequest

            # Build context block for prompts
            crazy_frog_request = CrazyFrogProvisioningRequest(
                customer_url=customer_url,
                use_case_context=crazy_frog_context.get("use_case_context", ""),
                industry_hint=crazy_frog_context.get("industry_hint"),
                target_persona=crazy_frog_context.get("target_persona"),
                demo_complexity=crazy_frog_context.get("demo_complexity"),
                special_focus=crazy_frog_context.get("special_focus"),
                integrations=crazy_frog_context.get("integrations"),
                avoid_topics=crazy_frog_context.get("avoid_topics")
            )

            context_block = build_crazy_frog_context_block(crazy_frog_request)
            initial_state["crazy_frog_context"] = context_block

            job_manager.add_log(
                job_id,
                "system",
                "🐸 Running in Crazy Frog Mode with enhanced context",
                "INFO"
            )

        # Execute pipeline
        job_manager.add_log(job_id, "system", "Starting 7-agent pipeline...", "INFO")

        final_state = await graph.ainvoke(initial_state)

        # Extract results for response
        demo_story = final_state.get("demo_story", {})
        validation_results = final_state.get("validation_results", {})

        # Prepare golden queries for frontend
        golden_queries = []
        for query in demo_story.get("golden_queries", []):
            golden_queries.append({
                "id": query.get("id", ""),
                "sequence": query.get("sequence", 0),
                "complexity": query.get("complexity", "SIMPLE"),
                "question": query.get("question", ""),
                "sql": query.get("expected_sql", ""),
                "businessValue": query.get("business_value", "")
            })

        # Prepare schema for frontend
        schema_data = []
        schema_dict = final_state.get("schema", {})
        for table in schema_dict.get("tables", []):
            schema_data.append({
                "name": table.get("name", ""),  # FIX: Changed from "table_name" to "name"
                "description": table.get("description", ""),
                "rowCount": 0,  # Will be filled by table_stats if available
                "fieldCount": len(table.get("schema", [])),  # FIX: Changed from "fields" to "schema"
                "fields": [
                    {
                        "name": field.get("name", ""),
                        "type": field.get("type", "STRING"),
                        "mode": field.get("mode", "NULLABLE"),
                        "description": field.get("description", "")
                    }
                    for field in table.get("schema", [])  # FIX: Changed from "fields" to "schema"
                ]
            })

        # Add row counts from table stats
        table_stats = final_state.get("table_stats", {})
        for table in schema_data:
            if table["name"] in table_stats:
                table["rowCount"] = table_stats[table["name"]].get("row_count", 0)

        # Prepare metadata
        total_rows = sum(s.get("row_count", 0) for s in table_stats.values())
        total_size_mb = sum(s.get("size_mb", 0) for s in table_stats.values())

        metadata = {
            "customerUrl": customer_url,  # Customer website URL for branding
            "datasetId": final_state.get("dataset_id", ""),
            "datasetFullName": final_state.get("dataset_full_name", ""),
            "projectId": project_id,
            "agentId": final_state.get("capi_agent_id", ""),  # CAPI Data Agent ID for chat
            "totalRows": total_rows,
            "totalStorageMB": round(total_size_mb, 2),
            "generationTimestamp": job_manager.get_job(job_id).created_at,
            "totalTables": len(schema_data),
            "yaml_file_path": final_state.get("capi_yaml_file", ""),
            "executive_summary": demo_story.get("executive_summary", ""),
            "business_challenges": demo_story.get("business_challenges", []),
            "talking_track": demo_story.get("talking_track", ""),
            "validation_results": validation_results  # FIX: Include validation results for frontend
        }

        logger.info(f"Demo orchestrator completed successfully for job {job_id}")

        # DEBUG: Log what we're returning
        result = {
            "status": "completed",
            "dataset_id": final_state.get("dataset_id", ""),
            "demo_title": demo_story.get("demo_title", ""),
            "golden_queries": golden_queries,
            "schema": schema_data,
            "metadata": metadata
        }
        logger.info(f"Orchestrator returning: status={result['status']}, demo_title={result['demo_title'][:50] if result['demo_title'] else None}, queries={len(result['golden_queries'])}, schema_tables={len(result['schema'])}, metadata_keys={list(result['metadata'].keys())}")

        return result

    except Exception as e:
        logger.error(f"Demo orchestrator failed for job {job_id}: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e)
        }
