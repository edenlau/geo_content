"""
Evaluator Agent for GEO Content Platform.

Responsible for evaluating content drafts and generating GEO performance commentary.
"""

import json
import logging
from typing import Any

from agents import Agent, Runner

from geo_content.agents.base import create_agent, get_model_config
from geo_content.config import settings
from geo_content.models import (
    ContentDraft,
    DraftEvaluation,
    EvaluationResult,
    EvaluationScore,
    GEOPerformanceCommentary,
    RevisionFeedback,
)
from geo_content.prompts.commentary import GEO_COMMENTARY_SYSTEM_PROMPT, get_commentary_prompt
from geo_content.prompts.evaluator import EVALUATOR_SYSTEM_PROMPT, get_evaluator_prompt

logger = logging.getLogger(__name__)


class EvaluatorAgent:
    """
    Evaluator Agent for assessing GEO content quality.

    Compares drafts, scores them, and generates performance commentary.
    """

    def __init__(self):
        """Initialize the Evaluator Agent."""
        self.model_config = get_model_config("evaluator")

        self.evaluation_agent = create_agent(
            name="EvaluatorAgent",
            instructions=EVALUATOR_SYSTEM_PROMPT,
            model=self.model_config["model"],
        )

        self.commentary_agent = create_agent(
            name="CommentaryAgent",
            instructions=GEO_COMMENTARY_SYSTEM_PROMPT,
            model=self.model_config["model"],
        )

    async def evaluate_drafts(
        self,
        draft_a: ContentDraft,
        draft_b: ContentDraft,
        target_question: str,
        client_name: str,
        language_code: str,
    ) -> EvaluationResult:
        """
        Evaluate and compare two content drafts.

        Args:
            draft_a: First draft (from GPT-4.1-mini)
            draft_b: Second draft (from Claude 3.5 Haiku)
            target_question: The question being answered
            client_name: Client/entity name
            language_code: Expected language code

        Returns:
            EvaluationResult with scores and selection
        """
        # Generate evaluation prompt
        evaluation_prompt = get_evaluator_prompt(
            draft_a_content=draft_a.content,
            draft_b_content=draft_b.content,
            target_question=target_question,
            client_name=client_name,
            language_code=language_code,
        )

        logger.info(
            f"[Evaluator] Starting evaluation: model={self.model_config['model']}, "
            f"language={language_code}"
        )
        logger.info(
            f"[Evaluator] Draft A: {draft_a.word_count} words, "
            f"stats={draft_a.statistics_count}, citations={draft_a.citations_count}"
        )
        logger.info(
            f"[Evaluator] Draft B: {draft_b.word_count} words, "
            f"stats={draft_b.statistics_count}, citations={draft_b.citations_count}"
        )

        try:
            # Run evaluation
            result = await Runner.run(self.evaluation_agent, evaluation_prompt)

            # Parse JSON response
            evaluation_data = self._parse_evaluation_response(result.final_output)

            # Build EvaluationResult
            eval_result = self._build_evaluation_result(evaluation_data)

            logger.info(
                f"[Evaluator] Evaluation completed: "
                f"Draft A score={eval_result.draft_a.overall_score:.1f}, "
                f"Draft B score={eval_result.draft_b.overall_score:.1f}"
            )
            logger.info(
                f"[Evaluator] Selection: Draft {eval_result.selected_draft} "
                f"(passes_threshold={eval_result.passes_threshold}, "
                f"threshold={eval_result.threshold_value})"
            )

            return eval_result

        except Exception as e:
            logger.error(f"[Evaluator] Evaluation error: {e}")
            # Return default evaluation favoring draft with more GEO elements
            return self._default_evaluation(draft_a, draft_b)

    async def generate_commentary(
        self,
        selected_content: str,
        alternative_content: str,
        selected_draft: str,
        evaluation_result: EvaluationResult,
        language_code: str,
    ) -> GEOPerformanceCommentary:
        """
        Generate detailed GEO performance commentary.

        Args:
            selected_content: Content of the selected draft
            alternative_content: Content of the alternative draft
            selected_draft: "A" or "B"
            evaluation_result: Evaluation result data
            language_code: Language code for output

        Returns:
            GEOPerformanceCommentary with detailed analysis
        """
        # Get scores
        if selected_draft == "A":
            selected_score = evaluation_result.draft_a.overall_score
            alternative_score = evaluation_result.draft_b.overall_score
        else:
            selected_score = evaluation_result.draft_b.overall_score
            alternative_score = evaluation_result.draft_a.overall_score

        # Build evaluation details dict
        evaluation_details = {
            "draft_a": {
                "scores": evaluation_result.draft_a.scores.model_dump(),
                "overall_score": evaluation_result.draft_a.overall_score,
            },
            "draft_b": {
                "scores": evaluation_result.draft_b.scores.model_dump(),
                "overall_score": evaluation_result.draft_b.overall_score,
            },
        }

        # Generate commentary prompt
        commentary_prompt = get_commentary_prompt(
            selected_content=selected_content,
            alternative_content=alternative_content,
            selected_draft=selected_draft,
            selected_score=selected_score,
            alternative_score=alternative_score,
            evaluation_details=evaluation_details,
            language_code=language_code,
        )

        logger.info(
            f"[Evaluator] Starting commentary generation: "
            f"selected=Draft {selected_draft}, score={selected_score:.1f}, "
            f"language={language_code}"
        )

        try:
            # Run commentary generation
            result = await Runner.run(self.commentary_agent, commentary_prompt)

            # Parse and build commentary
            commentary_data = self._parse_commentary_response(result.final_output)
            commentary = self._build_commentary(commentary_data, language_code)

            logger.info(
                f"[Evaluator] Commentary completed: "
                f"visibility_improvement={commentary.predicted_visibility_improvement}, "
                f"confidence={commentary.confidence_level}, "
                f"strategies_analyzed={len(commentary.strategy_analysis)}"
            )

            return commentary

        except Exception as e:
            logger.error(f"[Evaluator] Commentary generation error: {e}")
            return self._default_commentary(
                selected_draft, selected_score, alternative_score, language_code
            )

    def _parse_evaluation_response(self, response: str) -> dict:
        """Parse evaluation response JSON."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse evaluation JSON: {e}")

        # Return default structure
        return self._default_evaluation_data()

    def _parse_commentary_response(self, response: str) -> dict:
        """Parse commentary response JSON."""
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse commentary JSON: {e}")

        return {}

    def _build_evaluation_result(self, data: dict) -> EvaluationResult:
        """Build EvaluationResult from parsed data."""
        # Build Draft A evaluation
        draft_a_data = data.get("draft_a", {})
        draft_a_scores = draft_a_data.get("scores", {})

        draft_a = DraftEvaluation(
            draft_id="A",
            scores=EvaluationScore(
                statistics_score=draft_a_scores.get("statistics_score", 50),
                citations_score=draft_a_scores.get("citations_score", 50),
                quotations_score=draft_a_scores.get("quotations_score", 50),
                fluency_score=draft_a_scores.get("fluency_score", 50),
                experience_score=draft_a_scores.get("experience_score", 50),
                expertise_score=draft_a_scores.get("expertise_score", 50),
                authority_score=draft_a_scores.get("authority_score", 50),
                trust_score=draft_a_scores.get("trust_score", 50),
                opening_effectiveness=draft_a_scores.get("opening_effectiveness", 50),
                structure_quality=draft_a_scores.get("structure_quality", 50),
                entity_mention_quality=draft_a_scores.get("entity_mention_quality", 50),
                language_accuracy=draft_a_scores.get("language_accuracy", 50),
            ),
            overall_score=draft_a_data.get("overall_score", 50),
            strengths=draft_a_data.get("strengths", []),
            weaknesses=draft_a_data.get("weaknesses", []),
            feedback=self._parse_feedback(draft_a_data.get("revision_feedback", [])),
            statistics_count=draft_a_data.get("statistics_count", 0),
            citations_count=draft_a_data.get("citations_count", 0),
            quotations_count=draft_a_data.get("quotations_count", 0),
            entity_mentions=draft_a_data.get("entity_mentions", 0),
        )

        # Build Draft B evaluation
        draft_b_data = data.get("draft_b", {})
        draft_b_scores = draft_b_data.get("scores", {})

        draft_b = DraftEvaluation(
            draft_id="B",
            scores=EvaluationScore(
                statistics_score=draft_b_scores.get("statistics_score", 50),
                citations_score=draft_b_scores.get("citations_score", 50),
                quotations_score=draft_b_scores.get("quotations_score", 50),
                fluency_score=draft_b_scores.get("fluency_score", 50),
                experience_score=draft_b_scores.get("experience_score", 50),
                expertise_score=draft_b_scores.get("expertise_score", 50),
                authority_score=draft_b_scores.get("authority_score", 50),
                trust_score=draft_b_scores.get("trust_score", 50),
                opening_effectiveness=draft_b_scores.get("opening_effectiveness", 50),
                structure_quality=draft_b_scores.get("structure_quality", 50),
                entity_mention_quality=draft_b_scores.get("entity_mention_quality", 50),
                language_accuracy=draft_b_scores.get("language_accuracy", 50),
            ),
            overall_score=draft_b_data.get("overall_score", 50),
            strengths=draft_b_data.get("strengths", []),
            weaknesses=draft_b_data.get("weaknesses", []),
            feedback=self._parse_feedback(draft_b_data.get("revision_feedback", [])),
            statistics_count=draft_b_data.get("statistics_count", 0),
            citations_count=draft_b_data.get("citations_count", 0),
            quotations_count=draft_b_data.get("quotations_count", 0),
            entity_mentions=draft_b_data.get("entity_mentions", 0),
        )

        # Determine selection
        selected = data.get("selected_draft", "A")
        passes = data.get("passes_threshold", True)
        revision_needed = data.get("revision_needed", [])

        return EvaluationResult(
            draft_a=draft_a,
            draft_b=draft_b,
            selected_draft=selected,
            selection_rationale=data.get("selection_rationale", "Selected based on overall score"),
            passes_threshold=passes,
            threshold_value=settings.quality_threshold,
            revision_needed=revision_needed,
        )

    def _parse_feedback(self, feedback_list: list) -> list[RevisionFeedback]:
        """Parse revision feedback list."""
        result = []
        for item in feedback_list:
            if isinstance(item, dict):
                result.append(
                    RevisionFeedback(
                        priority=item.get("priority", "medium"),
                        category=item.get("category", "general"),
                        issue=item.get("issue", ""),
                        suggestion=item.get("suggestion", ""),
                        location=item.get("location"),
                    )
                )
            elif isinstance(item, str):
                result.append(
                    RevisionFeedback(
                        priority="medium",
                        category="general",
                        issue=item,
                        suggestion=item,
                    )
                )
        return result

    def _build_commentary(self, data: dict, language_code: str) -> GEOPerformanceCommentary:
        """Build GEOPerformanceCommentary from parsed data."""
        from geo_content.models.geo_commentary import (
            ComparisonAnalysis,
            EEATAnalysis,
            GEOStrategyAnalysis,
            StructureAnalysis,
        )

        # Parse strategy analysis
        strategies = []
        for s in data.get("strategy_analysis", []):
            strategies.append(
                GEOStrategyAnalysis(
                    strategy_name=s.get("strategy_name", "Unknown"),
                    applied_count=s.get("applied_count", 0),
                    expected_visibility_boost=s.get("expected_visibility_boost", "Unknown"),
                    specific_examples=s.get("specific_examples", []),
                    effectiveness_rating=s.get("effectiveness_rating", "Adequate"),
                    research_reference=s.get("research_reference", ""),
                )
            )

        # Parse E-E-A-T analysis
        eeat_data = data.get("eeat_analysis", {})
        # Normalize score: LLM sometimes returns 0-100 scale instead of 0-10
        raw_eeat_score = eeat_data.get("overall_eeat_score", 5)
        if raw_eeat_score > 10:
            # Convert 0-100 scale to 0-10
            normalized_score = min(10, max(0, raw_eeat_score // 10))
            logger.warning(
                f"[Evaluator] Normalizing E-E-A-T score from {raw_eeat_score} to {normalized_score}"
            )
        else:
            normalized_score = max(0, min(10, raw_eeat_score))

        eeat = EEATAnalysis(
            experience_signals=eeat_data.get("experience_signals", []),
            expertise_signals=eeat_data.get("expertise_signals", []),
            authority_signals=eeat_data.get("authority_signals", []),
            trust_signals=eeat_data.get("trust_signals", []),
            overall_eeat_score=normalized_score,
            eeat_summary=eeat_data.get("eeat_summary", ""),
        )

        # Parse structure analysis
        struct_data = data.get("structure_analysis", {})
        structure = StructureAnalysis(
            opening_effectiveness=struct_data.get("opening_effectiveness", "Not analyzed"),
            opening_word_count=struct_data.get("opening_word_count", 0),
            answers_query_directly=struct_data.get("answers_query_directly", True),
            structure_quality=struct_data.get("structure_quality", "Not analyzed"),
            entity_mention_analysis=struct_data.get("entity_mention_analysis", "Not analyzed"),
            entity_mention_count=struct_data.get("entity_mention_count", 0),
        )

        # Parse comparison
        comp_data = data.get("comparison", {})
        comparison = ComparisonAnalysis(
            selected_draft=comp_data.get("selected_draft", "A"),
            selected_score=comp_data.get("selected_score", 70),
            alternative_score=comp_data.get("alternative_score", 60),
            score_difference=comp_data.get("score_difference", 10),
            selection_rationale=comp_data.get("selection_rationale", "Selected based on score"),
            comparative_advantages=comp_data.get("comparative_advantages", []),
        )

        return GEOPerformanceCommentary(
            overall_assessment=data.get("overall_assessment", "Content evaluated for GEO optimization"),
            predicted_visibility_improvement=data.get("predicted_visibility_improvement", "25-35%"),
            confidence_level=data.get("confidence_level", "Medium"),
            strategy_analysis=strategies,
            eeat_analysis=eeat,
            structure_analysis=structure,
            key_strengths=data.get("key_strengths", []),
            comparison=comparison,
            enhancement_suggestions=data.get("enhancement_suggestions", []),
            commentary_language=language_code,
        )

    def _default_evaluation_data(self) -> dict:
        """Return default evaluation data structure."""
        default_scores = {
            "statistics_score": 50,
            "citations_score": 50,
            "quotations_score": 50,
            "fluency_score": 70,
            "experience_score": 50,
            "expertise_score": 50,
            "authority_score": 50,
            "trust_score": 50,
            "opening_effectiveness": 60,
            "structure_quality": 60,
            "entity_mention_quality": 50,
            "language_accuracy": 70,
        }

        return {
            "draft_a": {
                "scores": default_scores.copy(),
                "overall_score": 55,
                "strengths": [],
                "weaknesses": [],
            },
            "draft_b": {
                "scores": default_scores.copy(),
                "overall_score": 55,
                "strengths": [],
                "weaknesses": [],
            },
            "selected_draft": "A",
            "passes_threshold": False,
            "revision_needed": ["A", "B"],
        }

    def _default_evaluation(
        self, draft_a: ContentDraft, draft_b: ContentDraft
    ) -> EvaluationResult:
        """Create default evaluation when parsing fails."""
        # Simple comparison based on GEO element counts
        score_a = 50 + (draft_a.statistics_count * 5) + (draft_a.citations_count * 3) + (draft_a.quotations_count * 4)
        score_b = 50 + (draft_b.statistics_count * 5) + (draft_b.citations_count * 3) + (draft_b.quotations_count * 4)

        score_a = min(score_a, 85)
        score_b = min(score_b, 85)

        selected = "A" if score_a >= score_b else "B"
        best_score = max(score_a, score_b)

        data = self._default_evaluation_data()
        data["draft_a"]["overall_score"] = score_a
        data["draft_b"]["overall_score"] = score_b
        data["selected_draft"] = selected
        data["passes_threshold"] = best_score >= settings.quality_threshold

        return self._build_evaluation_result(data)

    def _default_commentary(
        self,
        selected_draft: str,
        selected_score: float,
        alternative_score: float,
        language_code: str,
    ) -> GEOPerformanceCommentary:
        """Create default commentary when generation fails."""
        from geo_content.models.geo_commentary import (
            ComparisonAnalysis,
            EEATAnalysis,
            StructureAnalysis,
        )

        return GEOPerformanceCommentary(
            overall_assessment="Content has been evaluated for GEO optimization potential.",
            predicted_visibility_improvement="20-30%",
            confidence_level="Medium",
            strategy_analysis=[],
            eeat_analysis=EEATAnalysis(
                experience_signals=[],
                expertise_signals=[],
                authority_signals=[],
                trust_signals=[],
                overall_eeat_score=5,
            ),
            structure_analysis=StructureAnalysis(
                opening_effectiveness="Evaluated",
                structure_quality="Evaluated",
                entity_mention_analysis="Evaluated",
            ),
            key_strengths=["Content generated with GEO optimization strategies"],
            comparison=ComparisonAnalysis(
                selected_draft=selected_draft,
                selected_score=selected_score,
                alternative_score=alternative_score,
                score_difference=selected_score - alternative_score,
                selection_rationale="Selected based on evaluation score",
                comparative_advantages=[],
            ),
            enhancement_suggestions=[],
            commentary_language=language_code,
        )


# Create default instance
evaluator_agent = EvaluatorAgent()


async def evaluate_drafts(
    draft_a: ContentDraft,
    draft_b: ContentDraft,
    target_question: str,
    client_name: str,
    language_code: str,
) -> EvaluationResult:
    """Convenience function to evaluate drafts."""
    return await evaluator_agent.evaluate_drafts(
        draft_a=draft_a,
        draft_b=draft_b,
        target_question=target_question,
        client_name=client_name,
        language_code=language_code,
    )


async def generate_commentary(
    selected_content: str,
    alternative_content: str,
    selected_draft: str,
    evaluation_result: EvaluationResult,
    language_code: str,
) -> GEOPerformanceCommentary:
    """Convenience function to generate commentary."""
    return await evaluator_agent.generate_commentary(
        selected_content=selected_content,
        alternative_content=alternative_content,
        selected_draft=selected_draft,
        evaluation_result=evaluation_result,
        language_code=language_code,
    )
