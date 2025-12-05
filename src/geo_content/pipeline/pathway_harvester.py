"""
Pathway-based web harvesting pipeline for GEO Content Platform.

Uses Pathway's real-time data processing framework for web scraping
with streaming data capabilities.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Try to import Pathway - it may not be available in all environments
try:
    import pathway as pw
    from pathway.io.python import ConnectorSubject

    PATHWAY_AVAILABLE = True
except ImportError:
    PATHWAY_AVAILABLE = False
    pw = None
    ConnectorSubject = object  # Fallback for type hints


@dataclass
class HarvestedContent:
    """Represents harvested content from a URL."""

    url: str
    title: str
    content: str
    word_count: int
    metadata: dict
    harvested_at: datetime
    content_hash: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "word_count": self.word_count,
            "metadata": self.metadata,
            "harvested_at": self.harvested_at.isoformat(),
            "content_hash": self.content_hash,
        }


class WebScraperSubject(ConnectorSubject if PATHWAY_AVAILABLE else object):
    """
    Pathway connector subject for web scraping.

    Implements the generator pattern required by Pathway for streaming data.
    """

    def __init__(self, urls: list[str], timeout: int = 30):
        """
        Initialize the web scraper subject.

        Args:
            urls: List of URLs to scrape
            timeout: Request timeout in seconds
        """
        if PATHWAY_AVAILABLE:
            super().__init__()
        self._urls = urls
        self._timeout = timeout
        self._scraped_urls: set[str] = set()

    def run(self) -> None:
        """
        Execute the scraping pipeline.

        This method is called by Pathway to start the data stream.
        """
        for url in self._urls:
            if url in self._scraped_urls:
                continue

            try:
                content = self._scrape_url_sync(url)
                if content:
                    self._scraped_urls.add(url)
                    if PATHWAY_AVAILABLE:
                        self.next(
                            url=content.url,
                            title=content.title,
                            text=content.content,
                            word_count=content.word_count,
                            metadata=content.metadata,
                        )
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")

    def _scrape_url_sync(self, url: str) -> HarvestedContent | None:
        """
        Synchronously scrape a single URL.

        Args:
            url: URL to scrape

        Returns:
            HarvestedContent or None if scraping fails
        """
        try:
            with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
                response = client.get(url, headers=_get_headers())
                response.raise_for_status()

                return _parse_html_content(url, response.text)

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None


class PathwayWebHarvester:
    """
    Web harvester using Pathway for real-time data processing.

    Falls back to direct HTTP requests if Pathway is not available.
    """

    def __init__(self, timeout: int = 30, max_concurrent: int = 5):
        """
        Initialize the harvester.

        Args:
            timeout: Request timeout in seconds
            max_concurrent: Maximum concurrent requests
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "PathwayWebHarvester":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=self.max_concurrent),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def harvest_url(self, url: str) -> HarvestedContent | None:
        """
        Harvest content from a single URL.

        Args:
            url: URL to harvest

        Returns:
            HarvestedContent or None if harvesting fails
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)

        try:
            response = await self._client.get(url, headers=_get_headers())
            response.raise_for_status()

            return _parse_html_content(url, response.text)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error harvesting {url}: {e}")
            return None

    async def harvest_urls(self, urls: list[str]) -> list[HarvestedContent]:
        """
        Harvest content from multiple URLs concurrently.

        Args:
            urls: List of URLs to harvest

        Returns:
            List of HarvestedContent objects
        """
        # Use semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def harvest_with_semaphore(url: str) -> HarvestedContent | None:
            async with semaphore:
                return await self.harvest_url(url)

        results = await asyncio.gather(
            *[harvest_with_semaphore(url) for url in urls],
            return_exceptions=True,
        )

        # Filter out None results and exceptions
        harvested = []
        for result in results:
            if isinstance(result, HarvestedContent):
                harvested.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Harvesting exception: {result}")

        return harvested

    async def harvest_stream(self, urls: list[str]) -> AsyncIterator[HarvestedContent]:
        """
        Stream harvested content as it becomes available.

        Args:
            urls: List of URLs to harvest

        Yields:
            HarvestedContent objects as they are harvested
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def harvest_with_semaphore(url: str) -> HarvestedContent | None:
            async with semaphore:
                return await self.harvest_url(url)

        # Create tasks for all URLs
        tasks = [asyncio.create_task(harvest_with_semaphore(url)) for url in urls]

        # Yield results as they complete
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                if result:
                    yield result
            except Exception as e:
                logger.error(f"Stream harvesting error: {e}")


