"""
Multi-Source Research Tools for V2 Agent.
Scrapes blog posts, LinkedIn company pages, and YouTube channels.
"""
import asyncio
import logging
import os
import re
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BlogScraper:
    """Scraper for company blog/news sections."""

    def __init__(self, max_articles: int = 20):
        """
        Initialize blog scraper.

        Args:
            max_articles: Maximum number of articles to scrape
        """
        self.max_articles = max_articles

        # Common blog URL patterns
        self.blog_patterns = [
            '/blog', '/news', '/insights', '/resources',
            '/articles', '/press', '/updates', '/stories'
        ]

    async def scrape_blog(
        self,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Dict:
        """
        Find and scrape blog/news section.

        Args:
            base_url: Website base URL
            session: Optional shared aiohttp session for connection pooling

        Returns:
            Dict with blog articles and metadata
        """
        logger.info(f"Searching for blog/news section on {base_url}")

        parsed = urlparse(base_url)
        blog_url = None

        # Use provided session or create temporary one
        if session:
            session_ctx = None
            fetch_session = session
        else:
            session_ctx = aiohttp.ClientSession()
            fetch_session = await session_ctx.__aenter__()

        try:
            # Try common patterns
            for pattern in self.blog_patterns:
                test_url = f"{parsed.scheme}://{parsed.netloc}{pattern}"
                if await self._url_exists(fetch_session, test_url):
                    blog_url = test_url
                    logger.info(f"Found blog at: {blog_url}")
                    break

            if not blog_url:
                logger.info("No blog section found")
                return {'found': False, 'articles': []}

            # Scrape blog listing page
            articles = await self._scrape_blog_listing(fetch_session, blog_url)

            # Scrape individual articles (up to max)
            detailed_articles = []
            for article in articles[:self.max_articles]:
                try:
                    details = await self._scrape_article(fetch_session, article['url'])
                    if details:
                        article.update(details)
                        detailed_articles.append(article)
                    await asyncio.sleep(0.5)  # Be respectful
                except Exception as e:
                    logger.warning(f"Failed to scrape article {article['url']}: {e}")
        finally:
            # Close session if we created it
            if session_ctx:
                await session_ctx.__aexit__(None, None, None)

        logger.info(f"Scraped {len(detailed_articles)} blog articles")

        return {
            'found': True,
            'blog_url': blog_url,
            'articles_count': len(detailed_articles),
            'articles': detailed_articles,
            'technologies_mentioned': self._extract_technologies(detailed_articles),
            'topics': self._extract_topics(detailed_articles)
        }

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

    async def _scrape_blog_listing(self, session: aiohttp.ClientSession, blog_url: str) -> List[Dict]:
        """Scrape blog listing page to get article links."""
        try:
            async with session.get(
                blog_url,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': 'Mozilla/5.0'}
            ) as response:
                html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            articles = []

            # Look for article links (common patterns)
            # Try finding articles in various structures
            article_containers = (
                soup.find_all('article') or
                soup.find_all('div', class_=re.compile(r'post|article|blog', re.I)) or
                soup.find_all('h2') or
                soup.find_all('h3')
            )

            for container in article_containers[:30]:  # Limit to first 30 found
                link = container.find('a', href=True)
                if link:
                    url = urljoin(blog_url, link['href'])
                    title = link.get_text(strip=True) or 'Untitled'

                    # Try to find date
                    date_elem = container.find('time') or container.find(class_=re.compile(r'date|time', re.I))
                    date_str = date_elem.get_text(strip=True) if date_elem else None

                    articles.append({
                        'url': url,
                        'title': title,
                        'date': date_str
                    })

            return articles

        except Exception as e:
            logger.error(f"Failed to scrape blog listing: {e}")
            return []

    async def _scrape_article(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        """Scrape individual article content."""
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': 'Mozilla/5.0'}
            ) as response:
                html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')

            # Remove noise
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()

            # Try to find main content
            content_area = (
                soup.find('article') or
                soup.find('main') or
                soup.find('div', class_=re.compile(r'content|post|article', re.I)) or
                soup.find('body')
            )

            if content_area:
                text = content_area.get_text(separator='\n', strip=True)
                # Limit content length
                text = text[:3000] if len(text) > 3000 else text

                return {
                    'content': text,
                    'word_count': len(text.split())
                }

        except Exception as e:
            logger.debug(f"Failed to scrape article content: {e}")
            return None

    def _extract_technologies(self, articles: List[Dict]) -> List[str]:
        """Extract technology mentions from articles."""
        tech_keywords = [
            'BigQuery', 'Snowflake', 'Databricks', 'Redshift', 'PostgreSQL', 'MySQL', 'MongoDB',
            'Kafka', 'Pub/Sub', 'Airflow', 'dbt', 'Looker', 'Tableau', 'Power BI',
            'Python', 'SQL', 'Spark', 'Kubernetes', 'Docker', 'AWS', 'GCP', 'Azure',
            'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'React', 'Node.js',
            'API', 'REST', 'GraphQL', 'microservices', 'machine learning', 'AI',
            'data warehouse', 'data lake', 'ETL', 'analytics', 'real-time'
        ]

        found_techs = set()
        all_text = ' '.join([a.get('content', '') + ' ' + a.get('title', '') for a in articles])

        for tech in tech_keywords:
            if re.search(r'\b' + re.escape(tech) + r'\b', all_text, re.IGNORECASE):
                found_techs.add(tech)

        return sorted(list(found_techs))

    def _extract_topics(self, articles: List[Dict]) -> List[str]:
        """Extract common topics from article titles."""
        topics = set()
        topic_keywords = [
            'data', 'analytics', 'cloud', 'security', 'performance', 'optimization',
            'integration', 'automation', 'scalability', 'migration', 'platform',
            'customer', 'product', 'feature', 'release', 'update'
        ]

        all_titles = ' '.join([a.get('title', '') for a in articles]).lower()

        for topic in topic_keywords:
            if topic in all_titles:
                topics.add(topic)

        return sorted(list(topics))


class LinkedInScraper:
    """Scraper for LinkedIn company pages."""

    async def scrape_linkedin(
        self,
        company_name: str,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Dict:
        """
        Scrape LinkedIn company page.

        Note: LinkedIn has strict anti-scraping. This does basic public data only.

        Args:
            company_name: Company name
            base_url: Company website URL
            session: Optional shared aiohttp session for connection pooling

        Returns:
            Dict with LinkedIn data
        """
        logger.info(f"Attempting to find LinkedIn for {company_name}")

        # Try to find LinkedIn URL from website
        linkedin_url = await self._find_linkedin_url(base_url, session)

        if not linkedin_url:
            logger.info("LinkedIn URL not found")
            return {'found': False, 'posts': []}

        logger.info(f"Found LinkedIn: {linkedin_url}")

        # Note: LinkedIn requires authentication for post access
        # For now, we just return the URL found
        return {
            'found': True,
            'linkedin_url': linkedin_url,
            'note': 'LinkedIn scraping requires authentication. Use LinkedIn API for full access.',
            'posts': []  # Would need LinkedIn API key
        }

    async def _find_linkedin_url(
        self,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Optional[str]:
        """Try to find LinkedIn URL from website footer/about page."""
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
                    base_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={'User-Agent': 'Mozilla/5.0'}
                ) as response:
                    html = await response.text()
            finally:
                # Close session if we created it
                if session_ctx:
                    await session_ctx.__aexit__(None, None, None)

            soup = BeautifulSoup(html, 'html.parser')

            # Look for LinkedIn links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'linkedin.com/company' in href or 'linkedin.com/in' in href:
                    return href

        except Exception as e:
            logger.debug(f"Failed to find LinkedIn URL: {e}")

        return None


class YouTubeScraper:
    """Scraper for YouTube channels using YouTube Data API."""

    def __init__(self):
        """Initialize YouTube scraper."""
        self.api_key = os.getenv('YOUTUBE_API_KEY')

    async def scrape_youtube(
        self,
        company_name: str,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Dict:
        """
        Find and scrape YouTube channel.

        Args:
            company_name: Company name
            base_url: Company website URL
            session: Optional shared aiohttp session for connection pooling

        Returns:
            Dict with YouTube data
        """
        logger.info(f"Searching for YouTube channel for {company_name}")

        # Try to find YouTube URL from website
        youtube_url = await self._find_youtube_url(base_url, session)

        if not youtube_url:
            logger.info("YouTube channel not found")
            return {'found': False, 'videos': []}

        logger.info(f"Found YouTube: {youtube_url}")

        # Extract channel ID or username from URL
        channel_info = self._parse_youtube_url(youtube_url)

        # If we have API key, fetch video data
        if self.api_key and channel_info:
            videos = await self._fetch_youtube_videos(channel_info)
            return {
                'found': True,
                'youtube_url': youtube_url,
                'videos_count': len(videos),
                'videos': videos,
                'topics': self._extract_video_topics(videos)
            }
        else:
            return {
                'found': True,
                'youtube_url': youtube_url,
                'note': 'Set YOUTUBE_API_KEY to fetch video details',
                'videos': []
            }

    async def _find_youtube_url(
        self,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None
    ) -> Optional[str]:
        """Try to find YouTube URL from website."""
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
                    base_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={'User-Agent': 'Mozilla/5.0'}
                ) as response:
                    html = await response.text()
            finally:
                # Close session if we created it
                if session_ctx:
                    await session_ctx.__aexit__(None, None, None)

            soup = BeautifulSoup(html, 'html.parser')

            # Look for YouTube links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'youtube.com' in href or 'youtu.be' in href:
                    return href

        except Exception as e:
            logger.debug(f"Failed to find YouTube URL: {e}")

        return None

    def _parse_youtube_url(self, url: str) -> Optional[Dict]:
        """Parse YouTube URL to extract channel info."""
        # Examples: youtube.com/c/ChannelName, youtube.com/channel/UCxxxxx, youtube.com/@username
        patterns = [
            r'youtube\.com/c/([^/?]+)',
            r'youtube\.com/channel/([^/?]+)',
            r'youtube\.com/@([^/?]+)',
            r'youtube\.com/user/([^/?]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return {'type': 'channel', 'id': match.group(1)}

        return None

    async def _fetch_youtube_videos(self, channel_info: Dict) -> List[Dict]:
        """Fetch recent videos using YouTube Data API."""
        if not self.api_key:
            return []

        try:
            from googleapiclient.discovery import build

            youtube = build('youtube', 'v3', developerKey=self.api_key)

            # Search for channel's recent uploads
            search_response = youtube.search().list(
                part='snippet',
                channelId=channel_info.get('id'),
                order='date',
                maxResults=15,
                type='video'
            ).execute()

            videos = []
            for item in search_response.get('items', []):
                snippet = item['snippet']
                videos.append({
                    'title': snippet['title'],
                    'description': snippet['description'][:500],  # Limit length
                    'published_at': snippet['publishedAt'],
                    'video_id': item['id']['videoId']
                })

            return videos

        except Exception as e:
            logger.warning(f"Failed to fetch YouTube videos: {e}")
            return []

    def _extract_video_topics(self, videos: List[Dict]) -> List[str]:
        """Extract topics from video titles and descriptions."""
        topics = set()
        keywords = [
            'tutorial', 'demo', 'feature', 'product', 'announcement',
            'webinar', 'conference', 'interview', 'case study',
            'data', 'analytics', 'cloud', 'API', 'integration'
        ]

        all_text = ' '.join([
            v.get('title', '') + ' ' + v.get('description', '')
            for v in videos
        ]).lower()

        for keyword in keywords:
            if keyword in all_text:
                topics.add(keyword)

        return sorted(list(topics))
