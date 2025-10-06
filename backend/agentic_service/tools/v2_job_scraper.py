"""
Job Posting Scraper for Research Agent V2.
Analyzes company job postings to detect actual tech stack and data infrastructure.
"""
import asyncio
import logging
import re
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin
from collections import Counter

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class JobPostingScraper:
    """Scraper for company job postings to detect technology stack."""

    def __init__(self, max_jobs: int = 20):
        """
        Initialize job scraper.

        Args:
            max_jobs: Maximum number of job postings to analyze
        """
        self.max_jobs = max_jobs

        # Common careers page patterns
        self.careers_patterns = [
            '/careers', '/jobs', '/opportunities', '/hiring',
            '/join-us', '/work-with-us', '/team', '/about/careers'
        ]

        # Technology keywords to extract
        self.tech_keywords = {
            # Cloud Providers
            'cloud': ['AWS', 'GCP', 'Google Cloud', 'Azure', 'Cloud Platform', 'EC2', 'S3', 'Lambda'],

            # Data Warehouses & Databases
            'data_warehouse': ['BigQuery', 'Snowflake', 'Redshift', 'Databricks', 'Synapse'],
            'databases': ['PostgreSQL', 'MySQL', 'MongoDB', 'Cassandra', 'DynamoDB',
                         'Redis', 'Elasticsearch', 'Neo4j', 'Oracle', 'SQL Server'],

            # Data Processing & ETL
            'data_processing': ['Spark', 'Hadoop', 'Airflow', 'dbt', 'Fivetran', 'Talend',
                               'Kafka', 'Pub/Sub', 'Kinesis', 'Dataflow', 'Flink'],

            # Analytics & BI
            'analytics': ['Looker', 'Tableau', 'Power BI', 'Metabase', 'Superset',
                         'Mode', 'Sigma', 'ThoughtSpot', 'Qlik'],

            # ML/AI Platforms
            'ml_ai': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Vertex AI', 'SageMaker',
                     'MLflow', 'Kubeflow', 'H2O', 'DataRobot'],

            # Programming Languages
            'languages': ['Python', 'SQL', 'Java', 'Scala', 'R', 'Go', 'JavaScript', 'TypeScript'],

            # Data Engineering Tools
            'data_tools': ['Docker', 'Kubernetes', 'Terraform', 'Git', 'CI/CD',
                          'Jenkins', 'GitHub Actions', 'GitLab'],

            # Data Science & Analytics
            'data_science': ['Pandas', 'NumPy', 'Jupyter', 'scikit-learn', 'XGBoost',
                            'LightGBM', 'statsmodels']
        }

        # Job title patterns for data roles
        self.data_job_titles = [
            'data engineer', 'data scientist', 'data analyst', 'analytics engineer',
            'ml engineer', 'machine learning', 'data architect', 'bi engineer',
            'business intelligence', 'data platform', 'etl', 'pipeline'
        ]

    async def scrape_jobs(
        self,
        base_url: str,
        company_name: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Dict:
        """
        Find and scrape job postings to detect tech stack.

        Args:
            base_url: Company website URL
            company_name: Company name
            session: Optional shared aiohttp session for connection pooling

        Returns:
            Dict with job postings and extracted tech stack
        """
        logger.info(f"Searching for job postings for {company_name}")

        careers_url = await self._find_careers_page(base_url, session)

        if not careers_url:
            logger.info("No careers page found on website")
            return {
                'found': False,
                'careers_url': None,
                'jobs': [],
                'tech_stack_detected': {}
            }

        logger.info(f"Found careers page: {careers_url}")

        # Scrape job listings
        jobs = await self._scrape_job_listings(careers_url, base_url, session)

        if not jobs:
            logger.info("No job listings found")
            return {
                'found': True,
                'careers_url': careers_url,
                'jobs': [],
                'tech_stack_detected': {}
            }

        # Extract data-related jobs
        data_jobs = self._filter_data_jobs(jobs)

        # Extract tech stack from job descriptions
        tech_stack = self._extract_tech_stack(data_jobs)

        logger.info(f"Analyzed {len(data_jobs)} data-related jobs, found {sum(len(v) for v in tech_stack.values())} technologies")

        return {
            'found': True,
            'careers_url': careers_url,
            'total_jobs_found': len(jobs),
            'data_jobs_count': len(data_jobs),
            'jobs': data_jobs[:self.max_jobs],
            'tech_stack_detected': tech_stack,
            'job_titles': [job.get('title', '') for job in data_jobs[:10]]
        }

    async def _find_careers_page(
        self,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Optional[str]:
        """Try to find the careers/jobs page."""
        parsed = urlparse(base_url)

        # Use provided session or create temporary one
        if session:
            session_ctx = None
            fetch_session = session
        else:
            session_ctx = aiohttp.ClientSession()
            fetch_session = await session_ctx.__aenter__()

        try:
            # Try common career page patterns
            for pattern in self.careers_patterns:
                test_url = f"{parsed.scheme}://{parsed.netloc}{pattern}"
                if await self._url_exists(fetch_session, test_url):
                    return test_url

            # Try to find from homepage
            try:
                async with fetch_session.get(
                    base_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={'User-Agent': 'Mozilla/5.0'}
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Look for career links
                        for link in soup.find_all('a', href=True):
                            text = link.get_text().lower()
                            href = link['href'].lower()

                            if any(word in text or word in href for word in ['career', 'job', 'hiring', 'join']):
                                full_url = urljoin(base_url, link['href'])
                                if await self._url_exists(fetch_session, full_url):
                                    return full_url
            except Exception as e:
                logger.debug(f"Failed to search homepage for careers link: {e}")
        finally:
            # Close session if we created it
            if session_ctx:
                await session_ctx.__aexit__(None, None, None)

        return None

    async def _url_exists(self, session: aiohttp.ClientSession, url: str) -> bool:
        """Check if URL exists."""
        try:
            async with session.head(
                url,
                timeout=aiohttp.ClientTimeout(total=5),
                headers={'User-Agent': 'Mozilla/5.0'}
            ) as response:
                return response.status in [200, 301, 302]
        except:
            return False

    async def _scrape_job_listings(
        self,
        careers_url: str,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> List[Dict]:
        """Scrape job listings from careers page."""
        jobs = []

        try:
            # Use provided session or create temporary one
            if session:
                session_ctx = None
                fetch_session = session
            else:
                session_ctx = aiohttp.ClientSession()
                fetch_session = await session_ctx.__aenter__()

            try:
                async with fetch_session.get(
                    careers_url,
                    timeout=aiohttp.ClientTimeout(total=15),
                    headers={'User-Agent': 'Mozilla/5.0'}
                ) as response:
                    if response.status != 200:
                        return jobs

                    html = await response.text()
            finally:
                # Close session if we created it
                if session_ctx:
                    await session_ctx.__aexit__(None, None, None)

            soup = BeautifulSoup(html, 'html.parser')

            # Look for job listings in common patterns
            job_containers = (
                soup.find_all('div', class_=re.compile(r'job|position|opening', re.I)) or
                soup.find_all('li', class_=re.compile(r'job|position|opening', re.I)) or
                soup.find_all('article', class_=re.compile(r'job|position', re.I)) or
                soup.find_all('a', href=re.compile(r'job|position|career', re.I))
            )

            for container in job_containers[:50]:  # Limit to first 50 found
                # Try to extract title
                title_elem = (
                    container.find('h2') or
                    container.find('h3') or
                    container.find(class_=re.compile(r'title|name', re.I)) or
                    container
                )

                title = title_elem.get_text(strip=True) if title_elem else ''

                if not title or len(title) > 200:  # Skip if no title or too long
                    continue

                # Try to get job link
                link_elem = container.find('a', href=True) if container.name != 'a' else container
                job_url = urljoin(base_url, link_elem['href']) if link_elem and link_elem.get('href') else None

                # Try to get description
                description = ''
                desc_elem = container.find(class_=re.compile(r'description|summary', re.I))
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:500]
                elif container.name != 'a':
                    description = container.get_text(strip=True)[:500]

                jobs.append({
                    'title': title,
                    'url': job_url,
                    'description': description
                })

            # Deduplicate by title
            seen_titles = set()
            unique_jobs = []
            for job in jobs:
                if job['title'] and job['title'] not in seen_titles:
                    seen_titles.add(job['title'])
                    unique_jobs.append(job)

            return unique_jobs

        except Exception as e:
            logger.error(f"Failed to scrape job listings: {e}")
            return jobs

    def _filter_data_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs to only data-related positions."""
        data_jobs = []

        for job in jobs:
            title_lower = job.get('title', '').lower()
            desc_lower = job.get('description', '').lower()

            # Check if job title matches data roles
            if any(keyword in title_lower for keyword in self.data_job_titles):
                job['is_data_role'] = True
                data_jobs.append(job)
            # Or if description heavily mentions data keywords
            elif desc_lower:
                data_keywords = ['data', 'analytics', 'sql', 'warehouse', 'pipeline', 'etl']
                matches = sum(1 for kw in data_keywords if kw in desc_lower)
                if matches >= 3:
                    job['is_data_role'] = True
                    data_jobs.append(job)

        return data_jobs

    def _extract_tech_stack(self, jobs: List[Dict]) -> Dict[str, List[str]]:
        """Extract technology stack from job descriptions."""
        all_text = ' '.join([
            job.get('title', '') + ' ' + job.get('description', '')
            for job in jobs
        ])

        tech_stack = {}

        for category, keywords in self.tech_keywords.items():
            found = []
            for tech in keywords:
                # Use word boundaries for accurate matching
                if re.search(r'\b' + re.escape(tech) + r'\b', all_text, re.IGNORECASE):
                    found.append(tech)

            if found:
                tech_stack[category] = sorted(list(set(found)))

        return tech_stack
