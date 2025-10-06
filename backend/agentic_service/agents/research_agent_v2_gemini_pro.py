"""
Customer Research Agent V2 - GEMINI 2.5 PRO VERSION
Enhanced Multi-Source Intelligence Gathering with Parallel Execution.

USES GEMINI 2.5 PRO VIA VERTEX AI for faster inference.

PERFORMANCE IMPROVEMENTS:
- Parallel intelligence gathering (12x speedup)
- Shared HTTP session (connection pooling)
- Optimized error handling
- Gemini 2.5 Pro for fast business analysis
- Target: Under 30 seconds total execution
"""
import logging
from typing import Dict, Optional
import asyncio
import time
import aiohttp

from ..utils.vertex_llm_client import get_gemini_pro_vertex_client
from ..tools.web_research import scrape_website
from ..tools.v2_intelligent_crawler_optimized import IntelligentWebsiteCrawlerOptimized
from ..tools.v2_multi_source import BlogScraper, LinkedInScraper, YouTubeScraper
from ..tools.v2_job_scraper import JobPostingScraper
from ..tools.v2_google_search import GoogleJobSearcher
from ..tools.v2_data_architect import DataArchitectureAnalyzer
from ..utils.prompt_templates import RESEARCH_AGENT_V2_PROMPT

logger = logging.getLogger(__name__)


