"""
Writer Agent B - Claude 3.5 Haiku based content writer.

Uses Anthropic SDK directly for GEO-optimized content generation.
This is Option B implementation - direct Anthropic API wrapper.
"""

import logging
import time

import anthropic

from geo_content.config import settings
from geo_content.models import ContentDraft, ResearchBrief
from geo_content.prompts.geo_writer import GEO_WRITER_SYSTEM_PROMPT, get_writer_prompt
from geo_content.prompts.language_specific import get_localized_system_prompt
from geo_content.tools.word_count import count_words

logger = logging.getLogger(__name__)


class WriterAgentB:
    """
    Writer Agent B using Claude 3.5 Haiku via Anthropic SDK.

    Generates GEO-optimized content based on research briefs.
    Implements parallel writing capability with Writer Agent A.
    """

    def __init__(self):
        """Initialize Writer Agent B with Anthropic client."""
        self.model = settings.anthropic_model_writer
        self._client: anthropic.AsyncAnthropic | None = None

    @property
    def client(self) -> anthropic.AsyncAnthropic:
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            self._client = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key,
            )
        return self._client

    async def generate_content(
        self,
        client_name: str,
        target_question: str,
        research_brief: ResearchBrief | dict,
        target_word_count: int = 500,
    ) -> ContentDraft:
        """
        Generate GEO-optimized content using Claude 3.5 Haiku.

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

        # Create localized system prompt
        system_prompt = get_localized_system_prompt(
            GEO_WRITER_SYSTEM_PROMPT,
            language_code,
        )

        # Generate user prompt
        user_prompt = get_writer_prompt(
            client_name=client_name,
            target_question=target_question,
            research_brief=brief_dict,
            writer_id="B",
            target_word_count=target_word_count,
        )

        logger.info(
            f"[Writer B] Starting generation: model={self.model}, "
            f"language={language_code}, target_words={target_word_count}"
        )

        try:
            # Call Anthropic API directly
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
            )

            # Extract content from response
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            # Calculate metrics
            generation_time_ms = int((time.time() - start_time) * 1000)
            word_count = count_words(content, language_code)

            # Count GEO elements
            statistics_count = self._count_statistics(content)
            citations_count = self._count_citations(content)
            quotations_count = self._count_quotations(content)

            logger.info(
                f"[Writer B] Generation completed: {word_count} words, "
                f"{generation_time_ms}ms, stats={statistics_count}, "
                f"citations={citations_count}, quotes={quotations_count}"
            )

            return ContentDraft(
                draft_id="B",
                content=content,
                word_count=word_count,
                model_used=self.model,
                generation_time_ms=generation_time_ms,
                statistics_count=statistics_count,
                citations_count=citations_count,
                quotations_count=quotations_count,
            )

        except anthropic.APIConnectionError as e:
            logger.error(f"[Writer B] Anthropic API connection error: {e}")
            return self._error_draft(start_time, f"API connection error: {e}")

        except anthropic.RateLimitError as e:
            logger.error(f"[Writer B] Anthropic rate limit error: {e}")
            return self._error_draft(start_time, f"Rate limit exceeded: {e}")

        except anthropic.APIStatusError as e:
            logger.error(f"[Writer B] Anthropic API status error: {e}")
            return self._error_draft(start_time, f"API error: {e}")

        except Exception as e:
            logger.error(f"[Writer B] Generation error: {e}")
            return self._error_draft(start_time, str(e))

    def _error_draft(self, start_time: float, error_message: str) -> ContentDraft:
        """Create an error draft."""
        return ContentDraft(
            draft_id="B",
            content=f"Error generating content: {error_message}",
            word_count=0,
            model_used=self.model,
            generation_time_ms=int((time.time() - start_time) * 1000),
            statistics_count=0,
            citations_count=0,
            quotations_count=0,
        )

    def _count_statistics(self, content: str) -> int:
        """Count statistics in content using simple heuristics."""
        import re

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

        return min(count, 10)

    def _count_citations(self, content: str) -> int:
        """Count citations in content using simple heuristics."""
        import re

        patterns = [
            r"according to [\w\s]+",
            r"(?:research|study|report) (?:by|from) [\w\s]+",
            r"(?:says?|said) [\w\s]+",
            r"\[[\w\s]+\]",
        ]

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            count += len(matches)

        return min(count, 10)

    def _count_quotations(self, content: str) -> int:
        """Count quotations in content."""
        import re

        patterns = [
            r'"[^"]{20,}"',
            r"'[^']{20,}'",
            r"「[^」]{10,}」",
            r"«[^»]{20,}»",
        ]

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content)
            count += len(matches)

        return min(count, 5)


# Create default instance
writer_agent_b = WriterAgentB()


async def generate_content_b(
    client_name: str,
    target_question: str,
    research_brief: ResearchBrief | dict,
    target_word_count: int = 500,
) -> ContentDraft:
    """
    Convenience function to generate content using Writer Agent B (Claude).

    Args:
        client_name: Name of the client/entity
        target_question: Question to answer
        research_brief: Compiled research material
        target_word_count: Target word count for the content

    Returns:
        ContentDraft with generated content
    """
    return await writer_agent_b.generate_content(
        client_name=client_name,
        target_question=target_question,
        research_brief=research_brief,
        target_word_count=target_word_count,
    )
