"""
GEO Performance Commentary models.

Defines structures for detailed GEO analysis explanations provided to users.
"""

from typing import Literal

from pydantic import BaseModel, Field


class GEOStrategyAnalysis(BaseModel):
    """Analysis of a single GEO strategy application."""

    strategy_name: str = Field(
        ...,
        description="Name of the GEO strategy (e.g., 'Statistics Addition')",
    )
    applied_count: int = Field(
        ...,
        ge=0,
        description="Number of times this strategy was applied",
    )
    expected_visibility_boost: str = Field(
        ...,
        description="Expected visibility improvement (e.g., '+25-40%')",
    )
    specific_examples: list[str] = Field(
        default_factory=list,
        description="Specific examples from the content",
    )
    effectiveness_rating: Literal["Excellent", "Good", "Adequate", "Needs Improvement"] = Field(
        ...,
        description="Rating of strategy effectiveness in this content",
    )
    research_reference: str = Field(
        default="",
        description="Research citation supporting this strategy",
    )


class EEATAnalysis(BaseModel):
    """Analysis of E-E-A-T signals in content."""

    experience_signals: list[str] = Field(
        default_factory=list,
        description="Experience signals found (case studies, real examples)",
    )
    expertise_signals: list[str] = Field(
        default_factory=list,
        description="Expertise signals found (technical accuracy, domain knowledge)",
    )
    authority_signals: list[str] = Field(
        default_factory=list,
        description="Authority signals found (citations, expert quotes)",
    )
    trust_signals: list[str] = Field(
        default_factory=list,
        description="Trust signals found (verified stats, source attribution)",
    )
    overall_eeat_score: int = Field(
        ...,
        ge=0,
        le=10,
        description="Overall E-E-A-T score (0-10)",
    )
    eeat_summary: str = Field(
        default="",
        description="Summary of E-E-A-T performance",
    )


class StructureAnalysis(BaseModel):
    """Analysis of content structure effectiveness."""

    opening_effectiveness: str = Field(
        ...,
        description="Assessment of opening statement effectiveness",
    )
    opening_word_count: int = Field(
        default=0,
        description="Word count of opening statement",
    )
    answers_query_directly: bool = Field(
        default=True,
        description="Whether opening directly answers the query",
    )
    structure_quality: str = Field(
        ...,
        description="Assessment of overall structure quality",
    )
    heading_analysis: str = Field(
        default="",
        description="Analysis of heading hierarchy",
    )
    entity_mention_analysis: str = Field(
        ...,
        description="Analysis of entity mention frequency and placement",
    )
    entity_mention_count: int = Field(
        default=0,
        description="Number of times entity is mentioned",
    )
    information_flow: str = Field(
        default="",
        description="Assessment of information flow and readability",
    )


class VerificationStatus(BaseModel):
    """Perplexity AI verification results for statistics and quotes."""

    statistics_verified: int = Field(
        default=0,
        ge=0,
        description="Number of statistics verified via Perplexity",
    )
    statistics_discarded: int = Field(
        default=0,
        ge=0,
        description="Number of statistics discarded (unverified)",
    )
    quotes_verified: int = Field(
        default=0,
        ge=0,
        description="Number of quotes verified via Perplexity",
    )
    quotes_discarded: int = Field(
        default=0,
        ge=0,
        description="Number of quotes discarded (unverified)",
    )
    retry_needed: bool = Field(
        default=False,
        description="Whether retry was needed due to insufficient verified content",
    )
    retry_attempts: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts performed",
    )
    verification_confidence: Literal["High", "Medium", "Low"] = Field(
        default="High",
        description="Confidence level in verification results",
    )
    verification_summary: str = Field(
        default="",
        description="Summary of verification process and results",
    )


