"""
Intelligent Website Crawler for Research Agent V2.
Discovers and navigates through website structure to gather comprehensive business intelligence.
"""
import asyncio
import logging
from typing import List, Dict, Set, Optional
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class IntelligentWebsiteCrawler:
    """Smart crawler that explores website structure intelligently."""

    def __init__(
        self,
        max_pages: int = 50,
        max_depth: int = 3,
        timeout: int = 10,
        respect_robots: bool = True
    ):
        """
        Initialize crawler.

        Args:
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum depth from root URL
            timeout: Request timeout in seconds
            respect_robots: Whether to respect robots.txt (basic check)
        """
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout = timeout
        self.respect_robots = respect_robots

        # Priority keywords for important pages
        self.priority_keywords = [
            'product', 'service', 'solution', 'platform',
            'about', 'pricing', 'faq', 'documentation', 'docs',
            'api', 'integration', 'feature', 'technology',
            'case-study', 'customer', 'industry',
            'blog', 'news', 'resource', 'insight'
        ]

        # Skip patterns to avoid (removed career/job/contact - we want those!)
        self.skip_patterns = [
            'login', 'signin', 'signup', 'register', 'account',
            'cart', 'checkout', 'privacy', 'terms', 'cookie',
            '.pdf', '.jpg', '.png', '.gif', '.zip', '.exe',
            'mailto:', 'tel:', 'javascript:', '#'
        ]

    async def crawl(self, start_url: str) -> Dict:
        """
        Crawl website starting from URL.

        Args:
            start_url: Starting URL

        Returns:
            Dict with crawl results including pages and metadata
        """
        logger.info(f"Starting intelligent crawl of {start_url}")

        parsed_start = urlparse(start_url)
        base_domain = parsed_start.netloc

        # Initialize tracking
        visited = set()
        to_visit = deque([(start_url, 0)])  # (url, depth)
        pages_data = []
        sitemap_urls = []
        header_footer_links = set()

        # Try to get sitemap first
        sitemap_urls = await self._fetch_sitemap(start_url)
        if sitemap_urls:
            logger.info(f"Found {len(sitemap_urls)} URLs in sitemap")
            # Add high-priority sitemap URLs to queue
            for url in sitemap_urls[:20]:  # Top 20 from sitemap
                to_visit.append((url, 0))

        async with aiohttp.ClientSession() as session:
            # FIRST: Crawl homepage to extract ALL header/footer navigation links
            logger.info("⭐ Extracting header and footer navigation links...")
            homepage_data = await self._fetch_page(session, start_url)
            if homepage_data:
                header_footer_links = self._extract_header_footer_links(
                    start_url, homepage_data['html'], base_domain
                )
                logger.info(f"Found {len(header_footer_links)} header/footer navigation links")

                # Add ALL header/footer links to queue with HIGH priority (depth 0)
                for link in header_footer_links:
                    to_visit.appendleft((link, 0))  # appendleft = high priority
            while to_visit and len(visited) < self.max_pages:
                url, depth = to_visit.popleft()

                # Skip if already visited or too deep
                if url in visited or depth > self.max_depth:
                    continue

                # Skip if different domain
                if urlparse(url).netloc != base_domain:
                    continue

                try:
                    page_data = await self._fetch_page(session, url)
                    if page_data:
                        visited.add(url)
                        pages_data.append({
                            'url': url,
                            'depth': depth,
                            'title': page_data['title'],
                            'content': page_data['content'],
                            'category': self._categorize_page(url, page_data['title']),
                            'word_count': len(page_data['content'].split())
                        })

                        logger.info(f"Crawled ({len(visited)}/{self.max_pages}): {url}")

                        # Extract and prioritize links
                        new_links = self._extract_links(url, page_data['html'], base_domain)
                        prioritized_links = self._prioritize_links(new_links, visited)

                        # Add to queue
                        for link in prioritized_links[:10]:  # Top 10 from each page
                            if link not in visited:
                                to_visit.append((link, depth + 1))

                    # Small delay to be respectful
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.warning(f"Failed to crawl {url}: {e}")
                    continue

        logger.info(f"Crawl complete. Visited {len(visited)} pages")

        return {
            'base_url': start_url,
            'pages_crawled': len(visited),
            'pages': pages_data,
            'categories': self._aggregate_categories(pages_data),
            'total_content_words': sum(p['word_count'] for p in pages_data)
        }

    async def _fetch_sitemap(self, base_url: str) -> List[str]:
        """Try to fetch and parse sitemap.xml"""
        parsed = urlparse(base_url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    sitemap_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        soup = BeautifulSoup(xml_content, 'xml')
                        urls = [loc.text for loc in soup.find_all('loc')]
                        return urls[:50]  # Limit to 50 URLs from sitemap
        except Exception as e:
            logger.debug(f"No sitemap found at {sitemap_url}: {e}")

        return []

    async def _fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        """Fetch and parse a single page."""
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/2.0)'}
            ) as response:
                if response.status != 200:
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Extract title
                title = ''
                if soup.title:
                    title = soup.title.string.strip() if soup.title.string else ''

                # Remove noise
                for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
                    tag.decompose()

                # Extract text
                text = soup.get_text(separator='\n', strip=True)
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                content = '\n'.join(lines)

                return {
                    'title': title,
                    'content': content,
                    'html': html
                }

        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
            return None

    def _extract_links(self, base_url: str, html: str, base_domain: str) -> List[str]:
        """Extract all valid links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for anchor in soup.find_all('a', href=True):
            href = anchor['href']

            # Skip unwanted patterns
            if any(pattern in href.lower() for pattern in self.skip_patterns):
                continue

            # Make absolute URL
            full_url = urljoin(base_url, href)

            # Remove fragment
            full_url, _ = urldefrag(full_url)

            # Only keep same domain
            if urlparse(full_url).netloc == base_domain:
                links.append(full_url)

        return list(set(links))  # Deduplicate

    def _extract_header_footer_links(self, base_url: str, html: str, base_domain: str) -> Set[str]:
        """
        Extract ALL navigation links from header and footer sections.
        These are critical pages that should ALWAYS be crawled.
        """
        soup = BeautifulSoup(html, 'html.parser')
        nav_links = set()

        # Find header, footer, and nav elements
        nav_sections = []
        nav_sections.extend(soup.find_all('header'))
        nav_sections.extend(soup.find_all('footer'))
        nav_sections.extend(soup.find_all('nav'))

        # Also look for common class/id patterns for navigation
        for pattern in ['navigation', 'navbar', 'menu', 'header', 'footer', 'nav']:
            nav_sections.extend(soup.find_all(class_=lambda x: x and pattern in x.lower()))
            nav_sections.extend(soup.find_all(id=lambda x: x and pattern in x.lower()))

        logger.info(f"Found {len(nav_sections)} navigation sections in header/footer")

        # Extract all links from these sections
        for section in nav_sections:
            for anchor in section.find_all('a', href=True):
                href = anchor['href']

                # Be more permissive here - we want ALL nav links including careers, contact, etc.
                # Only skip obvious non-pages
                if any(pattern in href.lower() for pattern in ['.pdf', '.jpg', '.png', '.gif', '.zip', 'mailto:', 'tel:', 'javascript:']):
                    continue

                # Make absolute URL
                full_url = urljoin(base_url, href)

                # Remove fragment
                full_url, _ = urldefrag(full_url)

                # Only keep same domain
                if urlparse(full_url).netloc == base_domain:
                    nav_links.add(full_url)

        return nav_links

    def _prioritize_links(self, links: List[str], visited: Set[str]) -> List[str]:
        """Prioritize links based on importance keywords."""
        scored_links = []

        for link in links:
            if link in visited:
                continue

            score = 0
            link_lower = link.lower()

            # Higher score for priority keywords
            for keyword in self.priority_keywords:
                if keyword in link_lower:
                    score += 10

            # Penalize very long URLs (likely not important)
            if len(link) > 100:
                score -= 5

            # Bonus for shorter paths (closer to root)
            path_depth = link.count('/') - 2  # Subtract protocol //
            score -= path_depth

            scored_links.append((score, link))

        # Sort by score descending
        scored_links.sort(reverse=True, key=lambda x: x[0])

        return [link for _, link in scored_links]

    def _categorize_page(self, url: str, title: str) -> str:
        """Categorize page based on URL and title."""
        combined = (url + ' ' + title).lower()

        categories = {
            'product': ['product', 'solution', 'platform', 'service', 'offering'],
            'pricing': ['pricing', 'plan', 'cost', 'subscription'],
            'documentation': ['doc', 'api', 'developer', 'integration', 'guide'],
            'about': ['about', 'company', 'team', 'mission', 'story'],
            'blog': ['blog', 'article', 'post', 'news'],
            'resources': ['resource', 'insight', 'whitepaper', 'report'],
            'case_study': ['case', 'customer', 'success', 'story'],
            'faq': ['faq', 'question', 'help'],
            'technology': ['technology', 'tech', 'stack', 'infrastructure']
        }

        for category, keywords in categories.items():
            if any(keyword in combined for keyword in keywords):
                return category

        return 'general'

    def _aggregate_categories(self, pages_data: List[Dict]) -> Dict[str, int]:
        """Aggregate page counts by category."""
        categories = {}
        for page in pages_data:
            cat = page['category']
            categories[cat] = categories.get(cat, 0) + 1
        return categories
