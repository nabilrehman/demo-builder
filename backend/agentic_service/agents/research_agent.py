"""
Customer Research Agent - Uses Claude Sonnet 4.5 via Vertex AI Model Garden.
"""
import logging
from typing import Dict

from ..utils.vertex_llm_client import get_claude_vertex_client
from ..tools.web_research import scrape_website
from ..utils.prompt_templates import RESEARCH_AGENT_PROMPT

logger = logging.getLogger(__name__)


class CustomerResearchAgent:
    """Agent for researching customer business domain."""

    def __init__(self):
        # Use Claude via Vertex AI (no external API key needed!)
        self.client = get_claude_vertex_client()
        logger.info("Research Agent initialized with Claude via Vertex AI")

    async def execute(self, state: Dict) -> Dict:
        """Execute research phase."""
        logger.info(f"Researching {state['customer_url']} with Claude (Vertex AI)")

        try:
            # Scrape website
            website_content = await scrape_website(state["customer_url"])
            logger.info(f"Scraped {len(website_content)} characters")

            # Get crazy frog context (empty string if not present)
            crazy_frog_context = state.get("crazy_frog_context", "")

            # Analyze with Claude via Vertex AI
            analysis = await self._analyze_business(website_content, crazy_frog_context)

            # Update state
            state["customer_info"] = analysis
            state["business_domain"] = analysis.get("business_domain")
            state["industry"] = analysis.get("industry")
            state["key_entities"] = [e["name"] for e in analysis.get("key_entities", [])]

            logger.info(f"Claude analysis complete. Domain: {state['business_domain']}")

            # Log detailed output to CE Dashboard
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]

                # Log business analysis details
                job_manager.add_log(
                    job_id,
                    "research agent",
                    f"📊 Business Analysis Complete:",
                    "INFO"
                )
                job_manager.add_log(
                    job_id,
                    "research agent",
                    f"  • Industry: {analysis.get('industry', 'N/A')}",
                    "INFO"
                )
                job_manager.add_log(
                    job_id,
                    "research agent",
                    f"  • Business Domain: {analysis.get('business_domain', 'N/A')}",
                    "INFO"
                )
                job_manager.add_log(
                    job_id,
                    "research agent",
                    f"  • Company Type: {analysis.get('company_type', 'N/A')}",
                    "INFO"
                )

                # Log key entities
                key_entities = analysis.get("key_entities", [])
                if key_entities:
                    entity_names = ", ".join([e.get("name", "Unknown") for e in key_entities[:5]])
                    job_manager.add_log(
                        job_id,
                        "research agent",
                        f"  • Key Entities Identified: {entity_names}" + ("..." if len(key_entities) > 5 else ""),
                        "INFO"
                    )

                # Log use cases
                use_cases = analysis.get("primary_use_cases", [])
                if use_cases:
                    job_manager.add_log(
                        job_id,
                        "research agent",
                        f"  • Primary Use Cases: {', '.join(use_cases[:3])}" + ("..." if len(use_cases) > 3 else ""),
                        "INFO"
                    )

            return state

        except Exception as e:
            logger.error(f"Research failed: {e}", exc_info=True)
            raise

    async def _analyze_business(self, website_content: str, crazy_frog_context: str = "") -> Dict:
        """Use Claude (via Vertex AI) to analyze business."""
        # Truncate if needed
        max_chars = 15000
        if len(website_content) > max_chars:
            website_content = website_content[:max_chars] + "\n\n[Content truncated...]"

        prompt = RESEARCH_AGENT_PROMPT.format(
            website_content=website_content,
            crazy_frog_context=crazy_frog_context
        )

        # Claude via Vertex AI excels at this complex analysis
        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.2,  # Lower for more consistent analysis
            max_output_tokens=4096,
            system_instruction="You are a business analyst expert at understanding company business models from their websites. Always return valid JSON only."
        )

        return self.client.parse_json_response(response_text)
