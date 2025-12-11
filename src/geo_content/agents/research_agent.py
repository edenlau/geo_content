"""
Research Agent for GEO Content Platform.

Responsible for gathering and synthesizing research material from web sources
and documents to support GEO-optimized content generation.
"""

import asyncio
import logging
from datetime import datetime

from agents import Agent, Runner, function_tool

from geo_content.agents.base import COMMON_INSTRUCTIONS, create_agent, get_model_config
from geo_content.config import settings
from geo_content.models import (
    CitationItem,
    QuotationItem,
    ResearchBrief,
    StatisticItem,
)
from geo_content.pipeline.pathway_harvester import PathwayWebHarvester, harvest_urls
from geo_content.tools.document_parser import parse_documents
from geo_content.tools.perplexity_search import perplexity_quote_search, perplexity_search_statistics
from geo_content.tools.tavily_search import tavily_search

logger = logging.getLogger(__name__)

RESEARCH_AGENT_INSTRUCTIONS = f"""
You are a Research Agent specialized in gathering comprehensive research material
for GEO (Generative Engine Optimization) content creation.

{COMMON_INSTRUCTIONS}

## YOUR MISSION

Gather high-quality research material that will help create content optimized for
generative search engines like ChatGPT, Perplexity AI, Google AI Overviews, and Claude.

## CRITICAL: SUBQUESTION DECOMPOSITION

Before conducting any searches, you MUST break down the target question into 3-5 subquestions.
This ensures comprehensive coverage and better quality research.

**Example:**
Target Question: "What are the main attractions at Ocean Park Hong Kong?"

Subquestions:
1. What are the thrill rides and roller coasters at Ocean Park Hong Kong?
2. What marine life exhibits and aquarium experiences does Ocean Park Hong Kong offer?
3. What are the family-friendly attractions at Ocean Park Hong Kong?
4. What unique entertainment shows and experiences are available at Ocean Park Hong Kong?
5. What recent additions or new attractions has Ocean Park Hong Kong opened?

Then search for EACH subquestion separately to gather comprehensive information.

## RESEARCH PRIORITIES

1. **Statistics and Data**
   - Find specific, verifiable numbers and statistics
   - Include years and sources for all statistics
   - Prioritize recent data (within 2-3 years)
   - Example: "According to [Source], [statistic] in [year]"

2. **Expert Quotations**
   - Find quotes from recognized experts in the field
   - Include speaker name, title, and organization
   - Prefer direct quotes over paraphrased content
   - Example: "[Quote]" said [Name], [Title] at [Organization]

3. **Credible Sources**
   - Identify authoritative sources to cite
   - Prioritize: Academic institutions, Government agencies, Industry reports,
     Recognized news outlets, Official company sources
   - Rate source credibility (High/Medium/Low)

4. **Key Facts**
   - Extract core facts relevant to the topic
   - Focus on information that directly answers the target question
   - Verify facts appear in multiple sources when possible

## OUTPUT FORMAT

Structure your research as a comprehensive brief with:
- List of key facts
- Statistics with sources
- Expert quotations
- Credible citation sources
- Summary of raw content gathered

## LANGUAGE HANDLING

- Detect the language of the target question
- Search for sources in that language when possible
- Include sources in multiple languages if relevant
- Note the language of each source
"""


@function_tool
async def web_search(query: str, max_results: int = 10) -> dict:
    """
    Search the web for information on a topic.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Search results with titles, URLs, content snippets, and AI answer
    """
    logger.info(f"[Research] Web search: query='{query[:100]}...', max_results={max_results}")
    result = await tavily_search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True,
    )

    if result:
        result_dict = result.to_dict()
        result_count = len(result_dict.get("results", []))
        logger.info(f"[Research] Web search completed: {result_count} results found")
        return result_dict

    logger.warning(f"[Research] Web search failed for query: '{query[:50]}...'")
    return {"error": "Search failed", "query": query, "results": []}


