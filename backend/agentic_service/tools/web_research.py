"""
Web research tools for scraping and analyzing websites.
"""
import asyncio
import logging
from typing import Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_website(
    url: str,
    session: Optional[aiohttp.ClientSession] = None,
    timeout: int = 30
) -> str:
    """
    Scrape website content and extract main text.

    Args:
        url: Website URL to scrape
        session: Optional shared aiohttp session for connection pooling
        timeout: Request timeout in seconds

    Returns:
        Extracted text content

    Raises:
        ValueError: If URL is invalid or request fails
    """
    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    logger.info(f"Scraping {url}")

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
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers={"User-Agent": "Mozilla/5.0 (compatible; DemoBot/1.0)"}
            ) as response:
                response.raise_for_status()
                html = await response.text()
        finally:
            # Close session if we created it
            if session_ctx:
                await session_ctx.__aexit__(None, None, None)

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            script.decompose()

        # Extract text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)

        logger.info(f"Scraped {len(clean_text)} characters from {url}")
        return clean_text

    except asyncio.TimeoutError:
        raise ValueError(f"Timeout while scraping {url}")
    except aiohttp.ClientError as e:
        raise ValueError(f"Failed to scrape {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error scraping {url}: {e}", exc_info=True)
        raise
