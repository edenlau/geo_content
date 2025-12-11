"""
Pydantic models for GEO Content Platform.
"""

from geo_content.models.evaluation import (
    DraftEvaluation,
    EvaluationResult,
    EvaluationScore,
    RevisionFeedback,
)
from geo_content.models.geo_commentary import (
    EEATAnalysis,
    GEOPerformanceCommentary,
    GEOStrategyAnalysis,
)
from geo_content.models.geo_insights import (
    BenchmarkComparison,
    ContentStructureScore,
    EnhancedSchemaMarkup,
    EntityMention,
    GEOInsights,
    ImplementationAction,
    ImplementationChecklist,
    KeywordAnalysis,
    MetricGap,
    MultiFormatExport,
    SourceAnalysis,
    SourceQuality,
)
from geo_content.models.rewrite_schemas import (
    ContentRewriteRequest,
    ContentRewriteResponse,
    GEOOptimizationsApplied,
    RewriteComparison,
    RewriteStyleInfo,
    RewriteStylesResponse,
    RewriteToneInfo,
    UrlContentPreview,
)
from geo_content.models.schemas import (
    CitationItem,
    ContentDraft,
    ContentGenerationRequest,
    ContentGenerationResponse,
    LanguageDetectionResult,
    QuotationItem,
    ResearchBrief,
    StatisticItem,
    TraceMetadata,
)

__all__ = [
    # Schemas
    "LanguageDetectionResult",
    "StatisticItem",
    "QuotationItem",
    "CitationItem",
    "ResearchBrief",
    "ContentDraft",
    "ContentGenerationRequest",
    "ContentGenerationResponse",
    "TraceMetadata",
    # Evaluation
    "EvaluationScore",
    "DraftEvaluation",
    "EvaluationResult",
    "RevisionFeedback",
    # GEO Commentary
    "GEOStrategyAnalysis",
    "EEATAnalysis",
    "GEOPerformanceCommentary",
    # GEO Insights
    "GEOInsights",
    "ImplementationChecklist",
    "ImplementationAction",
    "SourceAnalysis",
    "SourceQuality",
    "KeywordAnalysis",
    "EntityMention",
    "BenchmarkComparison",
    "MetricGap",
    "ContentStructureScore",
    "EnhancedSchemaMarkup",
    "MultiFormatExport",
    # Rewrite Schemas
    "ContentRewriteRequest",
    "ContentRewriteResponse",
    "RewriteComparison",
    "GEOOptimizationsApplied",
    "RewriteStyleInfo",
    "RewriteToneInfo",
    "RewriteStylesResponse",
    "UrlContentPreview",
]
