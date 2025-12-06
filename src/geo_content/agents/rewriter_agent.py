"""
Rewriter Agent - GPT-4.1 based content rewriter.

Specializes in rewriting existing content with GEO optimizations while
preserving the original message and language.
"""

import json
import logging
import re
import time

from agents import Agent, Runner

from geo_content.agents.base import create_agent, get_model_config
from geo_content.config import settings
from geo_content.models import ContentDraft, ResearchBrief
from geo_content.models.rewrite_schemas import GEOOptimizationsApplied
from geo_content.prompts.geo_rewriter import (
    GEO_REWRITER_SYSTEM_PROMPT,
    get_comparison_analysis_prompt,
    get_rewriter_prompt,
)
from geo_content.prompts.language_specific import get_localized_system_prompt
from geo_content.tools.word_count import count_words

logger = logging.getLogger(__name__)


class RewriterAgent:
    """
    Rewriter Agent using GPT-4.1.

    Rewrites existing content with GEO optimizations while preserving
    the original message, intent, and language.
    """

    def __init__(self):
        """Initialize Rewriter Agent."""
        # Use the evaluator model (GPT-4.1) for higher quality rewriting
        self.model_config = get_model_config("evaluator")
        self.agent: Agent | None = None

    def _create_agent(self, language_code: str) -> Agent:
        """
        Create the rewriter agent with language-specific instructions.

        Args:
            language_code: Target language code

        Returns:
            Configured Agent instance
        """
        localized_prompt = get_localized_system_prompt(
            GEO_REWRITER_SYSTEM_PROMPT,
            language_code,
        )

        return create_agent(
            name="RewriterAgent",
            instructions=localized_prompt,
            model=self.model_config["model"],
        )

    async def rewrite_content(
        self,
        original_content: str,
        research_brief: ResearchBrief | dict,
        style: str = "professional",
        tone: str = "neutral",
        client_name: str | None = None,
        target_word_count: int | None = None,
        preserve_structure: bool = True,
    ) -> ContentDraft:
        """
        Rewrite content with GEO optimizations.

        Args:
            original_content: The original content to rewrite
            research_brief: Research material for enhancement
            style: Writing style (professional, casual, academic, journalistic, marketing)
            tone: Tone (neutral, enthusiastic, authoritative, conversational)
            client_name: Client/entity name for optimization
            target_word_count: Target word count (defaults to original length)
            preserve_structure: Whether to preserve original structure

        Returns:
            ContentDraft with rewritten content
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
        user_prompt = get_rewriter_prompt(
            original_content=original_content,
            client_name=client_name,
            research_brief=brief_dict,
            style=style,
            tone=tone,
            target_word_count=target_word_count,
            preserve_structure=preserve_structure,
        )

        logger.info(
            f"[Rewriter] Starting rewrite: model={self.model_config['model']}, "
            f"language={language_code}, style={style}, tone={tone}"
        )

        try:
            # Run the agent
            result = await Runner.run(agent, user_prompt)
            content = result.final_output

            # Calculate metrics
            generation_time_ms = int((time.time() - start_time) * 1000)
            word_count = count_words(content, language_code)

            # Count GEO elements
            statistics_count = self._count_statistics(content)
            citations_count = self._count_citations(content)
            quotations_count = self._count_quotations(content)

            logger.info(
                f"[Rewriter] Rewrite completed: {word_count} words, "
                f"{generation_time_ms}ms, stats={statistics_count}, "
                f"citations={citations_count}, quotes={quotations_count}"
            )

            return ContentDraft(
                draft_id="A",  # Rewriter always produces draft "A"
                content=content,
                word_count=word_count,
                model_used=self.model_config["model"],
                generation_time_ms=generation_time_ms,
                statistics_count=statistics_count,
                citations_count=citations_count,
                quotations_count=quotations_count,
            )

        except Exception as e:
            logger.error(f"[Rewriter] Rewrite error: {e}")
            generation_time_ms = int((time.time() - start_time) * 1000)

            # Return error draft
            return ContentDraft(
                draft_id="A",
                content=f"Error rewriting content: {e}",
                word_count=0,
                model_used=self.model_config["model"],
                generation_time_ms=generation_time_ms,
                statistics_count=0,
                citations_count=0,
                quotations_count=0,
            )

    async def analyze_changes(
        self,
        original_content: str,
        rewritten_content: str,
        language_code: str = "en",
    ) -> GEOOptimizationsApplied:
        """
        Analyze the changes between original and rewritten content.

        Args:
            original_content: The original content
            rewritten_content: The rewritten content
            language_code: Language code for analysis

        Returns:
            GEOOptimizationsApplied with detailed change analysis
        """
        # Count GEO elements in original
        original_stats = self._count_statistics(original_content)
        original_citations = self._count_citations(original_content)
        original_quotes = self._count_quotations(original_content)

        # Count GEO elements in rewritten
        rewritten_stats = self._count_statistics(rewritten_content)
        rewritten_citations = self._count_citations(rewritten_content)
        rewritten_quotes = self._count_quotations(rewritten_content)

        # Use LLM for detailed analysis
        agent = self._create_agent(language_code)
        analysis_prompt = get_comparison_analysis_prompt(
            original_content=original_content,
            rewritten_content=rewritten_content,
        )

        try:
            result = await Runner.run(agent, analysis_prompt)
            analysis_text = result.final_output

            # Parse JSON from response
            analysis = self._parse_analysis_json(analysis_text)

            return GEOOptimizationsApplied(
                statistics_added=max(0, rewritten_stats - original_stats),
                statistics_original=original_stats,
                citations_added=max(0, rewritten_citations - original_citations),
                citations_original=original_citations,
                quotations_added=max(0, rewritten_quotes - original_quotes),
                quotations_original=original_quotes,
                fluency_improvements=analysis.get("fluency_improvements", []),
                structure_changes=analysis.get("structure_changes", []),
                eeat_enhancements=analysis.get("eeat_enhancements", []),
            )

        except Exception as e:
            logger.warning(f"[Rewriter] Analysis error, using simple counts: {e}")

            # Fallback to simple analysis
            return GEOOptimizationsApplied(
                statistics_added=max(0, rewritten_stats - original_stats),
                statistics_original=original_stats,
                citations_added=max(0, rewritten_citations - original_citations),
                citations_original=original_citations,
                quotations_added=max(0, rewritten_quotes - original_quotes),
                quotations_original=original_quotes,
                fluency_improvements=["Improved sentence flow and clarity"],
                structure_changes=[],
                eeat_enhancements=["Enhanced credibility with source attribution"],
            )

    def _parse_analysis_json(self, text: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Try to extract JSON from markdown code block
        json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to parse the whole text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in the text
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {}

    def _count_statistics(self, content: str) -> int:
        """Count statistics in content using simple heuristics."""
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

    def generate_changes_summary(
        self,
        original_content: str,
        rewritten_content: str,
        optimizations: GEOOptimizationsApplied,
    ) -> list[str]:
        """
        Generate a human-readable summary of changes made.

        Args:
            original_content: The original content
            rewritten_content: The rewritten content
            optimizations: The optimizations that were applied

        Returns:
            List of change descriptions
        """
        changes = []

        # Word count change
        original_words = len(original_content.split())
        rewritten_words = len(rewritten_content.split())
        word_diff = rewritten_words - original_words
        if abs(word_diff) > 10:
            if word_diff > 0:
                changes.append(f"Expanded content by {word_diff} words")
            else:
                changes.append(f"Condensed content by {abs(word_diff)} words")

        # Statistics changes
        if optimizations.statistics_added > 0:
            changes.append(
                f"Added {optimizations.statistics_added} new statistics "
                f"(original had {optimizations.statistics_original})"
            )

        # Citations changes
        if optimizations.citations_added > 0:
            changes.append(
                f"Added {optimizations.citations_added} new citations "
                f"(original had {optimizations.citations_original})"
            )

        # Quotations changes
        if optimizations.quotations_added > 0:
            changes.append(
                f"Added {optimizations.quotations_added} new quotations "
                f"(original had {optimizations.quotations_original})"
            )

        # Fluency improvements
        if optimizations.fluency_improvements:
            changes.append("Improved fluency and readability")

        # Structure changes
        if optimizations.structure_changes:
            changes.append("Optimized content structure for AI visibility")

        # E-E-A-T enhancements
        if optimizations.eeat_enhancements:
            changes.append("Enhanced E-E-A-T signals for credibility")

        return changes if changes else ["Applied GEO optimizations for improved visibility"]


# Create default instance
rewriter_agent = RewriterAgent()


async def rewrite_content(
    original_content: str,
    research_brief: ResearchBrief | dict,
    style: str = "professional",
    tone: str = "neutral",
    client_name: str | None = None,
    target_word_count: int | None = None,
    preserve_structure: bool = True,
) -> ContentDraft:
    """
    Convenience function to rewrite content using the Rewriter Agent.

    Args:
        original_content: The original content to rewrite
        research_brief: Research material for enhancement
        style: Writing style
        tone: Tone
        client_name: Client/entity name for optimization
        target_word_count: Target word count
        preserve_structure: Whether to preserve original structure

    Returns:
        ContentDraft with rewritten content
    """
    return await rewriter_agent.rewrite_content(
        original_content=original_content,
        research_brief=research_brief,
        style=style,
        tone=tone,
        client_name=client_name,
        target_word_count=target_word_count,
        preserve_structure=preserve_structure,
    )
