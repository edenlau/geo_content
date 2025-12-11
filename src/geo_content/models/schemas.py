"""
Core Pydantic models for GEO Content Platform.

Defines request/response schemas and data structures for the content generation workflow.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class LanguageDetectionResult(BaseModel):
    """Result of language detection analysis."""

    detected_language: str = Field(
        ...,
        description="Human-readable language name (e.g., 'English', 'Arabic', 'Chinese')",
    )
    language_code: str = Field(
        ...,
        description="Language code (e.g., 'en', 'zh-TW', 'ar-Gulf')",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Detection confidence score (0-1)",
    )
    dialect: str | None = Field(
        default=None,
        description="Detected dialect or variant (e.g., 'Gulf', 'Traditional', 'Egyptian')",
    )
    writing_direction: Literal["ltr", "rtl"] = Field(
        default="ltr",
        description="Text writing direction",
    )


class StatisticItem(BaseModel):
    """A single statistic extracted from research."""

    value: str = Field(..., description="The statistic value (e.g., '7.6 million')")
    context: str = Field(..., description="Context or description of the statistic")
    source: str = Field(..., description="Source of the statistic")
    year: str | None = Field(default=None, description="Year of the statistic if available")
    source_url: str | None = Field(default=None, description="Direct URL to the statistic source")
    verified: bool = Field(default=False, description="Whether the statistic was verified from a source")
    verification_source: str | None = Field(
        default=None,
        description="How the statistic was verified: 'perplexity', 'tavily', 'document', or None",
    )


class QuotationItem(BaseModel):
    """An expert quotation extracted from research."""

    quote: str = Field(..., description="The quotation text")
    speaker: str = Field(..., description="Name of the person quoted")
    title: str | None = Field(default=None, description="Title or position of the speaker")
    source: str = Field(..., description="Source where the quote was found")
    source_url: str | None = Field(default=None, description="Direct URL to the quote source")
    verified: bool = Field(default=False, description="Whether the quote was verified from a source")
    verification_source: str | None = Field(
        default=None,
        description="How the quote was verified: 'perplexity', 'tavily', 'document', or None",
    )


class CitationItem(BaseModel):
    """A credible source citation."""

    name: str = Field(..., description="Name of the source/organization")
    url: str | None = Field(default=None, description="URL to the source")
    description: str = Field(..., description="Brief description of the source's relevance")
    credibility_score: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Estimated credibility score (0-1)",
    )


class ResearchBrief(BaseModel):
    """Compiled research brief from the Research Agent."""

    client_name: str = Field(..., description="Name of the client/entity")
    target_question: str = Field(..., description="The question being answered")
    language_code: str = Field(..., description="Detected language code")

    # Extracted content
    key_facts: list[str] = Field(
        default_factory=list,
        description="Key facts and information gathered",
    )
    statistics: list[StatisticItem] = Field(
        default_factory=list,
        description="Extracted statistics with sources",
    )
    quotations: list[QuotationItem] = Field(
        default_factory=list,
        description="Expert quotations collected",
    )
    citations: list[CitationItem] = Field(
        default_factory=list,
        description="Credible sources identified",
    )

    # Source tracking
    source_urls: list[str] = Field(
        default_factory=list,
        description="URLs that were harvested",
    )
    raw_content_summary: str = Field(
        default="",
        description="Summary of raw content gathered",
    )

    # Metadata
    total_words_harvested: int = Field(
        default=0,
        description="Total words harvested from sources",
    )
    research_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the research was conducted",
    )

    # Perplexity verification metrics
    verification_stats: dict = Field(
        default_factory=dict,
        description="Perplexity verification statistics including verified/discarded counts",
    )


class ContentDraft(BaseModel):
    """A generated content draft."""

    draft_id: Literal["A", "B"] = Field(..., description="Draft identifier")
    content: str = Field(..., description="The generated content")
    word_count: int = Field(..., description="Word count of the content")
    model_used: str = Field(..., description="Model that generated this draft")
    generation_time_ms: int = Field(..., description="Generation time in milliseconds")

    # GEO metrics (populated after generation)
    statistics_count: int = Field(default=0, description="Number of statistics included")
    citations_count: int = Field(default=0, description="Number of citations included")
    quotations_count: int = Field(default=0, description="Number of quotations included")


class ContentGenerationRequest(BaseModel):
    """API request for content generation."""

    client_name: str = Field(
        ...,
        min_length=1,
        description="Name of the client/entity to optimize for",
    )
    target_question: str = Field(
        ...,
        min_length=10,
        description="The question to answer with GEO-optimized content",
    )
    reference_urls: list[str] = Field(
        default_factory=list,
        description="URLs to harvest for research",
    )
    reference_documents: list[str] = Field(
        default_factory=list,
        description="Paths to documents to parse",
    )
    language_override: str | None = Field(
        default=None,
        description="Override automatic language detection (e.g., 'zh-TW')",
    )
    target_word_count: int = Field(
        default=500,
        ge=100,
        le=3000,
        description="Target word count for generated content (100-3000)",
    )


class ContentGenerationResponse(BaseModel):
    """API response for content generation."""

    # Request tracking
    job_id: str = Field(..., description="Unique job identifier")
    trace_id: str = Field(..., description="OpenAI Trace identifier")
    trace_url: str = Field(..., description="URL to view trace in OpenAI dashboard")

    # Language
    detected_language: str = Field(..., description="Human-readable language name")
    language_code: str = Field(..., description="Language code used")
    dialect: str | None = Field(default=None, description="Detected dialect")
    writing_direction: Literal["ltr", "rtl"] = Field(..., description="Text direction")

    # Generated content
    content: str = Field(..., description="Final optimized content")
    word_count: int = Field(..., description="Word count of final content")

    # Evaluation
    selected_draft: Literal["A", "B"] = Field(..., description="Which draft was selected")
    evaluation_score: float = Field(..., description="Final evaluation score (0-100)")
    evaluation_iterations: int = Field(..., description="Number of evaluation iterations")

    # GEO Performance Commentary (detailed in geo_commentary.py)
    geo_commentary: dict = Field(..., description="GEO performance analysis")

    # Enhanced GEO Insights (NEW)
    geo_insights: dict | None = Field(
        default=None,
        description="Enhanced GEO insights with actionable recommendations",
    )

    # Technical outputs
    schema_markup: dict = Field(default_factory=dict, description="Schema.org markup")
    geo_analysis: dict = Field(..., description="GEO metrics summary")

    # Metadata
    generation_time_ms: int = Field(..., description="Total generation time in milliseconds")
    models_used: dict = Field(..., description="Models used for each agent")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response generation timestamp",
    )


class TraceMetadata(BaseModel):
    """Metadata captured in each trace for observability."""

    # Request identification
    trace_id: str = Field(..., description="Unique trace identifier")
    request_id: str = Field(..., description="Request identifier")
    client_name: str = Field(..., description="Client name")

    # Timing
    request_timestamp: datetime = Field(..., description="When request was received")
    completion_timestamp: datetime | None = Field(
        default=None,
        description="When request completed",
    )
    total_duration_ms: int | None = Field(
        default=None,
        description="Total processing time in milliseconds",
    )

    # Language
    input_language: str = Field(..., description="Detected input language code")
    detected_dialect: str | None = Field(default=None, description="Detected dialect")

    # Research metrics
    sources_harvested: int = Field(default=0, description="Number of sources harvested")
    statistics_found: int = Field(default=0, description="Statistics extracted")
    quotes_collected: int = Field(default=0, description="Quotations collected")

    # Generation metrics
    draft_a_tokens: int = Field(default=0, description="Tokens used for Draft A")
    draft_b_tokens: int = Field(default=0, description="Tokens used for Draft B")

    # Evaluation metrics
    evaluation_iterations: int = Field(default=0, description="Evaluation iterations")
    draft_a_final_score: float = Field(default=0.0, description="Draft A final score")
    draft_b_final_score: float = Field(default=0.0, description="Draft B final score")
    selected_draft: str = Field(default="", description="Selected draft (A or B)")

    # Cost tracking
    total_input_tokens: int = Field(default=0, description="Total input tokens")
    total_output_tokens: int = Field(default=0, description="Total output tokens")
    estimated_cost_usd: float = Field(default=0.0, description="Estimated cost in USD")

    # Status
    completion_status: Literal["pending", "success", "failed"] = Field(
        default="pending",
        description="Completion status",
    )
    error_message: str | None = Field(default=None, description="Error message if failed")
