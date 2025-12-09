"""
Perplexity AI search tool for GEO Content Platform.

Provides grounded quote search with source citations using Perplexity's online model.
"""

import json
import logging
import re
from dataclasses import dataclass, field

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from geo_content.config import settings
from geo_content.models.schemas import QuotationItem

logger = logging.getLogger(__name__)

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


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


@dataclass
class PerplexityQuoteResult:
    """Represents a quote found via Perplexity search."""

    quote: str
    speaker: str
    title: str | None = None
    organization: str | None = None
    source_url: str | None = None
    context: str | None = None

    def to_quotation_item(self) -> QuotationItem:
        """Convert to QuotationItem model."""
        title_str = self.title or ""
        if self.organization:
            title_str = f"{title_str} at {self.organization}" if title_str else self.organization

        return QuotationItem(
            quote=self.quote,
            speaker=self.speaker,
            title=title_str if title_str else None,
            source=self.context or "Perplexity AI search",
            source_url=self.source_url,
            verified=True,
            verification_source="perplexity",
        )


@dataclass
class PerplexitySearchResponse:
    """Represents the complete Perplexity search response."""

    query: str
    content: str
    quotes: list[PerplexityQuoteResult] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    model: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "content": self.content,
            "quotes": [
                {
                    "quote": q.quote,
                    "speaker": q.speaker,
                    "title": q.title,
                    "organization": q.organization,
                    "source_url": q.source_url,
                }
                for q in self.quotes
            ],
            "citations": self.citations,
            "model": self.model,
            "quotes_count": len(self.quotes),
        }


def _parse_quotes_from_response(content: str, citations: list[str]) -> list[PerplexityQuoteResult]:
    """
    Parse expert quotes from Perplexity response content.

    Looks for patterns like:
    - "[quote]" - Speaker Name, Title at Organization
    - "quote" said Speaker Name, Title
    - According to Speaker Name: "quote"
    """
    quotes = []

    # Pattern 1: "quote" - Speaker Name, Title at Organization [citation]
    # Example: "This is a quote" - John Smith, CEO at Company [1]
    pattern1 = re.compile(
        r'"([^"]{20,300})"\s*[-–—]\s*([A-Z][a-zA-Z\.\s]+?)(?:,\s*([^,\[\n]+?))?(?:\s+at\s+([^\[\n]+?))?(?:\s*\[(\d+)\])?',
        re.MULTILINE,
    )

    # Pattern 2: "quote," said Speaker Name, Title
    # Example: "This is important," said Jane Doe, Director of Research
    pattern2 = re.compile(
        r'"([^"]{20,300}),?"\s*(?:said|says|stated|noted|explained|commented)\s+([A-Z][a-zA-Z\.\s]+?)(?:,\s*([^\.\n]+?))?(?:\.|$)',
        re.MULTILINE,
    )

    # Pattern 3: According to Speaker Name: "quote"
    # Example: According to Dr. Smith: "This is the finding"
    pattern3 = re.compile(
        r'(?:According to|Per)\s+([A-Z][a-zA-Z\.\s]+?)(?:,\s*([^:]+?))?\s*[:\-]\s*"([^"]{20,300})"',
        re.MULTILINE,
    )

    # Find all matches from pattern 1
    for match in pattern1.finditer(content):
        quote_text = match.group(1).strip()
        speaker = match.group(2).strip() if match.group(2) else ""
        title = match.group(3).strip() if match.group(3) else None
        org = match.group(4).strip() if match.group(4) else None
        citation_idx = int(match.group(5)) - 1 if match.group(5) else None

        if speaker and len(quote_text) >= 20:
            source_url = None
            if citation_idx is not None and 0 <= citation_idx < len(citations):
                source_url = citations[citation_idx]

            quotes.append(
                PerplexityQuoteResult(
                    quote=quote_text,
                    speaker=speaker,
                    title=title,
                    organization=org,
                    source_url=source_url,
                    context="Expert quote from web search",
                )
            )

    # Find all matches from pattern 2
    for match in pattern2.finditer(content):
        quote_text = match.group(1).strip()
        speaker = match.group(2).strip()
        title = match.group(3).strip() if match.group(3) else None

        if speaker and len(quote_text) >= 20:
            # Try to find a citation near this quote
            source_url = citations[0] if citations else None

            quotes.append(
                PerplexityQuoteResult(
                    quote=quote_text,
                    speaker=speaker,
                    title=title,
                    source_url=source_url,
                    context="Expert quote from web search",
                )
            )

    # Find all matches from pattern 3
    for match in pattern3.finditer(content):
        speaker = match.group(1).strip()
        title = match.group(2).strip() if match.group(2) else None
        quote_text = match.group(3).strip()

        if speaker and len(quote_text) >= 20:
            source_url = citations[0] if citations else None

            quotes.append(
                PerplexityQuoteResult(
                    quote=quote_text,
                    speaker=speaker,
                    title=title,
                    source_url=source_url,
                    context="Expert quote from web search",
                )
            )

    # Deduplicate by quote text
    seen_quotes = set()
    unique_quotes = []
    for q in quotes:
        quote_key = q.quote[:50].lower()  # Use first 50 chars as key
        if quote_key not in seen_quotes:
            seen_quotes.add(quote_key)
            unique_quotes.append(q)

    return unique_quotes[:5]  # Return max 5 quotes


