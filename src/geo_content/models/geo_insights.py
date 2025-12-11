"""
GEO Insights models for enhanced output analysis.

Provides actionable insights to help users maximize GEO performance.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ImplementationAction(BaseModel):
    """A single actionable item in the implementation checklist."""

    priority: Literal["high", "medium", "low"] = Field(
        ...,
        description="Priority level of this action",
    )
    category: str = Field(
        ...,
        description="Category (e.g., 'citations', 'statistics', 'structure')",
    )
    action: str = Field(
        ...,
        description="Specific action to take",
    )
    impact: str = Field(
        ...,
        description="Expected impact on GEO visibility (e.g., '+15-20%')",
    )
    example: str | None = Field(
        default=None,
        description="Concrete example of how to implement",
    )
    current_gap: str | None = Field(
        default=None,
        description="Current gap or deficiency",
    )


class ImplementationChecklist(BaseModel):
    """Prioritized checklist for implementing GEO improvements."""

    actions: list[ImplementationAction] = Field(
        default_factory=list,
        description="List of implementation actions",
    )
    total_estimated_impact: str = Field(
        ...,
        description="Total estimated visibility impact (e.g., '+40-60%')",
    )


class SourceQuality(BaseModel):
    """Analysis of a single source's quality."""

    url: str = Field(..., description="Source URL")
    domain_authority: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Estimated domain authority score (0-100)",
    )
    content_recency: str | None = Field(
        default=None,
        description="Content recency (e.g., '2024', 'Last updated 2023')",
    )
    relevance_score: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Relevance score to the topic (0-1)",
    )
    source_type: Literal["government", "academic", "industry", "news", "other"] = Field(
        ...,
        description="Type of source",
    )
    credibility_rating: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Overall credibility rating",
    )


class SourceAnalysis(BaseModel):
    """Comprehensive analysis of research sources."""

    sources_used: list[SourceQuality] = Field(
        default_factory=list,
        description="Individual source quality assessments",
    )
    source_diversity: dict[str, int] = Field(
        default_factory=dict,
        description="Count of sources by type (government, academic, etc.)",
    )
    average_credibility: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Average credibility across all sources",
    )
    recommendation: str = Field(
        default="",
        description="Recommendation for improving source quality",
    )


class EntityMention(BaseModel):
    """Analysis of a primary entity."""

    entity: str = Field(..., description="Entity name")
    mentions: int = Field(..., description="Number of mentions")
    optimal_range: str = Field(
        ...,
        description="Optimal mention range (e.g., '4-6')",
    )
    status: Literal["optimal", "under", "over"] = Field(
        ...,
        description="Whether mentions are optimal, too few, or too many",
    )


class KeywordAnalysis(BaseModel):
    """Keyword and entity optimization analysis."""

    primary_entities: list[EntityMention] = Field(
        default_factory=list,
        description="Primary entities and their mention frequency",
    )
    semantic_coverage: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Topics covered and missing (covered_topics, missing_topics)",
    )
    keyword_density_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall keyword density optimization score (0-100)",
    )


class MetricGap(BaseModel):
    """Gap analysis for a single metric."""

    current: int | float = Field(..., description="Current value")
    top_performers_avg: int | float = Field(
        ...,
        description="Average for top-performing content",
    )
    gap: int | float = Field(..., description="Gap (current - target)")
    status: Literal["ahead", "at_target", "behind"] = Field(
        ...,
        description="Whether current value is ahead, at, or behind target",
    )


class BenchmarkComparison(BaseModel):
    """Benchmark comparison against top-performing content."""

    target_metrics: dict[str, MetricGap] = Field(
        default_factory=dict,
        description="Metrics comparison (statistics_count, citations_count, etc.)",
    )
    overall_competitiveness: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Overall competitiveness score (0-100)",
    )
    competitive_advantages: list[str] = Field(
        default_factory=list,
        description="Areas where content exceeds benchmarks",
    )
    improvement_areas: list[str] = Field(
        default_factory=list,
        description="Areas where content falls short",
    )


class ContentStructureScore(BaseModel):
    """Analysis of content structure for AI parsing."""

    heading_hierarchy: dict[str, int] = Field(
        default_factory=dict,
        description="Count of headings by level (h1, h2, h3, etc.)",
    )
    heading_issues: list[str] = Field(
        default_factory=list,
        description="Issues with heading structure",
    )
    list_usage: dict[str, int] = Field(
        default_factory=dict,
        description="Count of list types (bullet_lists, numbered_lists)",
    )
    table_usage: int = Field(
        default=0,
        description="Number of tables used",
    )
    structure_quality_score: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Overall structure quality score (0-100)",
    )
    recommendation: str = Field(
        default="",
        description="Recommendation for improving structure",
    )