@function_tool
async def harvest_web_content(urls: list[str]) -> dict:
    """
    Harvest full content from a list of URLs.

    Args:
        urls: List of URLs to harvest content from

    Returns:
        Harvested content with text, word counts, and metadata
    """
    logger.info(f"[Research] URL harvesting: {len(urls)} URLs to process")
    try:
        contents = await harvest_urls(urls, timeout=30)
        total_words = sum(c.word_count for c in contents)
        logger.info(
            f"[Research] URL harvesting completed: {len(contents)}/{len(urls)} successful, "
            f"{total_words} total words"
        )
        return {
            "harvested": [c.to_dict() for c in contents],
            "total_urls": len(urls),
            "successful": len(contents),
            "total_words": total_words,
        }
    except Exception as e:
        logger.error(f"[Research] Web harvesting error: {e}")
        return {
            "error": str(e),
            "harvested": [],
            "total_urls": len(urls),
            "successful": 0,
        }


@function_tool
def parse_reference_documents(file_paths: list[str]) -> dict:
    """
    Parse reference documents (PDF, DOCX, TXT) for research.

    Args:
        file_paths: List of file paths to parse

    Returns:
        Parsed document content with metadata
    """
    logger.info(f"[Research] Document parsing: {len(file_paths)} files to process")
    results = parse_documents(file_paths)
    total_words = sum(doc.word_count for doc in results)
    failed_count = len(file_paths) - len(results)
    logger.info(
        f"[Research] Document parsing completed: {len(results)} parsed, "
        f"{failed_count} failed, {total_words} total words"
    )
    return {
        "documents": [doc.to_dict() for doc in results],
        "total_documents": len(results),
        "total_words": total_words,
        "failed_count": failed_count,
    }


