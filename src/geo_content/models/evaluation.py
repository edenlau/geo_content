"""
Evaluation models for GEO Content Platform.

Defines scoring, feedback, and evaluation result structures.
"""

from typing import Literal

from pydantic import BaseModel, Field


class EvaluationScore(BaseModel):
    """Detailed scoring breakdown for a content draft."""

    # Core GEO metrics (0-100 each)
    statistics_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Score for statistics integration (research: +25-40% visibility)",
    )
    citations_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Score for citation quality (research: +24-30% visibility)",
    )
    quotations_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Score for expert quotations (research: +27-40% visibility)",
    )
    fluency_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Score for writing fluency (research: +24-30% visibility)",
    )

    # E-E-A-T metrics (0-100 each)
    experience_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Experience signals score",
    )
    expertise_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Expertise signals score",
    )
    authority_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Authority signals score",
    )
    trust_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Trust signals score",
    )

    # Structure metrics (0-100 each)
    opening_effectiveness: float = Field(
        ...,
        ge=0,
        le=100,
        description="How effectively opening answers the query",
    )
    structure_quality: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall structure and organization",
    )
    entity_mention_quality: float = Field(
        ...,
        ge=0,
        le=100,
        description="Entity mention frequency and naturalness",
    )

    # Language quality (0-100)
    language_accuracy: float = Field(
        ...,
        ge=0,
        le=100,
        description="Accuracy of language/dialect usage",
    )

    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score."""
        # Weights based on GEO research impact
        weights = {
            "statistics_score": 0.12,
            "citations_score": 0.10,
            "quotations_score": 0.12,
            "fluency_score": 0.10,
            "experience_score": 0.08,
            "expertise_score": 0.08,
            "authority_score": 0.08,
            "trust_score": 0.08,
            "opening_effectiveness": 0.10,
            "structure_quality": 0.06,
            "entity_mention_quality": 0.04,
            "language_accuracy": 0.04,
        }
        total = sum(
            getattr(self, field) * weight for field, weight in weights.items()
        )
        return round(total, 2)


class RevisionFeedback(BaseModel):
    """Feedback for improving a draft."""

    priority: Literal["high", "medium", "low"] = Field(
        ...,
        description="Priority level of the feedback",
    )
    category: str = Field(
        ...,
        description="Category of improvement (e.g., 'statistics', 'fluency', 'structure')",
    )
    issue: str = Field(
        ...,
        description="Description of the issue",
    )
    suggestion: str = Field(
        ...,
        description="Specific suggestion for improvement",
    )
    location: str | None = Field(
        default=None,
        description="Location in content where issue occurs",
    )


class DraftEvaluation(BaseModel):
    """Complete evaluation of a single draft."""

    draft_id: Literal["A", "B"] = Field(..., description="Draft identifier")
    scores: EvaluationScore = Field(..., description="Detailed scoring breakdown")
    overall_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall evaluation score",
    )

    # Qualitative assessment
    strengths: list[str] = Field(
        default_factory=list,
        description="Key strengths of this draft",
    )
    weaknesses: list[str] = Field(
        default_factory=list,
        description="Key weaknesses of this draft",
    )

    # Revision feedback
    feedback: list[RevisionFeedback] = Field(
        default_factory=list,
        description="Specific feedback for improvement",
    )

    # GEO metrics
    statistics_count: int = Field(default=0, description="Statistics found in draft")
    citations_count: int = Field(default=0, description="Citations found in draft")
    quotations_count: int = Field(default=0, description="Quotations found in draft")
    entity_mentions: int = Field(default=0, description="Entity name mentions")


class EvaluationResult(BaseModel):
    """Complete evaluation result comparing both drafts."""

    draft_a: DraftEvaluation = Field(..., description="Evaluation of Draft A")
    draft_b: DraftEvaluation = Field(..., description="Evaluation of Draft B")

    # Selection
    selected_draft: Literal["A", "B"] = Field(
        ...,
        description="Which draft was selected as better",
    )
    selection_rationale: str = Field(
        ...,
        description="Explanation of why this draft was selected",
    )

    # Threshold check
    passes_threshold: bool = Field(
        ...,
        description="Whether the best draft passes the quality threshold",
    )
    threshold_value: int = Field(
        default=70,
        description="The quality threshold value",
    )

    # Revision tracking
    revision_needed: list[Literal["A", "B"]] = Field(
        default_factory=list,
        description="Which drafts need revision",
    )
    iteration_number: int = Field(
        default=1,
        ge=1,
        description="Current evaluation iteration",
    )

    @property
    def best_score(self) -> float:
        """Return the score of the selected draft."""
        if self.selected_draft == "A":
            return self.draft_a.overall_score
        return self.draft_b.overall_score