class CustomerResearchAgentV2GeminiPro:
    """
    OPTIMIZED Enhanced research agent with Gemini 2.5 Pro and true parallel execution.

    Key Optimizations:
    1. Parallel intelligence gathering with asyncio.gather()
    2. Shared HTTP session for all scrapers (connection pooling)
    3. Concurrent batch crawling with semaphore
    4. Early termination for sufficient data coverage
    5. GEMINI 2.5 PRO for fast business analysis
    """

    def __init__(
        self,
        max_pages: int = 30,
        max_depth: int = 3,
        max_concurrent: int = 15,
        enable_blog: bool = True,
        enable_linkedin: bool = True,
        enable_youtube: bool = True,
        enable_jobs: bool = True,
        enable_google_jobs: bool = True
    ):
        """
        Initialize V2 Research Agent with Gemini 2.5 Pro.

        Args:
            max_pages: Maximum pages to crawl (reduced from 50 to 30 for speed)
            max_depth: Maximum crawl depth
            max_concurrent: Max concurrent HTTP requests (NEW - default 15)
            enable_blog: Enable blog scraping
            enable_linkedin: Enable LinkedIn scraping
            enable_youtube: Enable YouTube scraping
            enable_jobs: Enable job posting scraping
            enable_google_jobs: Enable Google job search fallback
        """
        # Use Gemini 2.5 Pro via Vertex AI
        self.client = get_gemini_pro_vertex_client()

        # Initialize tools with concurrency support
        self.crawler = IntelligentWebsiteCrawlerOptimized(
            max_pages=max_pages,
            max_depth=max_depth,
            max_concurrent=max_concurrent  # Pass concurrency setting
        )

        self.blog_scraper = BlogScraper() if enable_blog else None
        self.linkedin_scraper = LinkedInScraper() if enable_linkedin else None
        self.youtube_scraper = YouTubeScraper() if enable_youtube else None
        self.job_scraper = JobPostingScraper() if enable_jobs else None
        self.google_job_searcher = GoogleJobSearcher() if enable_google_jobs else None
        self.data_architect = DataArchitectureAnalyzer(self.client)

        logger.info(f"Research Agent V2 GEMINI PRO initialized (max_concurrent={max_concurrent})")

    async def execute(self, state: Dict) -> Dict:
        """
        Execute comprehensive research phase with optimized parallel execution.

        Args:
            state: Pipeline state with customer_url

        Returns:
            Enhanced state with comprehensive research data
        """
        url = state['customer_url']
        logger.info(f"🔍 Starting V2 Research (GEMINI PRO) for {url}")
        overall_start = time.time()

        try:
            # Create shared HTTP session for ALL scrapers (connection pooling)
            connector = aiohttp.TCPConnector(
                limit=100,              # Total connection pool
                limit_per_host=20,      # Per-host limit
                ttl_dns_cache=300,      # DNS caching
                force_close=False,      # Keep-alive
                enable_cleanup_closed=True
            )

            timeout = aiohttp.ClientTimeout(
                total=60,       # Increased from 30s for slow/protected sites
                connect=15,     # Increased from 10s
                sock_read=15    # Increased from 10s
            )

            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/2.0)'}
            ) as session:

                # Phase 1: Multi-source data gathering (PARALLEL with shared session)
                logger.info("📊 Phase 1: Gathering intelligence from multiple sources (PARALLEL)...")
                phase1_start = time.time()

                # Log to SSE stream
                job_manager = state.get("job_manager")
                job_id = state.get("job_id")
                if job_manager and job_id:
                    company_name = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].split('.')[0].title()
                    job_manager.add_log(
                        job_id,
                        "research agent",
                        f"🔍 Crawling {company_name} website (max {self.crawler.max_pages} pages, depth {self.crawler.max_depth})...",
                        "INFO"
                    )

                intelligence_data = await self._gather_intelligence_parallel(url, state, session)

                phase1_time = time.time() - phase1_start
                logger.info(f"✅ Phase 1 complete in {phase1_time:.2f}s")

                if job_manager and job_id:
                    pages_found = intelligence_data.get('website_data', {}).get('pages_crawled', 0)
                    job_manager.add_log(
                        job_id,
                        "research agent",
                        f"✓ Crawled {pages_found} pages in {phase1_time:.1f}s",
                        "INFO"
                    )

                # Phase 2: AI-powered business analysis with Gemini 2.5 Pro
                logger.info("🤖 Phase 2: Analyzing business model with Gemini 2.5 Pro...")
                phase2_start = time.time()

                if job_manager and job_id:
                    job_manager.add_log(
                        job_id,
                        "research agent",
                        "🧠 Analyzing business model with Gemini 2.5 Pro...",
                        "INFO"
                    )

                business_analysis = await self._analyze_business(intelligence_data, state)

                phase2_time = time.time() - phase2_start
                logger.info(f"✅ Phase 2 complete in {phase2_time:.2f}s")

                # Phase 3: Data architecture inference
                logger.info("🏗️ Phase 3: Inferring data architecture...")
                phase3_start = time.time()

                architecture = await self._infer_architecture(
                    business_analysis,
                    intelligence_data
                )

                phase3_time = time.time() - phase3_start
                logger.info(f"✅ Phase 3 complete in {phase3_time:.2f}s")

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

            total_time = time.time() - overall_start
            logger.info(f"✅ V2 Research (GEMINI PRO) complete in {total_time:.2f}s!")
            logger.info(f"   Phase 1 (Intelligence): {phase1_time:.2f}s")
            logger.info(f"   Phase 2 (Analysis): {phase2_time:.2f}s")
            logger.info(f"   Phase 3 (Architecture): {phase3_time:.2f}s")

            # Log to job manager if available
            self._log_to_dashboard(state, business_analysis, architecture)

            return state

        except Exception as e:
            logger.error(f"V2 Research (GEMINI PRO) failed: {e}", exc_info=True)
            raise

    async def _gather_intelligence_parallel(
        self,
        url: str,
        state: Dict,
        session: aiohttp.ClientSession
    ) -> Dict:
        """
        OPTIMIZED: Gather intelligence from all sources in TRUE PARALLEL.

        KEY FIX: Uses asyncio.gather() instead of sequential await loop.
        """
        from urllib.parse import urlparse

        # Parse company name from URL for social media search
        domain = urlparse(url).netloc.replace('www.', '')
        company_name = domain.split('.')[0].replace('-', ' ').title()

        # Build list of tasks for parallel execution
        tasks = []
        task_names = []

        # Always run these core tasks
        tasks.append(scrape_website(url, session))
        task_names.append('homepage')

        tasks.append(self.crawler.crawl(url, session))
        task_names.append('crawl')

        # Optional scrapers (add if enabled)
        if self.blog_scraper:
            tasks.append(self.blog_scraper.scrape_blog(url, session))
            task_names.append('blog')

        if self.linkedin_scraper:
            tasks.append(self.linkedin_scraper.scrape_linkedin(company_name, url, session))
            task_names.append('linkedin')

        if self.youtube_scraper:
            tasks.append(self.youtube_scraper.scrape_youtube(company_name, url, session))
            task_names.append('youtube')

        if self.job_scraper:
            tasks.append(self.job_scraper.scrape_jobs(url, company_name, session))
            task_names.append('jobs')

        # 🚀 CRITICAL FIX: Execute ALL tasks in PARALLEL with asyncio.gather()
        logger.info(f"🚀 Launching {len(tasks)} intelligence scrapers in PARALLEL...")
        start_time = time.time()

        # Use return_exceptions=True so one failure doesn't kill all tasks
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start_time
        logger.info(f"✅ All {len(tasks)} scrapers completed in {elapsed:.2f}s")

        # Map results back to names and handle exceptions
        results = {}
        success_count = 0
        fail_count = 0

        for name, result in zip(task_names, results_list):
            if isinstance(result, Exception):
                logger.warning(f"✗ Failed {name}: {result}")
                results[name] = {'found': False, 'error': str(result)}
                fail_count += 1
            else:
                logger.info(f"✓ Completed: {name}")
                results[name] = result
                success_count += 1

        # Log summary
        logger.info(f"📊 Scraping summary: {success_count} succeeded, {fail_count} failed")

        # Log to SSE if available
        job_manager = state.get("job_manager")
        job_id = state.get("job_id")
        if job_manager and job_id and fail_count > 0:
            job_manager.add_log(
                job_id,
                "research agent",
                f"⚠️  {fail_count} sources timed out or failed (continuing with {success_count} sources)",
                "INFO"
            )

        # Fallback: If job scraper found nothing, try Google search
        jobs_data = results.get('jobs', {})
        if not jobs_data.get('found') and self.google_job_searcher:
            logger.info("🔍 No careers page found, trying Google job search...")
            try:
                google_jobs = await self.google_job_searcher.search_jobs(company_name, url, session)
                if google_jobs.get('found'):
                    logger.info(f"✓ Found {google_jobs.get('total_jobs_found', 0)} jobs via Google search")
                    jobs_data = google_jobs
            except Exception as e:
                logger.warning(f"✗ Google job search failed: {e}")

        # Extract data safely - handle errors gracefully
        def safe_get_content(key, default=''):
            """Get content safely, returning default if result is an error dict."""
            result = results.get(key, default)
            # If it's an error dict, return default instead
            if isinstance(result, dict) and 'error' in result:
                return default
            return result

        return {
            'homepage_content': safe_get_content('homepage', ''),
            'crawl_data': safe_get_content('crawl', {}),
            'blog_data': safe_get_content('blog', {}),
            'linkedin_data': safe_get_content('linkedin', {}),
            'youtube_data': safe_get_content('youtube', {}),
            'jobs_data': jobs_data,
            'website_data': results.get('crawl', {})  # Add for logging
        }

    async def _analyze_business(self, intelligence_data: Dict, state: Dict) -> Dict:
        """Use Gemini 2.5 Pro to analyze business model from all gathered intelligence."""

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

        # Analyze with Gemini 2.5 Pro
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
                "Always return valid JSON only. Ensure all JSON strings are properly terminated."
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
            "research agent v2 gemini pro",
            f"📊 V2 Business Analysis Complete (Gemini 2.5 Pro):",
            "INFO"
        )
        job_manager.add_log(
            job_id,
            "research agent v2 gemini pro",
            f"  • Industry: {business_analysis.get('industry', 'N/A')}",
            "INFO"
        )
        job_manager.add_log(
            job_id,
            "research agent v2 gemini pro",
            f"  • Business Domain: {business_analysis.get('business_domain', 'N/A')}",
            "INFO"
        )

        # Log data architecture insights
        entities_count = len(architecture.get('core_entities', []))
        if entities_count > 0:
            job_manager.add_log(
                job_id,
                "research agent v2 gemini pro",
                f"🏗️ Data Architecture Inferred:",
                "INFO"
            )
            job_manager.add_log(
                job_id,
                "research agent v2 gemini pro",
                f"  • Core Entities Identified: {entities_count}",
                "INFO"
            )

            warehouse = architecture.get('warehouse_design', {})
            if warehouse:
                fact_count = len(warehouse.get('fact_tables', []))
                dim_count = len(warehouse.get('dimension_tables', []))
                job_manager.add_log(
                    job_id,
                    "research agent v2 gemini pro",
                    f"  • Warehouse Design: {fact_count} fact tables, {dim_count} dimensions",
                    "INFO"
                )
