"""
Customer Research Agent V2 - Enhanced Multi-Source Intelligence Gathering.
Acts as a Data Architect Detective to deeply understand customer's business and data ecosystem.
"""
import logging
from typing import Dict
import asyncio

from ..utils.vertex_llm_client import get_claude_vertex_client
from ..tools.web_research import scrape_website
from ..tools.v2_intelligent_crawler import IntelligentWebsiteCrawler
from ..tools.v2_multi_source import BlogScraper, LinkedInScraper, YouTubeScraper
from ..tools.v2_job_scraper import JobPostingScraper
from ..tools.v2_google_search import GoogleJobSearcher
from ..tools.v2_data_architect import DataArchitectureAnalyzer
from ..utils.prompt_templates import RESEARCH_AGENT_V2_PROMPT

logger = logging.getLogger(__name__)


class CustomerResearchAgentV2:
    """
    Enhanced research agent with multi-source intelligence gathering.

    Capabilities:
    - Intelligent website crawling (sitemap, navigation, categorization)
    - Blog/news analysis for technology stack
    - LinkedIn company page scraping
    - YouTube channel analysis
    - AI-powered data architecture inference
    """

    def __init__(
        self,
        max_pages: int = 50,
        max_depth: int = 3,
        enable_blog: bool = True,
        enable_linkedin: bool = True,
        enable_youtube: bool = True,
        enable_jobs: bool = True,
        enable_google_jobs: bool = True
    ):
        """
        Initialize V2 Research Agent.

        Args:
            max_pages: Maximum pages to crawl
            max_depth: Maximum crawl depth
            enable_blog: Enable blog scraping
            enable_linkedin: Enable LinkedIn scraping
            enable_youtube: Enable YouTube scraping
            enable_jobs: Enable job posting scraping
            enable_google_jobs: Enable Google job search fallback
        """
        # Use Claude via Vertex AI (no external API key needed!)
        self.client = get_claude_vertex_client()

        # Initialize tools
        self.crawler = IntelligentWebsiteCrawler(
            max_pages=max_pages,
            max_depth=max_depth
        )
        self.blog_scraper = BlogScraper() if enable_blog else None
        self.linkedin_scraper = LinkedInScraper() if enable_linkedin else None
        self.youtube_scraper = YouTubeScraper() if enable_youtube else None
        self.job_scraper = JobPostingScraper() if enable_jobs else None
        self.google_job_searcher = GoogleJobSearcher() if enable_google_jobs else None
        self.data_architect = DataArchitectureAnalyzer(self.client)

        logger.info("Research Agent V2 initialized with enhanced capabilities")

    async def execute(self, state: Dict) -> Dict:
        """
        Execute comprehensive research phase.

        Args:
            state: Pipeline state with customer_url

        Returns:
            Enhanced state with comprehensive research data
        """
        url = state['customer_url']
        logger.info(f"🔍 Starting V2 Research for {url}")

        try:
            # Phase 1: Multi-source data gathering (parallel)
            logger.info("📊 Phase 1: Gathering intelligence from multiple sources...")

            intelligence_data = await self._gather_intelligence(url, state)

            # Phase 2: AI-powered business analysis
            logger.info("🤖 Phase 2: Analyzing business model with Claude...")

            business_analysis = await self._analyze_business(intelligence_data, state)

            # Phase 3: Data architecture inference
            logger.info("🏗️ Phase 3: Inferring data architecture...")

            architecture = await self._infer_architecture(
                business_analysis,
                intelligence_data
            )

            # Update state with comprehensive results
            state["customer_info"] = business_analysis
            state["business_domain"] = business_analysis.get("business_domain")
            state["industry"] = business_analysis.get("industry")
            state["key_entities"] = [e["name"] for e in business_analysis.get("key_entities", [])]

            # V2-specific additions
            state["v2_intelligence"] = {
                "website_crawl": intelligence_data.get("crawl_data"),
                "blog_data": intelligence_data.get("blog_data"),
                "linkedin_data": intelligence_data.get("linkedin_data"),
                "youtube_data": intelligence_data.get("youtube_data"),
                "jobs_data": intelligence_data.get("jobs_data"),
                "data_architecture": architecture
            }

            logger.info("✅ V2 Research complete!")

            # Log to job manager if available
            self._log_to_dashboard(state, business_analysis, architecture)

            return state

        except Exception as e:
            logger.error(f"V2 Research failed: {e}", exc_info=True)
            raise

    async def _gather_intelligence(self, url: str, state: Dict) -> Dict:
        """Gather intelligence from all sources in parallel."""

        # Parse company name from URL for social media search
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace('www.', '')
        company_name = domain.split('.')[0].replace('-', ' ').title()

        # Run all scrapers in parallel
        tasks = {
            'homepage': scrape_website(url),  # Quick homepage scrape
            'crawl': self.crawler.crawl(url)  # Deep crawl
        }

        if self.blog_scraper:
            tasks['blog'] = self.blog_scraper.scrape_blog(url)

        if self.linkedin_scraper:
            tasks['linkedin'] = self.linkedin_scraper.scrape_linkedin(company_name, url)

        if self.youtube_scraper:
            tasks['youtube'] = self.youtube_scraper.scrape_youtube(company_name, url)

        if self.job_scraper:
            tasks['jobs'] = self.job_scraper.scrape_jobs(url, company_name)

        # Execute all in parallel
        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
                logger.info(f"✓ Completed: {name}")
            except Exception as e:
                logger.warning(f"✗ Failed {name}: {e}")
                results[name] = {'found': False, 'error': str(e)}

        # Fallback: If job scraper found nothing, try Google search
        jobs_data = results.get('jobs', {})
        if not jobs_data.get('found') and self.google_job_searcher:
            logger.info("🔍 No careers page found, trying Google job search...")
            try:
                google_jobs = await self.google_job_searcher.search_jobs(company_name, url)
                if google_jobs.get('found'):
                    logger.info(f"✓ Found {google_jobs.get('total_jobs_found', 0)} jobs via Google search")
                    jobs_data = google_jobs
            except Exception as e:
                logger.warning(f"✗ Google job search failed: {e}")

        return {
            'homepage_content': results.get('homepage', ''),
            'crawl_data': results.get('crawl', {}),
            'blog_data': results.get('blog', {}),
            'linkedin_data': results.get('linkedin', {}),
            'youtube_data': results.get('youtube', {}),
            'jobs_data': jobs_data
        }

    async def _analyze_business(self, intelligence_data: Dict, state: Dict) -> Dict:
        """Use Claude to analyze business model from all gathered intelligence."""

        # Combine all content for analysis
        homepage = intelligence_data.get('homepage_content', '')
        crawl = intelligence_data.get('crawl_data', {})
        blog = intelligence_data.get('blog_data', {})

        # Build comprehensive content summary
        content_summary = self._build_content_summary(
            homepage, crawl, blog
        )

        # Get crazy frog context (empty string if not present)
        crazy_frog_context = state.get("crazy_frog_context", "")

        # Analyze with Claude
        prompt = RESEARCH_AGENT_V2_PROMPT.format(
            content_summary=content_summary,
            crawl_summary=self._format_crawl_summary(crawl),
            blog_summary=self._format_blog_summary(blog),
            crazy_frog_context=crazy_frog_context
        )

        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=8192,
            system_instruction=(
                "You are a senior business analyst and customer engineer expert at understanding "
                "company business models from comprehensive web research. You analyze websites, blogs, "
                "and all available intelligence to create detailed business profiles. "
                "Always return valid JSON only."
            )
        )

        return self.client.parse_json_response(response_text)

    async def _infer_architecture(
        self,
        business_analysis: Dict,
        intelligence_data: Dict
    ) -> Dict:
        """Infer complete data architecture."""

        research_data = {
            'business_analysis': business_analysis,
            'website_crawl': intelligence_data.get('crawl_data', {}),
            'blog_data': intelligence_data.get('blog_data', {}),
            'jobs_data': intelligence_data.get('jobs_data', {})
        }

        architecture = await self.data_architect.infer_architecture(research_data)
        return architecture

    def _build_content_summary(
        self,
        homepage: str,
        crawl_data: Dict,
        blog_data: Dict
    ) -> str:
        """Build comprehensive content summary for analysis."""

        # Start with homepage
        summary = f"### HOMEPAGE CONTENT\n{homepage[:5000]}\n\n"

        # Add categorized page content from crawl
        if crawl_data and crawl_data.get('pages'):
            summary += "### WEBSITE STRUCTURE\n"

            # Group by category
            by_category = {}
            for page in crawl_data['pages']:
                cat = page['category']
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(page)

            # Add content from each category
            for category, pages in by_category.items():
                summary += f"\n#### {category.upper()} PAGES:\n"
                for page in pages[:3]:  # Top 3 per category
                    summary += f"- {page['title']}: {page['content'][:500]}\n"

        # Add blog insights
        if blog_data and blog_data.get('articles'):
            summary += "\n### BLOG/NEWS ARTICLES\n"
            for article in blog_data['articles'][:5]:  # Top 5 articles
                summary += f"- {article['title']}: {article.get('content', '')[:300]}\n"

        # Truncate if too long
        if len(summary) > 20000:
            summary = summary[:20000] + "\n\n[Content truncated...]"

        return summary

    def _format_crawl_summary(self, crawl_data: Dict) -> str:
        """Format crawl data summary."""
        if not crawl_data:
            return "No crawl data available"

        return f"""
- Pages Crawled: {crawl_data.get('pages_crawled', 0)}
- Categories: {', '.join(crawl_data.get('categories', {}).keys())}
- Total Content Words: {crawl_data.get('total_content_words', 0):,}
"""

    def _format_blog_summary(self, blog_data: Dict) -> str:
        """Format blog data summary."""
        if not blog_data or not blog_data.get('found'):
            return "No blog found"

        return f"""
- Blog URL: {blog_data.get('blog_url', 'N/A')}
- Articles Found: {blog_data.get('articles_count', 0)}
- Technologies Mentioned: {', '.join(blog_data.get('technologies_mentioned', [])[:10])}
- Topics: {', '.join(blog_data.get('topics', []))}
"""

    def _log_to_dashboard(self, state: Dict, business_analysis: Dict, architecture: Dict):
        """Log detailed results to CE Dashboard."""
        if "job_manager" not in state or "job_id" not in state:
            return

        job_manager = state["job_manager"]
        job_id = state["job_id"]

        # Log business analysis
        job_manager.add_log(
            job_id,
            "research agent v2",
            f"📊 V2 Business Analysis Complete:",
            "INFO"
        )
        job_manager.add_log(
            job_id,
            "research agent v2",
            f"  • Industry: {business_analysis.get('industry', 'N/A')}",
            "INFO"
        )
        job_manager.add_log(
            job_id,
            "research agent v2",
            f"  • Business Domain: {business_analysis.get('business_domain', 'N/A')}",
            "INFO"
        )

        # Log data architecture insights
        entities_count = len(architecture.get('core_entities', []))
        if entities_count > 0:
            job_manager.add_log(
                job_id,
                "research agent v2",
                f"🏗️ Data Architecture Inferred:",
                "INFO"
            )
            job_manager.add_log(
                job_id,
                "research agent v2",
                f"  • Core Entities Identified: {entities_count}",
                "INFO"
            )

            warehouse = architecture.get('warehouse_design', {})
            if warehouse:
                fact_count = len(warehouse.get('fact_tables', []))
                dim_count = len(warehouse.get('dimension_tables', []))
                job_manager.add_log(
                    job_id,
                    "research agent v2",
                    f"  • Warehouse Design: {fact_count} fact tables, {dim_count} dimensions",
                    "INFO"
                )
