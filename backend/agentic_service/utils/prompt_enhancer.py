"""
Prompt Enhancement Utility for Crazy Frog Mode

Injects CE-provided context into agent prompts to create highly customized demos.
"""
from typing import Dict
from agentic_service.models.crazy_frog_request import CrazyFrogProvisioningRequest


def build_crazy_frog_context_block(request: CrazyFrogProvisioningRequest) -> str:
    """
    Build a rich context block from Crazy Frog request to inject into prompts.

    Args:
        request: CrazyFrogProvisioningRequest with CE context

    Returns:
        Formatted context string for prompt injection
    """
    context_parts = []

    # Core use case context (always present)
    context_parts.append("=== CUSTOMER ENGINEER CONTEXT ===")
    context_parts.append(f"\n**USE CASE DETAILS:**\n{request.use_case_context}")

    # Add optional hints if provided
    if request.industry_hint:
        context_parts.append(f"\n**INDUSTRY:** {request.industry_hint}")

    if request.target_persona:
        context_parts.append(f"\n**TARGET AUDIENCE:** {request.target_persona}")
        context_parts.append(f"IMPORTANT: Tailor the demo narrative, terminology, and metrics to resonate with a {request.target_persona}.")

    if request.demo_complexity:
        context_parts.append(f"\n**COMPLEXITY LEVEL:** {request.demo_complexity}")
        if request.demo_complexity.lower() == "advanced":
            context_parts.append("Focus on sophisticated queries: window functions, CTEs, multi-table joins, statistical analysis.")
        elif request.demo_complexity.lower() == "medium":
            context_parts.append("Balance simple and complex queries. Include JOINs, GROUP BY, basic time-series.")
        else:
            context_parts.append("Keep queries straightforward. Focus on basic aggregations and simple filters.")

    if request.special_focus:
        context_parts.append(f"\n**SPECIAL FOCUS:** {request.special_focus}")
        context_parts.append(f"Ensure golden queries and data model emphasize {request.special_focus} scenarios.")

    if request.integrations:
        context_parts.append(f"\n**DATA INTEGRATIONS TO HIGHLIGHT:** {request.integrations}")
        context_parts.append(f"Consider data model entities that would come from: {request.integrations}")

    if request.avoid_topics:
        context_parts.append(f"\n**AVOID THESE TOPICS:** {request.avoid_topics}")
        context_parts.append("DO NOT include scenarios, queries, or data related to the above topics.")

    context_parts.append("\n=== END CUSTOMER ENGINEER CONTEXT ===\n")

    return "\n".join(context_parts)


def enhance_research_prompt(base_prompt: str, crazy_frog_context: str) -> str:
    """Enhance Research Agent prompt with CE context."""
    enhancement = f"""
{crazy_frog_context}

**IMPORTANT:** Use the above CE context to guide your research. Look for aspects of the company
that align with the use case context. Prioritize entities and relationships that support the
scenarios described by the Customer Engineer.

{base_prompt}
"""
    return enhancement


def enhance_demo_story_prompt(base_prompt: str, crazy_frog_context: str) -> str:
    """Enhance Demo Story Agent prompt with CE context."""
    enhancement = f"""
{crazy_frog_context}

**CRITICAL:** The CE context above is your north star. Design the demo story to directly address:
1. The specific business challenges mentioned
2. The target persona's needs and perspective
3. The special focus areas highlighted
4. The complexity level requested

Your golden queries MUST showcase the scenarios the CE wants to demonstrate.

{base_prompt}
"""
    return enhancement


def enhance_data_modeling_prompt(base_prompt: str, crazy_frog_context: str) -> str:
    """Enhance Data Modeling Agent prompt with CE context."""
    enhancement = f"""
{crazy_frog_context}

**SCHEMA DESIGN GUIDANCE:**
- If integrations are mentioned, include entities/fields that would come from those systems
- Structure the schema to support the special focus area (e.g., revenue analytics needs transaction tables)
- Ensure complexity aligns with the CE's requested demo complexity level

{base_prompt}
"""
    return enhancement


def enhance_synthetic_data_prompt(base_prompt: str, crazy_frog_context: str) -> str:
    """Enhance Synthetic Data Generator prompt with CE context."""
    enhancement = f"""
{crazy_frog_context}

**DATA GENERATION GUIDANCE:**
- Embed patterns that illustrate the use case scenarios
- Create data distributions that make the demo insights compelling for the target persona
- If integrations are mentioned, ensure data characteristics match those systems

{base_prompt}
"""
    return enhancement


def enhance_validator_prompt(base_prompt: str, crazy_frog_context: str) -> str:
    """Enhance Demo Validator prompt with CE context."""
    enhancement = f"""
{crazy_frog_context}

**VALIDATION FOCUS:**
- Ensure queries address the use case scenarios
- Verify results are meaningful for the target persona
- Check that complexity matches the CE's requirements

{base_prompt}
"""
    return enhancement


def enhance_capi_instruction_prompt(base_prompt: str, crazy_frog_context: str) -> str:
    """Enhance CAPI Instruction Generator prompt with CE context."""
    enhancement = f"""
{crazy_frog_context}

**SYSTEM INSTRUCTION CUSTOMIZATION:**
- Tailor the agent's role description to the industry and use case
- Include business glossary terms relevant to the target persona
- Ensure golden queries showcase the scenarios the CE wants to demonstrate

{base_prompt}
"""
    return enhancement


def enhance_all_prompts_with_crazy_frog_context(
    base_prompts: Dict[str, str],
    crazy_frog_request: CrazyFrogProvisioningRequest
) -> Dict[str, str]:
    """
    Enhance all agent prompts with Crazy Frog context.

    Args:
        base_prompts: Dictionary of agent names to their base prompts
        crazy_frog_request: The Crazy Frog provisioning request

    Returns:
        Dictionary of agent names to enhanced prompts
    """
    context_block = build_crazy_frog_context_block(crazy_frog_request)

    enhanced_prompts = {}

    # Map agent names to enhancement functions
    enhancers = {
        "research": enhance_research_prompt,
        "demo_story": enhance_demo_story_prompt,
        "data_modeling": enhance_data_modeling_prompt,
        "synthetic_data": enhance_synthetic_data_prompt,
        "validator": enhance_validator_prompt,
        "capi_instruction": enhance_capi_instruction_prompt,
    }

    for agent_name, base_prompt in base_prompts.items():
        enhancer = enhancers.get(agent_name)
        if enhancer:
            enhanced_prompts[agent_name] = enhancer(base_prompt, context_block)
        else:
            # If no specific enhancer, just prepend context
            enhanced_prompts[agent_name] = f"{context_block}\n\n{base_prompt}"

    return enhanced_prompts