class ResearchAgent:
    """
    High-level Research Agent class for orchestrating research workflows.
    """

    def __init__(self):
        """Initialize the Research Agent."""
        model_config = get_model_config("research")

        self.agent = create_agent(
            name="ResearchAgent",
            instructions=RESEARCH_AGENT_INSTRUCTIONS,
            tools=[web_search, harvest_web_content, parse_reference_documents],
            model=model_config["model"],
        )

    async def conduct_research(
        self,
        client_name: str,
        target_question: str,
        reference_urls: list[str] | None = None,
        reference_documents: list[str] | None = None,
        language_code: str = "en",
    ) -> ResearchBrief:
        """
        Conduct comprehensive research for content generation.

        Args:
            client_name: Name of the client/entity
            target_question: The question to research
            reference_urls: Optional URLs to harvest
            reference_documents: Optional document paths to parse
            language_code: Detected language code

        Returns:
            ResearchBrief with compiled research material
        """
        research_prompt = f"""
Conduct comprehensive research for the following:

**Client/Entity:** {client_name}
**Target Question:** {target_question}
**Language:** {language_code}

## STEP 1: SUBQUESTION DECOMPOSITION (CRITICAL)

First, break down the target question into 3-5 specific subquestions that will help
gather comprehensive information. Think about different angles, aspects, and perspectives
that would help create authoritative content.

For example, if the question is about a company's products, subquestions might cover:
- Main product features and benefits
- Pricing and availability
- Customer reviews and satisfaction
- Comparison with competitors
- Recent updates or innovations

## STEP 2: RESEARCH TASKS

For EACH subquestion, conduct targeted research:

1. **Web Search**: Search for information using each subquestion
   - Search for: "{client_name} {target_question}"
   - Then search for each generated subquestion individually
   - Also search for: "{target_question} statistics facts"
   - Find statistics, expert opinions, and recent news

2. **URL Harvesting**: {f"Harvest content from these URLs: {reference_urls}" if reference_urls else "No specific URLs provided"}

3. **Document Parsing**: {f"Parse these documents: {reference_documents}" if reference_documents else "No documents provided"}

## OUTPUT REQUIREMENTS

Compile your research into a structured brief with:
1. Key facts (10-15 bullet points covering multiple aspects)
2. Statistics with sources (at least 5-8)
3. Expert quotations (at least 3-5)
4. Credible sources for citation (at least 6-10)

Ensure all statistics and quotes include their sources.
The more comprehensive and well-researched your output, the higher the quality score.
"""

        logger.info(f"[Research] Starting research for client='{client_name}', language={language_code}")
        logger.info(f"[Research] Target question: '{target_question[:100]}...'")
        if reference_urls:
            logger.info(f"[Research] Reference URLs provided: {len(reference_urls)}")
        if reference_documents:
            logger.info(f"[Research] Reference documents provided: {len(reference_documents)}")

        try:
            # Run the agent for facts, statistics, and citations
            result = await Runner.run(self.agent, research_prompt)

            # Parse the result into a ResearchBrief
            brief = self._parse_research_result(
                result.final_output,
                client_name,
                target_question,
                language_code,
                reference_urls or [],
            )

            # Use Perplexity AI for verified quote search
            logger.info("[Research] Searching for verified quotes via Perplexity AI")
            try:
                perplexity_quotes = await perplexity_quote_search(
                    topic=target_question,
                    client_name=client_name,
                    max_quotes=3,
                )
                if perplexity_quotes:
                    # Prepend verified quotes (they have source URLs)
                    brief.quotations = perplexity_quotes + list(brief.quotations)
                    logger.info(
                        f"[Research] Added {len(perplexity_quotes)} verified quotes from Perplexity"
                    )
                else:
                    logger.info("[Research] Perplexity did not find quotes")
            except Exception as e:
                logger.warning(f"[Research] Perplexity quote search failed: {e}")

            # Use Perplexity AI for verified statistics search
            logger.info("[Research] Searching for verified statistics via Perplexity AI")
            try:
                perplexity_stats = await perplexity_search_statistics(
                    topic=target_question,
                    client_name=client_name,
                    max_stats=5,
                )
                if perplexity_stats:
                    # Prepend verified statistics (they have source URLs)
                    brief.statistics = perplexity_stats + list(brief.statistics)
                    logger.info(
                        f"[Research] Added {len(perplexity_stats)} verified statistics from Perplexity"
                    )
                else:
                    logger.info("[Research] Perplexity did not find statistics")
            except Exception as e:
                logger.warning(f"[Research] Perplexity statistics search failed: {e}")

            # CRITICAL: Filter to verified-only content to prevent fabrication
            # Only keep statistics and quotes that have been verified via Perplexity
            verified_stats = [s for s in brief.statistics if s.verified]
            verified_quotes = [q for q in brief.quotations if q.verified]

            unverified_stats_count = len(brief.statistics) - len(verified_stats)
            unverified_quotes_count = len(brief.quotations) - len(verified_quotes)

            if unverified_stats_count > 0 or unverified_quotes_count > 0:
                logger.info(
                    f"[Research] Filtering out unverified content: "
                    f"{unverified_stats_count} stats, {unverified_quotes_count} quotes discarded"
                )

            # Check if we have insufficient verified content and retry if needed
            min_stats = 2
            min_quotes = 1
            max_retries = 2
            retries_performed = 0

            for retry in range(max_retries):
                if len(verified_stats) >= min_stats and len(verified_quotes) >= min_quotes:
                    break
                retries_performed = retry + 1

                logger.info(
                    f"[Research] Insufficient verified content (stats={len(verified_stats)}, "
                    f"quotes={len(verified_quotes)}), retry {retry + 1}/{max_retries}"
                )

                # Retry with alternative search terms
                alternative_query = f"{client_name} {target_question} expert opinion statistics data"

                # Retry quotes if needed
                if len(verified_quotes) < min_quotes:
                    try:
                        additional_quotes = await perplexity_quote_search(
                            topic=alternative_query,
                            client_name=client_name,
                            max_quotes=3,
                        )
                        if additional_quotes:
                            verified_quotes.extend(additional_quotes)
                            logger.info(
                                f"[Research] Retry found {len(additional_quotes)} additional quotes"
                            )
                    except Exception as e:
                        logger.warning(f"[Research] Quote retry failed: {e}")

                # Retry stats if needed
                if len(verified_stats) < min_stats:
                    try:
                        additional_stats = await perplexity_search_statistics(
                            topic=alternative_query,
                            client_name=client_name,
                            max_stats=5,
                        )
                        if additional_stats:
                            verified_stats.extend(additional_stats)
                            logger.info(
                                f"[Research] Retry found {len(additional_stats)} additional statistics"
                            )
                    except Exception as e:
                        logger.warning(f"[Research] Statistics retry failed: {e}")

            # Apply filtered verified content to brief
            brief.statistics = verified_stats
            brief.quotations = verified_quotes

            # Track verification metrics for commentary
            brief.verification_stats = {
                "total_stats_found": len(verified_stats) + unverified_stats_count,
                "verified_stats": len(verified_stats),
                "discarded_stats": unverified_stats_count,
                "total_quotes_found": len(verified_quotes) + unverified_quotes_count,
                "verified_quotes": len(verified_quotes),
                "discarded_quotes": unverified_quotes_count,
                "retry_attempts": retries_performed,
                "verification_source": "perplexity",
            }

            logger.info(
                f"[Research] Research completed: {len(brief.key_facts)} facts, "
                f"{len(brief.statistics)} verified stats, {len(brief.quotations)} verified quotes, "
                f"{len(brief.citations)} citations, retries={retries_performed}"
            )
            return brief

        except Exception as e:
            logger.error(f"[Research] Research agent error: {e}")
            # Return a minimal research brief on error
            return ResearchBrief(
                client_name=client_name,
                target_question=target_question,
                language_code=language_code,
                key_facts=[f"Research for {client_name} regarding: {target_question}"],
                statistics=[],
                quotations=[],
                citations=[],
                source_urls=reference_urls or [],
                raw_content_summary=f"Error during research: {e}",
            )

    def _parse_research_result(
        self,
        raw_output: str,
        client_name: str,
        target_question: str,
        language_code: str,
        source_urls: list[str],
    ) -> ResearchBrief:
        """
        Parse raw agent output into a structured ResearchBrief.

        Args:
            raw_output: Raw text output from the agent
            client_name: Client name
            target_question: Target question
            language_code: Language code
            source_urls: Source URLs used

        Returns:
            Structured ResearchBrief
        """
        # Extract key facts (simple heuristic parsing)
        key_facts = []
        statistics = []
        quotations = []
        citations = []

        lines = raw_output.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            lower_line = line.lower()
            if "fact" in lower_line or "key point" in lower_line:
                current_section = "facts"
            elif "statistic" in lower_line or "data" in lower_line:
                current_section = "statistics"
            elif "quote" in lower_line or "quotation" in lower_line:
                current_section = "quotations"
            elif "source" in lower_line or "citation" in lower_line:
                current_section = "citations"
            elif line.startswith(("-", "•", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
                # Parse list items based on current section
                content = line.lstrip("-•*0123456789.) ")

                if current_section == "facts" and content:
                    key_facts.append(content)
                elif current_section == "statistics" and content:
                    statistics.append(
                        StatisticItem(
                            value=content[:50],
                            context=content,
                            source="Research Agent",
                        )
                    )
                elif current_section == "quotations" and content:
                    quotations.append(
                        QuotationItem(
                            quote=content,
                            speaker="Expert",
                            source="Research Agent",
                        )
                    )
                elif current_section == "citations" and content:
                    citations.append(
                        CitationItem(
                            name=content[:100],
                            description=content,
                        )
                    )

        # Ensure we have at least some content
        if not key_facts:
            key_facts = [f"Research conducted for {client_name} on: {target_question}"]

        return ResearchBrief(
            client_name=client_name,
            target_question=target_question,
            language_code=language_code,
            key_facts=key_facts[:15],  # Limit to 15 (increased for subquestions)
            statistics=statistics[:8],  # Limit to 8 (increased for subquestions)
            quotations=quotations[:5],  # Limit to 5 (increased for subquestions)
            citations=citations[:10],  # Limit to 10 (increased for subquestions)
            source_urls=source_urls,
            raw_content_summary=raw_output[:3000],  # First 3000 chars (increased)
            total_words_harvested=len(raw_output.split()),
            research_timestamp=datetime.utcnow(),
        )


# Create a default research agent instance
research_agent = ResearchAgent()


async def conduct_research(
    client_name: str,
    target_question: str,
    reference_urls: list[str] | None = None,
    reference_documents: list[str] | None = None,
    language_code: str = "en",
) -> ResearchBrief:
    """
    Convenience function to conduct research.

    Args:
        client_name: Name of the client/entity
        target_question: The question to research
        reference_urls: Optional URLs to harvest
        reference_documents: Optional document paths
        language_code: Detected language code

    Returns:
        ResearchBrief with compiled research
    """
    return await research_agent.conduct_research(
        client_name=client_name,
        target_question=target_question,
        reference_urls=reference_urls,
        reference_documents=reference_documents,
        language_code=language_code,
    )
