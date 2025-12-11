"""
Pydantic models for Content Rewrite feature.

Defines request/response schemas for the content rewrite workflow.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# Style and Tone types
RewriteStyle = Literal["professional", "casual", "academic", "journalistic", "marketing"]
RewriteTone = Literal["neutral", "enthusiastic", "authoritative", "conversational"]


class ContentRewriteRequest(BaseModel):
    """API request for content rewrite."""

    # Source content (one of these required)
    source_url: str | None = Field(
        default=None,
        description="URL to fetch and rewrite content from",
    )
    source_file_path: str | None = Field(
        default=None,
        description="Path to uploaded file to rewrite",
    )
    source_text: str | None = Field(
        default=None,
        description="Direct text input to rewrite (for future use)",
    )

    # Rewrite options
    style: RewriteStyle = Field(
        default="professional",
        description="Writing style for the rewritten content",
    )
    tone: RewriteTone = Field(
        default="neutral",
        description="Tone for the rewritten content",
    )
    preserve_structure: bool = Field(
        default=True,
        description="Whether to preserve the original content structure (headings, sections)",
    )
    target_word_count: int | None = Field(
        default=None,
        ge=100,
        le=5000,
        description="Target word count (defaults to original length +/- 10%)",
    )

    # Research enhancement (like Generate feature)
    reference_urls: list[str] = Field(
        default_factory=list,
        description="Additional URLs to harvest for research enhancement",
    )
    reference_documents: list[str] = Field(
        default_factory=list,
        description="Paths to additional documents for research",
    )

    # Context
    client_name: str | None = Field(
        default=None,
        description="Client/entity name for optimization (optional)",
    )
    language_override: str | None = Field(
        default=None,
        description="Override automatic language detection (e.g., 'zh-TW')",
    )

    @model_validator(mode="after")
    def validate_source_provided(self) -> "ContentRewriteRequest":
        """Ensure at least one source is provided."""
        if not any([self.source_url, self.source_file_path, self.source_text]):
            raise ValueError(
                "At least one source must be provided: source_url, source_file_path, or source_text"
            )
        return self


class RewriteComparison(BaseModel):
    """Before/after comparison data for rewritten content."""

    original_content: str = Field(
        ...,
        description="The original content before rewriting",
    )
    original_word_count: int = Field(
        ...,
        description="Word count of original content",
    )
    original_language: str = Field(
        ...,
        description="Detected language of original content",
    )
    rewritten_content: str = Field(
        ...,
        description="The rewritten/optimized content",
    )
    rewritten_word_count: int = Field(
        ...,
        description="Word count of rewritten content",
    )
    changes_summary: list[str] = Field(
        default_factory=list,
        description="List of key changes made during rewriting",
    )


class GEOOptimizationsApplied(BaseModel):
    """Track which GEO optimizations were applied during rewrite."""

    statistics_added: int = Field(
        default=0,
        description="Number of statistics added to the content",
    )
    statistics_original: int = Field(
        default=0,
        description="Number of statistics in original content",
    )
    citations_added: int = Field(
        default=0,
        description="Number of citations added to the content",
    )
    citations_original: int = Field(
        default=0,
        description="Number of citations in original content",
    )
    quotations_added: int = Field(
        default=0,
        description="Number of quotations added to the content",
    )
    quotations_original: int = Field(
        default=0,
        description="Number of quotations in original content",
    )
    fluency_improvements: list[str] = Field(
        default_factory=list,
        description="List of fluency improvements made",
    )
    structure_changes: list[str] = Field(
        default_factory=list,
        description="List of structural changes made",
    )
    eeat_enhancements: list[str] = Field(
        default_factory=list,
        description="List of E-E-A-T enhancements made",
    )


class ContentRewriteResponse(BaseModel):
    """API response for content rewrite."""

    # Request tracking
    job_id: str = Field(..., description="Unique job identifier")
    trace_id: str = Field(..., description="OpenAI Trace identifier")
    trace_url: str = Field(..., description="URL to view trace in OpenAI dashboard")

    # Language
    detected_language: str = Field(..., description="Human-readable language name")
    language_code: str = Field(..., description="Language code used")
    writing_direction: Literal["ltr", "rtl"] = Field(..., description="Text direction")

    # Comparison
    comparison: RewriteComparison = Field(
        ...,
        description="Before/after comparison of content",
    )

    # Optimizations
    optimizations_applied: GEOOptimizationsApplied = Field(
        ...,
        description="Details of GEO optimizations applied",
    )

    # Style/tone used
    style_applied: RewriteStyle = Field(
        ...,
        description="Writing style applied to content",
    )
    tone_applied: RewriteTone = Field(
        ...,
        description="Tone applied to content",
    )

    # Evaluation (reuse existing evaluation logic)
    evaluation_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Final evaluation score (0-100)",
    )
    evaluation_iterations: int = Field(
        ...,
        description="Number of evaluation iterations",
    )

    # GEO Commentary (same format as Generate)
    geo_commentary: dict = Field(
        ...,
        description="GEO performance analysis",
    )

    # Enhanced GEO Insights
    geo_insights: dict | None = Field(
        default=None,
        description="Enhanced GEO insights with actionable recommendations",
    )

    # Metadata
    generation_time_ms: int = Field(
        ...,
        description="Total processing time in milliseconds",
    )
    models_used: dict = Field(
        ...,
        description="Models used for each agent",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response generation timestamp",
    )


class RewriteStyleInfo(BaseModel):
    """Information about a rewrite style option."""

    id: RewriteStyle = Field(..., description="Style identifier")
    name: str = Field(..., description="Human-readable style name")
    description: str = Field(..., description="Description of the style")


class RewriteToneInfo(BaseModel):
    """Information about a rewrite tone option."""

    id: RewriteTone = Field(..., description="Tone identifier")
    name: str = Field(..., description="Human-readable tone name")
    description: str = Field(..., description="Description of the tone")


class RewriteStylesResponse(BaseModel):
    """Response listing available rewrite styles and tones."""

    styles: list[RewriteStyleInfo] = Field(
        ...,
        description="Available writing styles",
    )
    tones: list[RewriteToneInfo] = Field(
        ...,
        description="Available tones",
    )


class UrlContentPreview(BaseModel):
    """Preview of content fetched from a URL."""

    url: str = Field(..., description="The source URL")
    title: str = Field(..., description="Page title")
    content_preview: str = Field(
        ...,
        description="First ~500 characters of content",
    )
    full_content: str = Field(
        ...,
        description="Full extracted content",
    )
    word_count: int = Field(..., description="Total word count")
    language: str = Field(..., description="Detected language")
    fetch_time_ms: int = Field(..., description="Time to fetch in milliseconds")
