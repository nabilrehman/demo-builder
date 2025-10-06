"""
Agent Model Configuration Registry.

This module provides centralized configuration for selecting which LLM model
(Gemini vs Claude) to use for each agent in the pipeline.

Based on benchmark results from:
- benchmarks/AGENT_SELECTOR_GUIDE.md
- benchmarks/RESEARCH_V2_GEMINI_PRO_RESULTS.md
- benchmarks/DEMO_STORY_GEMINI_PRO_RESULTS.md
- benchmarks/CAPI_INSTRUCTION_GEMINI_PRO_RESULTS.md
"""
import os
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# AGENT VARIANT REGISTRY
# ============================================================================
# Maps agent name → model type → (module_name, class_name)

AGENT_VARIANTS = {
    "research": {
        "gemini": ("research_agent_v2_gemini_pro", "CustomerResearchAgentV2GeminiPro"),
        "claude": ("research_agent_v2_optimized", "CustomerResearchAgentV2Optimized"),
    },
    "demo_story": {
        "gemini": ("demo_story_agent_gemini_pro", "DemoStoryAgentGeminiPro"),
        "claude": ("demo_story_agent", "DemoStoryAgent"),
    },
    "data_modeling": {
        "gemini": ("data_modeling_agent_gemini_pro", "DataModelingAgentGeminiPro"),
        "claude": ("data_modeling_agent", "DataModelingAgent"),
    },
    "capi": {
        "gemini": ("capi_instruction_generator_gemini_pro", "CAPIInstructionGeneratorGeminiPro"),
        "claude": ("capi_instruction_generator_optimized", "CAPIInstructionGeneratorOptimized"),
    },
}

# ============================================================================
# DEFAULT CONFIGURATION (Based on Benchmark Results)
# ============================================================================

DEFAULT_CONFIG = {
    # Research: Gemini 2x faster (131s vs 263s), acceptable quality (5 entities vs 8)
    # Trade-off: Speed over thoroughness (good for demos/dev)
    # Benchmark: benchmarks/RESEARCH_V2_GEMINI_PRO_RESULTS.md
    "research": "gemini",

    # Demo Story: Gemini 2.13x faster (43s vs 92s), IDENTICAL quality
    # CLEAR WINNER - no trade-offs (6 queries, 4 scenes, 8 entities)
    # Benchmark: benchmarks/DEMO_STORY_GEMINI_PRO_RESULTS.md
    "demo_story": "gemini",

    # Data Modeling: Claude (user preference)
    # User quote: "lets stick to Claude Sonnet for now"
    # Benchmark: benchmarks/OPTIMIZATION_SUMMARY.md line 56
    "data_modeling": "claude",

    # CAPI: Claude REQUIRED (quality critical)
    # Gemini produces incomplete YAML (missing tables/queries, 49% smaller)
    # Benchmark: benchmarks/CAPI_INSTRUCTION_GEMINI_PRO_RESULTS.md
    # CRITICAL: Gemini output would break CAPI functionality
    "capi": "claude",
}

# ============================================================================
# BENCHMARK METADATA (for documentation and debugging)
# ============================================================================

BENCHMARK_RESULTS = {
    "research": {
        "gemini": {
            "time_seconds": 131.72,
            "entities": 5,
            "data_entities": 5,
            "speedup": "2x faster",
            "pros": ["Fast", "Good for demos", "Cost-effective"],
            "cons": ["Fewer entities than Claude", "Less thorough"],
        },
        "claude": {
            "time_seconds": 262.82,
            "entities": 8,
            "data_entities": 12,
            "speedup": "baseline",
            "pros": ["More thorough", "More entities", "Production quality"],
            "cons": ["2x slower", "Higher cost"],
        },
        "recommendation": "gemini for speed, claude for quality",
        "benchmark_file": "benchmarks/RESEARCH_V2_GEMINI_PRO_RESULTS.md",
    },
    "demo_story": {
        "gemini": {
            "time_seconds": 43.33,
            "queries": 6,
            "scenes": 4,
            "entities": 8,
            "speedup": "2.13x faster",
            "pros": ["Very fast", "Identical quality to Claude", "Clear winner"],
            "cons": ["None - identical output"],
        },
        "claude": {
            "time_seconds": 92.35,
            "queries": 6,
            "scenes": 4,
            "entities": 8,
            "speedup": "baseline",
            "pros": ["Same quality as Gemini"],
            "cons": ["2x slower", "No advantage over Gemini"],
        },
        "recommendation": "gemini (clear winner - same quality, 2x faster)",
        "benchmark_file": "benchmarks/DEMO_STORY_GEMINI_PRO_RESULTS.md",
    },
    "data_modeling": {
        "gemini": {
            "time_seconds": 40,
            "status": "available but not benchmarked",
            "pros": ["Likely similar speed to Claude"],
            "cons": ["Not tested in production"],
        },
        "claude": {
            "time_seconds": 40,
            "status": "user preference",
            "pros": ["User explicitly requested", "Proven quality"],
            "cons": ["None"],
        },
        "recommendation": "claude (user explicitly requested)",
        "benchmark_file": "benchmarks/OPTIMIZATION_SUMMARY.md",
    },
    "capi": {
        "gemini": {
            "time_seconds": 66.56,
            "yaml_size_chars": 12410,
            "yaml_lines": 324,
            "tables_documented": 0,
            "golden_queries": False,
            "speedup": "1.26x faster",
            "status": "INCOMPLETE OUTPUT",
            "pros": ["Slightly faster"],
            "cons": ["Missing tables", "Missing golden queries", "49% smaller YAML", "Would break CAPI"],
        },
        "claude": {
            "time_seconds": 83.94,
            "yaml_size_chars": 24294,
            "yaml_lines": 591,
            "tables_documented": 33,
            "golden_queries": True,
            "speedup": "baseline",
            "status": "complete",
            "pros": ["Complete YAML", "All tables documented", "Golden queries included", "Production ready"],
            "cons": ["17s slower than Gemini"],
        },
        "recommendation": "claude (QUALITY CRITICAL - gemini produces incomplete YAML)",
        "benchmark_file": "benchmarks/CAPI_INSTRUCTION_GEMINI_PRO_RESULTS.md",
    },
}