async def perplexity_quote_search(
    topic: str,
    client_name: str | None = None,
    max_quotes: int = 3,
) -> list[QuotationItem]:
    """
    Search for expert quotes using Perplexity AI.

    Uses the online model which provides grounded, cited responses.

    Args:
        topic: The topic to search for quotes about
        client_name: Optional client/entity name to include in search
        max_quotes: Maximum number of quotes to return

    Returns:
        List of QuotationItem objects with verified=True
    """
    api_key = settings.perplexity_api_key
    if not api_key:
        logger.warning("Perplexity API key not configured - skipping quote search")
        return []

    # Build the search prompt
    client_context = f" related to {client_name}" if client_name else ""
    prompt = f"""Find 2-3 real expert quotations about {topic}{client_context}.

Requirements:
- Direct quotes only (in quotation marks)
- Include speaker's full name and their title/organization
- Only include quotes you can cite with a source
- Recent quotes preferred (last 2-3 years)
- Quotes should be from recognized experts, industry leaders, or officials

Format each quote as:
"[exact quote text]" - [Speaker Full Name], [Title] at [Organization]

Provide the source URL for each quote."""

    payload = {
        "model": settings.perplexity_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a research assistant that finds real, verifiable expert quotations. Only provide quotes that actually exist and can be cited. Never fabricate quotes.",
            },
            {"role": "user", "content": prompt},
        ],
        "return_citations": True,
        "return_related_questions": False,
    }

    @_create_retry_decorator()
    async def _execute_search():
        async with httpx.AsyncClient(timeout=settings.search_timeout_seconds) as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    try:
        data = await _execute_search()

        # Extract content and citations
        content = ""
        citations = []

        if data.get("choices"):
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")

        # Citations are returned as a list of URLs
        citations = data.get("citations", [])

        logger.info(f"Perplexity search completed. Content length: {len(content)}, Citations: {len(citations)}")

        # Parse quotes from the response
        quotes = _parse_quotes_from_response(content, citations)

        logger.info(f"Parsed {len(quotes)} quotes from Perplexity response")

        # Convert to QuotationItem and return
        return [q.to_quotation_item() for q in quotes[:max_quotes]]

    except httpx.HTTPStatusError as e:
        logger.error(f"Perplexity API HTTP error: {e.response.status_code} - {e.response.text}")
        return []
    except httpx.TimeoutException:
        logger.error(f"Perplexity API timeout after {settings.search_timeout_seconds}s")
        return []
    except httpx.RequestError as e:
        logger.error(f"Perplexity API request error after retries: {e}")
        return []
    except Exception as e:
        logger.error(f"Perplexity search error: {e}")
        return []