def _get_headers() -> dict[str, str]:
    """Get HTTP headers for requests."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }


def _parse_html_content(url: str, html: str) -> HarvestedContent:
    """
    Parse HTML content and extract text.

    Args:
        url: Source URL
        html: Raw HTML content

    Returns:
        HarvestedContent with extracted text
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        element.decompose()

    # Extract title
    title = ""
    if soup.title:
        title = soup.title.get_text(strip=True)
    elif soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)

    # Extract main content
    # Try to find main content area
    main_content = None
    for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
        main_content = soup.select_one(selector)
        if main_content:
            break

    if not main_content:
        main_content = soup.body if soup.body else soup

    # Extract text
    text = main_content.get_text(separator="\n", strip=True) if main_content else ""

    # Clean up text
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    cleaned_text = "\n".join(lines)

    # Count words
    word_count = len(cleaned_text.split())

    # Extract metadata
    metadata = _extract_metadata(soup, url)

    # Generate content hash
    content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()

    return HarvestedContent(
        url=url,
        title=title,
        content=cleaned_text,
        word_count=word_count,
        metadata=metadata,
        harvested_at=datetime.utcnow(),
        content_hash=content_hash,
    )


def _extract_metadata(soup: BeautifulSoup, url: str) -> dict:
    """
    Extract metadata from HTML.

    Args:
        soup: BeautifulSoup object
        url: Source URL

    Returns:
        Dictionary of metadata
    """
    metadata = {"url": url}

    # Extract meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        metadata["description"] = meta_desc["content"]

    # Extract Open Graph data
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        metadata["og_title"] = og_title["content"]

    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        metadata["og_description"] = og_desc["content"]

    # Extract author
    author = soup.find("meta", attrs={"name": "author"})
    if author and author.get("content"):
        metadata["author"] = author["content"]

    # Extract publish date
    for date_attr in ["article:published_time", "datePublished", "publishDate"]:
        date_meta = soup.find("meta", property=date_attr) or soup.find(
            "meta", attrs={"name": date_attr}
        )
        if date_meta and date_meta.get("content"):
            metadata["published_date"] = date_meta["content"]
            break

    return metadata


async def harvest_urls(urls: list[str], timeout: int = 30) -> list[HarvestedContent]:
    """
    Convenience function to harvest multiple URLs.

    Args:
        urls: List of URLs to harvest
        timeout: Request timeout in seconds

    Returns:
        List of HarvestedContent objects
    """
    async with PathwayWebHarvester(timeout=timeout) as harvester:
        return await harvester.harvest_urls(urls)


def create_pathway_pipeline(urls: list[str]) -> "pw.Table | None":
    """
    Create a Pathway pipeline for web scraping.

    Args:
        urls: List of URLs to scrape

    Returns:
        Pathway table with scraped data, or None if Pathway not available
    """
    if not PATHWAY_AVAILABLE:
        logger.warning("Pathway not available, returning None")
        return None

    class WebContentSchema(pw.Schema):
        url: str = pw.column_definition(primary_key=True)
        title: str
        text: str
        word_count: int
        metadata: dict

    subject = WebScraperSubject(urls=urls)
    table = pw.io.python.read(subject, schema=WebContentSchema)

    return table