class EnhancedSchemaMarkup(BaseModel):
    """Enhanced schema markup with multiple types."""

    article: dict = Field(
        default_factory=dict,
        description="Schema.org Article markup",
    )
    faq: dict | None = Field(
        default=None,
        description="Schema.org FAQPage markup (if Q&A detected)",
    )
    how_to: dict | None = Field(
        default=None,
        description="Schema.org HowTo markup (if steps detected)",
    )
    organization: dict | None = Field(
        default=None,
        description="Schema.org Organization markup for client entity",
    )
    breadcrumb: dict | None = Field(
        default=None,
        description="Schema.org BreadcrumbList markup",
    )


class MultiFormatExport(BaseModel):
    """Multi-format export options for content."""

    html: str = Field(..., description="HTML with semantic markup")
    markdown: str = Field(..., description="Markdown format for CMS")
    plain_text: str = Field(..., description="Plain text version")
    json_ld: str = Field(..., description="JSON-LD schema markup")


class GEOInsights(BaseModel):
    """Complete GEO insights package for user presentation."""

    implementation_checklist: ImplementationChecklist = Field(
        ...,
        description="Actionable implementation checklist",
    )
    source_analysis: SourceAnalysis = Field(
        ...,
        description="Research source quality analysis",
    )
    keyword_analysis: KeywordAnalysis = Field(
        ...,
        description="Keyword and entity optimization analysis",
    )
    benchmark_comparison: BenchmarkComparison = Field(
        ...,
        description="Comparison with top-performing content",
    )
    structure_analysis: ContentStructureScore = Field(
        ...,
        description="Content structure analysis",
    )
    enhanced_schema: EnhancedSchemaMarkup = Field(
        ...,
        description="Enhanced schema markup with multiple types",
    )
    multi_format_export: MultiFormatExport | None = Field(
        default=None,
        description="Pre-formatted exports in multiple formats",
    )

    def to_display_dict(self) -> dict:
        """Convert to display-friendly dictionary format."""
        return {
            "implementation_checklist": {
                "actions": [
                    {
                        "priority": action.priority,
                        "category": action.category,
                        "action": action.action,
                        "impact": action.impact,
                        "example": action.example,
                        "current_gap": action.current_gap,
                    }
                    for action in self.implementation_checklist.actions
                ],
                "total_estimated_impact": self.implementation_checklist.total_estimated_impact,
            },
            "source_analysis": {
                "sources_used": [
                    {
                        "url": s.url,
                        "domain_authority": s.domain_authority,
                        "recency": s.content_recency,
                        "type": s.source_type,
                        "credibility": s.credibility_rating,
                    }
                    for s in self.source_analysis.sources_used
                ],
                "source_diversity": self.source_analysis.source_diversity,
                "average_credibility": round(self.source_analysis.average_credibility, 2),
                "recommendation": self.source_analysis.recommendation,
            },
            "keyword_analysis": {
                "primary_entities": [
                    {
                        "entity": e.entity,
                        "mentions": e.mentions,
                        "optimal_range": e.optimal_range,
                        "status": e.status,
                    }
                    for e in self.keyword_analysis.primary_entities
                ],
                "semantic_coverage": self.keyword_analysis.semantic_coverage,
                "keyword_density_score": round(self.keyword_analysis.keyword_density_score, 1),
            },
            "benchmark_comparison": {
                "target_metrics": {
                    metric: {
                        "current": gap.current,
                        "target": gap.top_performers_avg,
                        "gap": gap.gap,
                        "status": gap.status,
                    }
                    for metric, gap in self.benchmark_comparison.target_metrics.items()
                },
                "overall_competitiveness": self.benchmark_comparison.overall_competitiveness,
                "competitive_advantages": self.benchmark_comparison.competitive_advantages,
                "improvement_areas": self.benchmark_comparison.improvement_areas,
            },
            "structure_analysis": {
                "heading_hierarchy": self.structure_analysis.heading_hierarchy,
                "list_usage": self.structure_analysis.list_usage,
                "tables": self.structure_analysis.table_usage,
                "quality_score": self.structure_analysis.structure_quality_score,
                "recommendation": self.structure_analysis.recommendation,
            },
            "enhanced_schema": {
                "article": self.enhanced_schema.article,
                "faq": self.enhanced_schema.faq,
                "how_to": self.enhanced_schema.how_to,
                "organization": self.enhanced_schema.organization,
                "breadcrumb": self.enhanced_schema.breadcrumb,
            },
        }
