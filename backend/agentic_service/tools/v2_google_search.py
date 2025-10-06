"""
Google Job Search for Research Agent V2.
Searches for company job postings on external platforms when careers page not found.
"""
import logging
import asyncio
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class GoogleJobSearcher:
    """
    Searches Google for company job postings on external platforms.
    Useful when company doesn't have a public careers page.
    """

    def __init__(self, max_results: int = 10):
        """
        Initialize Google job searcher.

        Args:
            max_results: Maximum number of job results to return
        """
        self.max_results = max_results

        # Job platforms to look for
        self.job_platforms = [
            'linkedin.com/jobs',
            'indeed.com',
            'glassdoor.com',
            'monster.com',
            'ziprecruiter.com',
            'dice.com',
            'greenhouse.io',
            'lever.co'
        ]

        # Tech keywords to extract from job descriptions
        self.tech_keywords = {
            'cloud': ['AWS', 'GCP', 'Google Cloud', 'Azure', 'Cloud Platform'],
            'data_warehouse': ['BigQuery', 'Snowflake', 'Redshift', 'Databricks', 'Synapse'],
            'databases': ['PostgreSQL', 'MySQL', 'MongoDB', 'Cassandra', 'Redis', 'DynamoDB'],
            'data_processing': ['Spark', 'Hadoop', 'Airflow', 'dbt', 'Kafka', 'Flink', 'Beam'],
            'ml_platforms': ['TensorFlow', 'PyTorch', 'Vertex AI', 'SageMaker', 'MLflow', 'Kubeflow'],
            'data_tools': ['Tableau', 'Looker', 'Power BI', 'Metabase', 'Superset'],
            'languages': ['Python', 'Java', 'Scala', 'Go', 'R', 'SQL', 'JavaScript'],
            'orchestration': ['Kubernetes', 'Docker', 'Terraform', 'Ansible'],
            'streaming': ['Kafka', 'Pub/Sub', 'Kinesis', 'Event Hubs'],
            'version_control': ['Git', 'GitHub', 'GitLab', 'Bitbucket']
        }

    async def search_jobs(
        self,
        company_name: str,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Dict:
        """
        Search Google for company job postings.

        Args:
            company_name: Company name to search for
            base_url: Company website URL (for reference)
            session: Optional shared aiohttp session for connection pooling

        Returns:
            Dict with job search results
        """
        logger.info(f"🔍 Searching Google for {company_name} job postings...")

        # Build search queries
        queries = [
            f'{company_name} data engineer jobs',
            f'{company_name} data analyst jobs',
            f'{company_name} data scientist jobs',
            f'site:linkedin.com/jobs {company_name} data',
            f'site:indeed.com {company_name} data engineer'
        ]

        all_jobs = []
        tech_stack = {}

        # Use provided session or create temporary one
        if session:
            session_ctx = None
            fetch_session = session
        else:
            session_ctx = aiohttp.ClientSession()
            fetch_session = await session_ctx.__aenter__()

        try:
            for query in queries[:3]:  # Top 3 queries to avoid rate limits
                try:
                    jobs = await self._search_query(fetch_session, query, company_name)
                    all_jobs.extend(jobs)
                    await asyncio.sleep(2)  # Respectful delay
                except Exception as e:
                    logger.warning(f"Search failed for '{query}': {e}")
        finally:
            # Close session if we created it
            if session_ctx:
                await session_ctx.__aexit__(None, None, None)

        # Deduplicate by URL
        unique_jobs = {job['url']: job for job in all_jobs}.values()
        unique_jobs = list(unique_jobs)[:self.max_results]

        # Extract tech stack from all job descriptions
        if unique_jobs:
            tech_stack = self._extract_tech_stack(unique_jobs)

        logger.info(f"Found {len(unique_jobs)} unique job postings via Google search")

        return {
            'found': len(unique_jobs) > 0,
            'method': 'google_search',
            'search_queries': queries[:3],
            'jobs': unique_jobs,
            'total_jobs_found': len(unique_jobs),
            'data_jobs_count': len([j for j in unique_jobs if 'data' in j['title'].lower()]),
            'job_titles': [j['title'] for j in unique_jobs],
            'platforms_found': list(set([j['platform'] for j in unique_jobs])),
            'tech_stack_detected': tech_stack
        }

    async def _search_query(self, session: aiohttp.ClientSession, query: str, company_name: str) -> List[Dict]:
        """Perform a single Google search query."""
        # Use Google search (simple HTML scraping - respectful and minimal)
        # Note: For production, use Google Custom Search API for better reliability
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            async with session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    logger.warning(f"Google search returned status {response.status}")
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                jobs = []

                # Parse search results
                for result in soup.find_all('div', class_='g')[:5]:  # Top 5 results per query
                    try:
                        # Extract link
                        link_tag = result.find('a', href=True)
                        if not link_tag:
                            continue

                        url = link_tag['href']
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]

                        # Check if it's a job platform
                        platform = self._identify_platform(url)
                        if not platform:
                            continue

                        # Extract title
                        title_tag = result.find('h3')
                        title = title_tag.get_text() if title_tag else 'Unknown Title'

                        # Extract snippet (description preview)
                        snippet_tag = result.find('div', class_=['VwiC3b', 'yXK7lf'])
                        snippet = snippet_tag.get_text() if snippet_tag else ''

                        jobs.append({
                            'title': title,
                            'url': url,
                            'platform': platform,
                            'snippet': snippet,
                            'company': company_name
                        })

                    except Exception as e:
                        logger.debug(f"Failed to parse search result: {e}")
                        continue

                return jobs

        except Exception as e:
            logger.warning(f"Google search request failed: {e}")
            return []

    def _identify_platform(self, url: str) -> str:
        """Identify which job platform a URL is from."""
        url_lower = url.lower()

        if 'linkedin.com' in url_lower:
            return 'LinkedIn'
        elif 'indeed.com' in url_lower:
            return 'Indeed'
        elif 'glassdoor.com' in url_lower:
            return 'Glassdoor'
        elif 'monster.com' in url_lower:
            return 'Monster'
        elif 'ziprecruiter.com' in url_lower:
            return 'ZipRecruiter'
        elif 'dice.com' in url_lower:
            return 'Dice'
        elif 'greenhouse.io' in url_lower:
            return 'Greenhouse'
        elif 'lever.co' in url_lower:
            return 'Lever'
        else:
            return None

    def _extract_tech_stack(self, jobs: List[Dict]) -> Dict[str, List[str]]:
        """Extract technology stack from job descriptions."""
        tech_found = {}

        # Combine all text from jobs
        all_text = ' '.join([
            f"{job['title']} {job['snippet']}"
            for job in jobs
        ])

        # Search for technologies
        for category, technologies in self.tech_keywords.items():
            found_techs = []
            for tech in technologies:
                # Case-insensitive search
                if tech.lower() in all_text.lower():
                    found_techs.append(tech)

            if found_techs:
                tech_found[category] = sorted(list(set(found_techs)))

        return tech_found
