"""
Tavily web search tool for GEO Content Platform.

Provides web search capabilities for research gathering.
"""

import logging
from dataclasses import dataclass

import httpx
from agents import function_tool
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from geo_content.config import settings

logger = logging.getLogger(__name__)


def _create_retry_decorator():
    """Create a retry decorator with settings from config."""
    return retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.retry_min_wait_seconds,
            max=settings.retry_max_wait_seconds,
        ),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )

TAVILY_API_URL = "https://api.tavily.com/search"


@dataclass
class SearchResult:
    """Represents a single search result."""

    title: str
    url: str
    content: str
    score: float
    published_date: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "score": self.score,
            "published_date": self.published_date,
        }


@dataclass
class SearchResponse:
    """Represents the complete search response."""

    query: str
    results: list[SearchResult]
    answer: str | None = None
    follow_up_questions: list[str] | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "answer": self.answer,
            "follow_up_questions": self.follow_up_questions,
            "result_count": len(self.results),
        }


async def tavily_search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 10,
    include_answer: bool = True,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
) -> SearchResponse | None:
    """
    Perform a web search using Tavily API with retry logic.

    Args:
        query: Search query string
        search_depth: "basic" or "advanced" (more comprehensive)
        max_results: Maximum number of results (1-20)
        include_answer: Whether to include AI-generated answer
        include_domains: Domains to include in search
        exclude_domains: Domains to exclude from search

    Returns:
        SearchResponse or None if search fails
    """
    api_key = settings.tavily_api_key
    if not api_key:
        logger.error("Tavily API key not configured")
        return None

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": search_depth,
        "max_results": min(max_results, 20),
        "include_answer": include_answer,
        "include_raw_content": False,
        "include_images": False,
    }

    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains

    @_create_retry_decorator()
    async def _execute_search():
        async with httpx.AsyncClient(timeout=settings.search_timeout_seconds) as client:
            response = await client.post(TAVILY_API_URL, json=payload)
            response.raise_for_status()
            return response.json()

    try:
        data = await _execute_search()

        results = [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", ""),
                score=r.get("score", 0.0),
                published_date=r.get("published_date"),
            )
            for r in data.get("results", [])
        ]

        return SearchResponse(
            query=query,
            results=results,
            answer=data.get("answer"),
            follow_up_questions=data.get("follow_up_questions"),
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Tavily API HTTP error: {e.response.status_code}")
        return None
    except httpx.TimeoutException:
        logger.error(f"Tavily API timeout after {settings.search_timeout_seconds}s")
        return None
    except httpx.RequestError as e:
        logger.error(f"Tavily API request error after retries: {e}")
        return None
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return None


def tavily_search_sync(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 10,
    include_answer: bool = True,
) -> SearchResponse | None:
    """
    Synchronous version of Tavily search with retry logic.

    Args:
        query: Search query string
        search_depth: "basic" or "advanced"
        max_results: Maximum number of results
        include_answer: Whether to include AI-generated answer

    Returns:
        SearchResponse or None if search fails
    """
    api_key = settings.tavily_api_key
    if not api_key:
        logger.error("Tavily API key not configured")
        return None

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": search_depth,
        "max_results": min(max_results, 20),
        "include_answer": include_answer,
        "include_raw_content": False,
        "include_images": False,
    }

    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.retry_min_wait_seconds,
            max=settings.retry_max_wait_seconds,
        ),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _execute_search():
        with httpx.Client(timeout=settings.search_timeout_seconds) as client:
            response = client.post(TAVILY_API_URL, json=payload)
            response.raise_for_status()
            return response.json()

    try:
        data = _execute_search()

        results = [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", ""),
                score=r.get("score", 0.0),
                published_date=r.get("published_date"),
            )
            for r in data.get("results", [])
        ]

        return SearchResponse(
            query=query,
            results=results,
            answer=data.get("answer"),
            follow_up_questions=data.get("follow_up_questions"),
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Tavily API HTTP error: {e.response.status_code}")
        return None
    except httpx.TimeoutException:
        logger.error(f"Tavily API timeout after {settings.search_timeout_seconds}s")
        return None
    except httpx.RequestError as e:
        logger.error(f"Tavily API request error after retries: {e}")
        return None
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return None


@function_tool
def tavily_search_tool(
    query: str,
    max_results: int = 10,
    search_depth: str = "advanced",
) -> dict:
    """
    Search the web for information using Tavily.

    This tool performs comprehensive web searches to gather research
    material for content generation.

    Args:
        query: The search query to execute
        max_results: Maximum number of results to return (1-20)
        search_depth: Search depth - "basic" for faster, "advanced" for more comprehensive

    Returns:
        Dictionary with query, results, answer, and follow_up_questions
    """
    result = tavily_search_sync(
        query=query,
        search_depth=search_depth,
        max_results=max_results,
        include_answer=True,
    )

    if result:
        return result.to_dict()

    return {
        "error": "Search failed",
        "query": query,
        "results": [],
        "result_count": 0,
    }


@function_tool
def tavily_research_tool(
    topic: str,
    client_name: str,
    num_searches: int = 3,
) -> dict:
    """
    Conduct comprehensive research on a topic for GEO content.

    Performs multiple searches to gather statistics, expert quotes,
    and credible sources about the topic.

    Args:
        topic: The main topic to research
        client_name: Name of the client/entity to include in searches
        num_searches: Number of different search angles to try

    Returns:
        Dictionary with combined research results
    """
    search_queries = [
        f"{client_name} {topic}",
        f"{topic} statistics data facts",
        f"{topic} expert quotes opinions",
    ][:num_searches]

    all_results = []
    all_answers = []

    for query in search_queries:
        result = tavily_search_sync(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
        )

        if result:
            all_results.extend(result.results)
            if result.answer:
                all_answers.append({"query": query, "answer": result.answer})

    # Deduplicate results by URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r.url not in seen_urls:
            seen_urls.add(r.url)
            unique_results.append(r)

    return {
        "topic": topic,
        "client_name": client_name,
        "searches_performed": len(search_queries),
        "results": [r.to_dict() for r in unique_results],
        "answers": all_answers,
        "total_results": len(unique_results),
        "source_urls": list(seen_urls),
    }