def perplexity_quote_search_sync(
    topic: str,
    client_name: str | None = None,
    max_quotes: int = 3,
) -> list[QuotationItem]:
    """
    Synchronous version of Perplexity quote search.

    Args:
        topic: The topic to search for quotes about
        client_name: Optional client/entity name to include in search
        max_quotes: Maximum number of quotes to return

    Returns:
        List of QuotationItem objects with verified=True
    """
    api_key = settings.perplexity_api_key
    if not api_key:
        logger.warning("Perplexity API key not configured - skipping quote search")
        return []

    # Build the search prompt
    client_context = f" related to {client_name}" if client_name else ""
    prompt = f"""Find 2-3 real expert quotations about {topic}{client_context}.

Requirements:
- Direct quotes only (in quotation marks)
- Include speaker's full name and their title/organization
- Only include quotes you can cite with a source
- Recent quotes preferred (last 2-3 years)
- Quotes should be from recognized experts, industry leaders, or officials

Format each quote as:
"[exact quote text]" - [Speaker Full Name], [Title] at [Organization]

Provide the source URL for each quote."""

    payload = {
        "model": settings.perplexity_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a research assistant that finds real, verifiable expert quotations. Only provide quotes that actually exist and can be cited. Never fabricate quotes.",
            },
            {"role": "user", "content": prompt},
        ],
        "return_citations": True,
        "return_related_questions": False,
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
            response = client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    try:
        data = _execute_search()

        # Extract content and citations
        content = ""
        citations = []

        if data.get("choices"):
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")

        citations = data.get("citations", [])

        logger.info(f"Perplexity search completed. Content length: {len(content)}, Citations: {len(citations)}")

        # Parse quotes from the response
        quotes = _parse_quotes_from_response(content, citations)

        logger.info(f"Parsed {len(quotes)} quotes from Perplexity response")

        return [q.to_quotation_item() for q in quotes[:max_quotes]]

    except httpx.HTTPStatusError as e:
        logger.error(f"Perplexity API HTTP error: {e.response.status_code} - {e.response.text}")
        return []
    except httpx.TimeoutException:
        logger.error(f"Perplexity API timeout after {settings.search_timeout_seconds}s")
        return []
    except httpx.RequestError as e:
        logger.error(f"Perplexity API request error after retries: {e}")
        return []
    except Exception as e:
        logger.error(f"Perplexity search error: {e}")
        return []


async def perplexity_search_statistics(
    topic: str,
    client_name: str | None = None,
) -> dict:
    """
    Search for statistics and data using Perplexity AI.

    Args:
        topic: The topic to search for statistics about
        client_name: Optional client/entity name to include in search

    Returns:
        Dictionary with statistics found and their sources
    """
    api_key = settings.perplexity_api_key
    if not api_key:
        logger.warning("Perplexity API key not configured - skipping statistics search")
        return {"statistics": [], "citations": []}

    client_context = f" related to {client_name}" if client_name else ""
    prompt = f"""Find 3-5 specific, verifiable statistics about {topic}{client_context}.

Requirements:
- Include exact numbers, percentages, or data points
- Cite the source for each statistic
- Use recent data (within last 2-3 years when possible)
- Statistics should be from credible sources (government, academic, industry reports)

Format each statistic as:
- [Statistic with number] (Source: [Source Name], [Year])"""

    payload = {
        "model": settings.perplexity_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a research assistant that finds real, verifiable statistics. Only provide data that actually exists and can be cited. Never fabricate statistics.",
            },
            {"role": "user", "content": prompt},
        ],
        "return_citations": True,
    }

    @_create_retry_decorator()
    async def _execute_search():
        async with httpx.AsyncClient(timeout=settings.search_timeout_seconds) as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    try:
        data = await _execute_search()

        content = ""
        citations = []

        if data.get("choices"):
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")

        citations = data.get("citations", [])

        return {
            "content": content,
            "citations": citations,
            "topic": topic,
        }

    except Exception as e:
        logger.error(f"Perplexity statistics search error: {e}")
        return {"statistics": [], "citations": [], "error": str(e)}