class ComparisonAnalysis(BaseModel):
    """Analysis comparing the selected draft to the alternative."""

    selected_draft: Literal["A", "B"] = Field(
        ...,
        description="Which draft was selected",
    )
    selected_score: float = Field(
        ...,
        description="Score of selected draft",
    )
    alternative_score: float = Field(
        ...,
        description="Score of alternative draft",
    )
    score_difference: float = Field(
        ...,
        description="Score difference between drafts",
    )
    selection_rationale: str = Field(
        ...,
        description="Detailed explanation of why this draft was selected",
    )
    comparative_advantages: list[str] = Field(
        default_factory=list,
        description="Specific advantages of selected draft over alternative",
    )
    model_comparison: str = Field(
        default="",
        description="Brief comparison of model performance (GPT vs Claude)",
    )


class GEOPerformanceCommentary(BaseModel):
    """Complete GEO performance commentary for user presentation."""

    # Summary
    overall_assessment: str = Field(
        ...,
        description="High-level assessment of GEO performance",
    )
    predicted_visibility_improvement: str = Field(
        ...,
        description="Predicted visibility improvement percentage",
    )
    confidence_level: Literal["High", "Medium", "Low"] = Field(
        ...,
        description="Confidence level in the prediction",
    )

    # Detailed analysis
    strategy_analysis: list[GEOStrategyAnalysis] = Field(
        default_factory=list,
        description="Analysis of each GEO strategy applied",
    )
    eeat_analysis: EEATAnalysis = Field(
        ...,
        description="E-E-A-T signal analysis",
    )
    structure_analysis: StructureAnalysis = Field(
        ...,
        description="Content structure analysis",
    )

    # Key points
    key_strengths: list[str] = Field(
        default_factory=list,
        description="Top 3-5 strengths driving GEO performance",
    )

    # Comparison
    comparison: ComparisonAnalysis = Field(
        ...,
        description="Comparison with alternative draft",
    )

    # Optional improvements
    enhancement_suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for further improvement (2-3 max)",
    )

    # Perplexity verification status
    verification_status: VerificationStatus | None = Field(
        default=None,
        description="Perplexity AI verification results for statistics and quotes",
    )

    # Metadata
    commentary_language: str = Field(
        default="en",
        description="Language of this commentary",
    )

    def to_display_dict(self) -> dict:
        """Convert to a display-friendly dictionary format."""
        return {
            "summary": {
                "overall_assessment": self.overall_assessment,
                "predicted_visibility_improvement": self.predicted_visibility_improvement,
                "confidence_level": self.confidence_level,
            },
            "strategies": [
                {
                    "name": s.strategy_name,
                    "count": s.applied_count,
                    "boost": s.expected_visibility_boost,
                    "rating": s.effectiveness_rating,
                    "examples": s.specific_examples[:3],  # Limit to 3 examples
                }
                for s in self.strategy_analysis
            ],
            "eeat": {
                "score": self.eeat_analysis.overall_eeat_score,
                "experience": self.eeat_analysis.experience_signals[:3],
                "expertise": self.eeat_analysis.expertise_signals[:3],
                "authority": self.eeat_analysis.authority_signals[:3],
                "trust": self.eeat_analysis.trust_signals[:3],
            },
            "key_strengths": self.key_strengths,
            "selection": {
                "selected": self.comparison.selected_draft,
                "score": self.comparison.selected_score,
                "rationale": self.comparison.selection_rationale,
                "advantages": self.comparison.comparative_advantages,
            },
            "suggestions": self.enhancement_suggestions,
            "verification": (
                {
                    "statistics": {
                        "verified": self.verification_status.statistics_verified,
                        "discarded": self.verification_status.statistics_discarded,
                    },
                    "quotes": {
                        "verified": self.verification_status.quotes_verified,
                        "discarded": self.verification_status.quotes_discarded,
                    },
                    "retry_needed": self.verification_status.retry_needed,
                    "retry_attempts": self.verification_status.retry_attempts,
                    "confidence": self.verification_status.verification_confidence,
                    "summary": self.verification_status.verification_summary,
                }
                if self.verification_status
                else None
            ),
        }