# ============================================================================
# AGENT CLASS RESOLVER
# ============================================================================

def get_agent_class(agent_name: str, model: str = None):
    """
    Get agent class based on configuration.

    Priority: Environment Variable > Parameter > Default Config

    Args:
        agent_name: One of "research", "demo_story", "data_modeling", "capi"
        model: "gemini" or "claude" (optional - uses env var or default)

    Returns:
        Agent class ready to be instantiated

    Raises:
        ValueError: If agent_name or model is invalid

    Example:
        >>> # Use default (from DEFAULT_CONFIG)
        >>> ResearchAgentClass = get_agent_class("research")
        >>> agent = ResearchAgentClass(max_pages=30, max_depth=2)

        >>> # Override with parameter
        >>> ResearchAgentClass = get_agent_class("research", model="claude")
        >>> agent = ResearchAgentClass(max_pages=30, max_depth=2)

        >>> # Override with environment variable
        >>> # export RESEARCH_AGENT_MODEL=claude
        >>> ResearchAgentClass = get_agent_class("research")
        >>> agent = ResearchAgentClass(max_pages=30, max_depth=2)
    """
    import importlib

    # Validate agent name
    if agent_name not in AGENT_VARIANTS:
        raise ValueError(
            f"Unknown agent '{agent_name}'. "
            f"Valid agents: {list(AGENT_VARIANTS.keys())}"
        )

    # Determine model: env var > parameter > default
    env_var = f"{agent_name.upper()}_AGENT_MODEL"
    env_value = os.getenv(env_var)
    selected_model = (env_value or model or DEFAULT_CONFIG[agent_name]).lower()

    # Validate model
    if selected_model not in AGENT_VARIANTS[agent_name]:
        raise ValueError(
            f"Unknown model '{selected_model}' for agent '{agent_name}'. "
            f"Valid models: {list(AGENT_VARIANTS[agent_name].keys())}"
        )

    # Get module and class name
    module_name, class_name = AGENT_VARIANTS[agent_name][selected_model]

    # Dynamic import
    try:
        module = importlib.import_module(f"agentic_service.agents.{module_name}")
        agent_class = getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import agent: {module_name}.{class_name}")
        raise ImportError(
            f"Could not import agent class '{class_name}' from module '{module_name}'. "
            f"Error: {e}"
        )

    # Log selection for debugging
    source = "env var" if env_value else ("parameter" if model else "default")
    logger.info(
        f"✅ {agent_name.upper()} Agent: {class_name} ({selected_model.upper()}) "
        f"[source: {source}]"
    )

    return agent_class


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_current_config() -> dict:
    """
    Get current agent configuration with environment variable overrides.

    Returns:
        Dictionary mapping agent name to selected model

    Example:
        >>> config = get_current_config()
        >>> print(config)
        {'research': 'gemini', 'demo_story': 'gemini', 'data_modeling': 'claude', 'capi': 'claude'}
    """
    return {
        agent: os.getenv(f"{agent.upper()}_AGENT_MODEL", default).lower()
        for agent, default in DEFAULT_CONFIG.items()
    }


def print_config():
    """
    Print current agent configuration to console (useful for debugging).

    Shows which model is selected for each agent and whether it came from
    environment variable or default configuration.
    """
    config = get_current_config()

    print("\n" + "="*80)
    print("AGENT MODEL CONFIGURATION")
    print("="*80)

    for agent, model in config.items():
        env_var = f"{agent.upper()}_AGENT_MODEL"
        env_value = os.getenv(env_var)

        if env_value:
            source = f" (from ${env_var})"
        else:
            source = " (default)"

        # Add benchmark context
        benchmark = BENCHMARK_RESULTS.get(agent, {}).get(model, {})
        speed_info = benchmark.get("speedup", "")

        print(f"  {agent:20s} → {model:10s}{source:25s} {speed_info}")

    print("="*80)
    print("\nTo override: export <AGENT_NAME>_AGENT_MODEL=<gemini|claude>")
    print("Example: export RESEARCH_AGENT_MODEL=claude")
    print("="*80 + "\n")


def get_benchmark_info(agent_name: str, model: str) -> dict:
    """
    Get benchmark information for a specific agent/model combination.

    Args:
        agent_name: One of "research", "demo_story", "data_modeling", "capi"
        model: "gemini" or "claude"

    Returns:
        Dictionary with benchmark data (speed, quality, pros/cons, etc.)

    Example:
        >>> info = get_benchmark_info("research", "gemini")
        >>> print(f"Speed: {info['time_seconds']}s, Entities: {info['entities']}")
    """
    if agent_name not in BENCHMARK_RESULTS:
        return {}

    if model not in BENCHMARK_RESULTS[agent_name]:
        return {}

    return BENCHMARK_RESULTS[agent_name][model]
