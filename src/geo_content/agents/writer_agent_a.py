"""
Writer Agent A - GPT-4.1-mini based content writer.

Uses OpenAI Agents SDK for GEO-optimized content generation.
"""

import logging
import time
from typing import Any

from agents import Agent, Runner

from geo_content.agents.base import create_agent, get_model_config
from geo_content.config import settings
from geo_content.models import ContentDraft, ResearchBrief
from geo_content.prompts.geo_writer import GEO_WRITER_SYSTEM_PROMPT, get_writer_prompt
from geo_content.prompts.language_specific import get_localized_system_prompt
from geo_content.tools.word_count import count_words

logger = logging.getLogger(__name__)


class WriterAgentA:
    """
    Writer Agent A using GPT-4.1-mini.

    Generates GEO-optimized content based on research briefs.
    """

    def __init__(self):
        """Initialize Writer Agent A."""
        self.model_config = get_model_config("writer_a")
        self.agent: Agent | None = None

    def _create_agent(self, language_code: str) -> Agent:
        """
        Create the writer agent with language-specific instructions.

        Args:
            language_code: Target language code

        Returns:
            Configured Agent instance
        """
        localized_prompt = get_localized_system_prompt(
            GEO_WRITER_SYSTEM_PROMPT,
            language_code,
        )

        return create_agent(
            name="WriterAgentA",
            instructions=localized_prompt,
            model=self.model_config["model"],
        )

    async def generate_content(
        self,
        client_name: str,
        target_question: str,
        research_brief: ResearchBrief | dict,
        target_word_count: int = 500,
    ) -> ContentDraft:
        """
        Generate GEO-optimized content.

        Args:
            client_name: Name of the client/entity
            target_question: Question to answer
            research_brief: Compiled research material
            target_word_count: Target word count for the content

        Returns:
            ContentDraft with generated content
        """
        start_time = time.time()

        # Convert ResearchBrief to dict if needed
        if isinstance(research_brief, ResearchBrief):
            brief_dict = research_brief.model_dump()
        else:
            brief_dict = research_brief

        language_code = brief_dict.get("language_code", "en")

        # Create agent with localized prompt
        agent = self._create_agent(language_code)

        # Generate the user prompt
        user_prompt = get_writer_prompt(
            client_name=client_name,
            target_question=target_question,
            research_brief=brief_dict,
            writer_id="A",
            target_word_count=target_word_count,
        )

        logger.info(
            f"[Writer A] Starting generation: model={self.model_config['model']}, "
            f"language={language_code}, target_words={target_word_count}"
        )

        try:
            # Run the agent
            result = await Runner.run(agent, user_prompt)
            content = result.final_output

            # Calculate metrics
            generation_time_ms = int((time.time() - start_time) * 1000)
            word_count = count_words(content, language_code)

            # Count GEO elements (simple heuristics)
            statistics_count = self._count_statistics(content)
            citations_count = self._count_citations(content)
            quotations_count = self._count_quotations(content)

            logger.info(
                f"[Writer A] Generation completed: {word_count} words, "
                f"{generation_time_ms}ms, stats={statistics_count}, "
                f"citations={citations_count}, quotes={quotations_count}"
            )

            return ContentDraft(
                draft_id="A",
                content=content,
                word_count=word_count,
                model_used=self.model_config["model"],
                generation_time_ms=generation_time_ms,
                statistics_count=statistics_count,
                citations_count=citations_count,
                quotations_count=quotations_count,
            )

        except Exception as e:
            logger.error(f"[Writer A] Generation error: {e}")
            generation_time_ms = int((time.time() - start_time) * 1000)

            # Return error draft
            return ContentDraft(
                draft_id="A",
                content=f"Error generating content: {e}",
                word_count=0,
                model_used=self.model_config["model"],
                generation_time_ms=generation_time_ms,
                statistics_count=0,
                citations_count=0,
                quotations_count=0,
            )

    def _count_statistics(self, content: str) -> int:
        """Count statistics in content using simple heuristics."""
        import re

        # Look for patterns like percentages, numbers with units, years, etc.
        patterns = [
            r"\d+(?:\.\d+)?%",  # Percentages
            r"\d{1,3}(?:,\d{3})+",  # Large numbers with commas
            r"\d+(?:\.\d+)?\s*(?:million|billion|trillion)",  # Numbers with units
            r"(?:in|since|by)\s+\d{4}",  # Years
            r"ranked?\s+#?\d+",  # Rankings
        ]

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            count += len(matches)

        return min(count, 10)  # Cap at 10

    def _count_citations(self, content: str) -> int:
        """Count citations in content using simple heuristics."""
        import re

        # Look for citation patterns
        patterns = [
            r"according to [\w\s]+",  # "According to..."
            r"(?:research|study|report) (?:by|from) [\w\s]+",  # Research citations
            r"(?:says?|said) [\w\s]+",  # Quote attributions
            r"\[[\w\s]+\]",  # Bracketed citations
        ]

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            count += len(matches)

        return min(count, 10)  # Cap at 10

    def _count_quotations(self, content: str) -> int:
        """Count quotations in content."""
        import re

        # Count quoted text patterns
        patterns = [
            r'"[^"]{20,}"',  # Double quotes with substantial content
            r"'[^']{20,}'",  # Single quotes with substantial content
            r"「[^」]{10,}」",  # Chinese quotes
            r"«[^»]{20,}»",  # French/Arabic quotes
        ]

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content)
            count += len(matches)

        return min(count, 5)  # Cap at 5


# Create default instance
writer_agent_a = WriterAgentA()


async def generate_content_a(
    client_name: str,
    target_question: str,
    research_brief: ResearchBrief | dict,
    target_word_count: int = 500,
) -> ContentDraft:
    """
    Convenience function to generate content using Writer Agent A.

    Args:
        client_name: Name of the client/entity
        target_question: Question to answer
        research_brief: Compiled research material
        target_word_count: Target word count for the content

    Returns:
        ContentDraft with generated content
    """
    return await writer_agent_a.generate_content(
        client_name=client_name,
        target_question=target_question,
        research_brief=research_brief,
        target_word_count=target_word_count,
    )
