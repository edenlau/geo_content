"""
GEO Analyzers for comprehensive content analysis.

Provides detailed insights on implementation actions, source quality,
keyword optimization, benchmarks, and content structure.
"""

import re
from collections import Counter
from typing import Any
from urllib.parse import urlparse

from geo_content.models.evaluation import DraftEvaluation, EvaluationResult
from geo_content.models.geo_commentary import GEOPerformanceCommentary
from geo_content.models.geo_insights import (
    BenchmarkComparison,
    ContentStructureScore,
    EntityMention,
    ImplementationAction,
    ImplementationChecklist,
    KeywordAnalysis,
    MetricGap,
    SourceAnalysis,
    SourceQuality,
)
from geo_content.models.schemas import ResearchBrief


class GEOInsightsAnalyzer:
    """Analyzes GEO output to generate actionable insights."""

    def __init__(self):
        """Initialize the analyzer."""
        self.domain_authority_cache: dict[str, int] = {}

    def generate_implementation_checklist(
        self,
        evaluation: EvaluationResult,
        selected_draft: DraftEvaluation,
        commentary: GEOPerformanceCommentary,
    ) -> ImplementationChecklist:
        """
        Generate prioritized implementation checklist.

        Args:
            evaluation: Evaluation result
            selected_draft: Selected draft evaluation
            commentary: GEO performance commentary

        Returns:
            ImplementationChecklist with actionable items
        """
        actions: list[ImplementationAction] = []

        # Check citations gap
        if selected_draft.citations_count == 0:
            actions.append(
                ImplementationAction(
                    priority="high",
                    category="citations",
                    action="Add authoritative source links",
                    impact="Increases E-E-A-T Trust score by 15-20%",
                    example="Add inline links to official government statistics or academic research",
                    current_gap=f"{selected_draft.citations_count} citations found",
                )
            )
        elif selected_draft.citations_count < 3:
            actions.append(
                ImplementationAction(
                    priority="medium",
                    category="citations",
                    action="Increase number of authoritative citations",
                    impact="Improves credibility and visibility by 10-15%",
                    example="Target 4-5 citations from diverse authoritative sources",
                    current_gap=f"Only {selected_draft.citations_count} citation(s), recommended 4-5",
                )
            )

        # Check statistics gap
        if selected_draft.statistics_count < 5:
            gap = 5 - selected_draft.statistics_count
            actions.append(
                ImplementationAction(
                    priority="high" if gap > 3 else "medium",
                    category="statistics",
                    action=f"Add {gap} more statistical data points",
                    impact="Statistics boost visibility by 25-40%",
                    example="Include specific numbers, percentages, and quantitative data from research",
                    current_gap=f"{selected_draft.statistics_count} statistics (target: 5+)",
                )
            )

        # Check quotations gap
        if selected_draft.quotations_count < 2:
            gap = 2 - selected_draft.quotations_count
            actions.append(
                ImplementationAction(
                    priority="medium",
                    category="quotations",
                    action=f"Add {gap} expert quotation(s)",
                    impact="Quotations improve authority by 27-40%",
                    example="Include quotes from industry experts, researchers, or official statements",
                    current_gap=f"{selected_draft.quotations_count} quotation(s) (target: 2+)",
                )
            )

        # Check fluency score
        fluency = selected_draft.scores.fluency_score
        if fluency < 90:
            actions.append(
                ImplementationAction(
                    priority="medium" if fluency > 80 else "high",
                    category="fluency",
                    action="Improve writing fluency and readability",
                    impact="Better fluency increases visibility by 24-30%",
                    example="Review sentence structure, transitions, and natural flow",
                    current_gap=f"Fluency score: {fluency:.1f}/100 (target: 90+)",
                )
            )

        # Check E-E-A-T score
        eeat_score = commentary.eeat_analysis.overall_eeat_score
        if eeat_score < 8:
            actions.append(
                ImplementationAction(
                    priority="high",
                    category="eeat",
                    action="Strengthen E-E-A-T signals",
                    impact="Critical for AI engine trust and visibility",
                    example="Add author credentials, expert quotes, and verifiable facts",
                    current_gap=f"E-E-A-T score: {eeat_score}/10 (target: 8+)",
                )
            )

        # Sort by priority (high > medium > low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        actions.sort(key=lambda x: priority_order[x.priority])

        # Estimate total impact
        total_impact = self._estimate_total_impact(actions)

        return ImplementationChecklist(
            actions=actions,
            total_estimated_impact=total_impact,
        )

    def _estimate_total_impact(self, actions: list[ImplementationAction]) -> str:
        """Estimate total visibility impact from all actions."""
        # Parse impact ranges and sum them
        total_min = 0
        total_max = 0

        for action in actions:
            # Extract percentage ranges (e.g., "+15-20%")
            match = re.search(r'\+?(\d+)-(\d+)%', action.impact)
            if match:
                total_min += int(match.group(1))
                total_max += int(match.group(2))

        if total_min > 0:
            # Cap at reasonable maximum
            total_min = min(total_min, 80)
            total_max = min(total_max, 120)
            return f"+{total_min}-{total_max}%"
        return "+0%"

    def analyze_source_quality(self, research_brief: ResearchBrief) -> SourceAnalysis:
        """
        Analyze quality and credibility of research sources.

        Args:
            research_brief: Research brief with sources

        Returns:
            SourceAnalysis with quality metrics
        """
        sources_quality: list[SourceQuality] = []
        source_types: Counter = Counter()

        for source_url in research_brief.source_urls:
            # Determine source type based on domain
            source_type = self._classify_source_type(source_url)
            source_types[source_type] += 1

            # Estimate domain authority (simplified)
            domain_authority = self._estimate_domain_authority(source_url)

            # Estimate recency (simplified - would need actual parsing)
            recency = "Unknown"

            # Credibility rating
            credibility = self._rate_credibility(source_type, domain_authority)

            sources_quality.append(
                SourceQuality(
                    url=source_url,
                    domain_authority=domain_authority,
                    content_recency=recency,
                    relevance_score=0.85,  # Default high relevance
                    source_type=source_type,
                    credibility_rating=credibility,
                )
            )

        # Calculate average credibility
        credibility_scores = {
            "high": 0.9,
            "medium": 0.7,
            "low": 0.4,
        }
        avg_credibility = sum(
            credibility_scores[s.credibility_rating] for s in sources_quality
        ) / max(len(sources_quality), 1)

        # Generate recommendation
        recommendation = self._generate_source_recommendation(source_types, avg_credibility)

        return SourceAnalysis(
            sources_used=sources_quality,
            source_diversity=dict(source_types),
            average_credibility=avg_credibility,
            recommendation=recommendation,
        )

    def _classify_source_type(self, url: str) -> str:
        """Classify source type based on URL domain."""
        domain = urlparse(url).netloc.lower()

        # Government domains
        if any(tld in domain for tld in ['.gov', '.mil']):
            return "government"

        # Academic domains
        if any(tld in domain for tld in ['.edu', '.ac.']):
            return "academic"

        # News domains
        news_domains = ['news', 'times', 'post', 'journal', 'cnn', 'bbc', 'reuters']
        if any(news in domain for news in news_domains):
            return "news"

        # Industry/corporate
        if any(tld in domain for tld in ['.com', '.org', '.net']):
            return "industry"

        return "other"

    def _estimate_domain_authority(self, url: str) -> int:
        """Estimate domain authority (simplified)."""
        domain = urlparse(url).netloc.lower()

        # High authority domains
        high_authority = {
            '.gov': 90,
            '.mil': 90,
            '.edu': 85,
            'wikipedia.org': 95,
            'who.int': 95,
            'un.org': 95,
        }

        for pattern, score in high_authority.items():
            if pattern in domain:
                return score

        # Default medium authority
        return 65

    def _rate_credibility(self, source_type: str, domain_authority: int | None) -> str:
        """Rate source credibility."""
        if source_type in ["government", "academic"]:
            return "high"
        if domain_authority and domain_authority >= 80:
            return "high"
        if domain_authority and domain_authority >= 60:
            return "medium"
        return "low"

    def _generate_source_recommendation(
        self,
        source_types: Counter,
        avg_credibility: float,
    ) -> str:
        """Generate recommendation for improving source quality."""
        recommendations = []

        if source_types.get("academic", 0) == 0:
            recommendations.append("Add academic sources to strengthen expertise signals")

        if source_types.get("government", 0) == 0:
            recommendations.append("Include official government sources for authoritative data")

        if avg_credibility < 0.7:
            recommendations.append("Prioritize higher-credibility sources")

        if len(source_types) < 3:
            recommendations.append("Diversify source types for comprehensive coverage")

        return "; ".join(recommendations) if recommendations else "Source quality is excellent"

    def analyze_keywords_entities(
        self,
        content: str,
        client_name: str,
        target_question: str,
    ) -> KeywordAnalysis:
        """
        Analyze keyword density and entity mentions.

        Args:
            content: Generated content
            client_name: Client entity name
            target_question: Target question

        Returns:
            KeywordAnalysis with optimization insights
        """
        # Count entity mentions
        client_mentions = len(re.findall(re.escape(client_name), content, re.IGNORECASE))
        optimal_min = 4
        optimal_max = 8

        # Determine status
        if optimal_min <= client_mentions <= optimal_max:
            status = "optimal"
        elif client_mentions < optimal_min:
            status = "under"
        else:
            status = "over"

        primary_entities = [
            EntityMention(
                entity=client_name,
                mentions=client_mentions,
                optimal_range=f"{optimal_min}-{optimal_max}",
                status=status,
            )
        ]

        # Analyze semantic coverage (simplified)
        covered_topics = self._extract_covered_topics(content, target_question)
        missing_topics = self._identify_missing_topics(content, target_question)

        semantic_coverage = {
            "covered_topics": covered_topics,
            "missing_topics": missing_topics,
        }

        # Calculate keyword density score
        keyword_score = self._calculate_keyword_density_score(
            client_mentions,
            optimal_min,
            optimal_max,
        )

        return KeywordAnalysis(
            primary_entities=primary_entities,
            semantic_coverage=semantic_coverage,
            keyword_density_score=keyword_score,
        )

    def _extract_covered_topics(self, content: str, target_question: str) -> list[str]:
        """Extract topics covered in content (simplified)."""
        # This is a simplified implementation
        # In production, would use NLP to extract semantic topics
        topics = []

        # Common topic patterns
        if re.search(r'(eligibility|qualifications?|requirements?)', content, re.IGNORECASE):
            topics.append("eligibility")
        if re.search(r'(process|procedure|steps?|how to)', content, re.IGNORECASE):
            topics.append("application_process")
        if re.search(r'(benefits?|advantages?)', content, re.IGNORECASE):
            topics.append("benefits")
        if re.search(r'(timeline|duration|time)', content, re.IGNORECASE):
            topics.append("timeline")
        if re.search(r'(success rate|approval|statistics)', content, re.IGNORECASE):
            topics.append("success_rate")

        return topics[:5]  # Limit to 5 topics

    def _identify_missing_topics(self, content: str, target_question: str) -> list[str]:
        """Identify potentially missing topics (simplified)."""
        missing = []

        # Check for common missing elements
        if not re.search(r'(mistake|error|avoid|warning)', content, re.IGNORECASE):
            missing.append("common_mistakes")
        if not re.search(r'(cost|fee|price)', content, re.IGNORECASE):
            missing.append("costs")
        if not re.search(r'(timeline|duration)', content, re.IGNORECASE):
            missing.append("timeline")

        return missing[:3]  # Limit to 3 suggestions

    def _calculate_keyword_density_score(
        self,
        mentions: int,
        optimal_min: int,
        optimal_max: int,
    ) -> float:
        """Calculate keyword density optimization score."""
        if optimal_min <= mentions <= optimal_max:
            return 100.0
        elif mentions < optimal_min:
            # Penalize under-optimization
            return max(0, (mentions / optimal_min) * 100)
        else:
            # Penalize over-optimization
            excess = mentions - optimal_max
            penalty = min(excess * 10, 50)  # Cap penalty at 50
            return max(0, 100 - penalty)

    def generate_benchmark_comparison(
        self,
        selected_draft: DraftEvaluation,
    ) -> BenchmarkComparison:
        """
        Compare content against top-performing benchmarks.

        Args:
            selected_draft: Selected draft evaluation

        Returns:
            BenchmarkComparison with competitive analysis
        """
        # Define benchmark targets (industry averages for top performers)
        benchmarks = {
            "statistics_count": 5,
            "citations_count": 4,
            "quotations_count": 2,
        }

        target_metrics: dict[str, MetricGap] = {}

        # Statistics
        current_stats = selected_draft.statistics_count
        target_stats = benchmarks["statistics_count"]
        gap_stats = current_stats - target_stats
        target_metrics["statistics_count"] = MetricGap(
            current=current_stats,
            top_performers_avg=target_stats,
            gap=gap_stats,
            status="ahead" if gap_stats > 0 else ("at_target" if gap_stats == 0 else "behind"),
        )

        # Citations
        current_citations = selected_draft.citations_count
        target_citations = benchmarks["citations_count"]
        gap_citations = current_citations - target_citations
        target_metrics["citations_count"] = MetricGap(
            current=current_citations,
            top_performers_avg=target_citations,
            gap=gap_citations,
            status="ahead" if gap_citations > 0 else ("at_target" if gap_citations == 0 else "behind"),
        )

        # Quotations
        current_quotes = selected_draft.quotations_count
        target_quotes = benchmarks["quotations_count"]
        gap_quotes = current_quotes - target_quotes
        target_metrics["quotations_count"] = MetricGap(
            current=current_quotes,
            top_performers_avg=target_quotes,
            gap=gap_quotes,
            status="ahead" if gap_quotes > 0 else ("at_target" if gap_quotes == 0 else "behind"),
        )

        # Calculate overall competitiveness (0-100)
        competitiveness = self._calculate_competitiveness(target_metrics)

        # Identify advantages and improvement areas
        advantages = [
            f"Exceeds target by {abs(gap.gap)} in {metric}"
            for metric, gap in target_metrics.items()
            if gap.status == "ahead"
        ]

        improvement_areas = [
            f"Add {abs(gap.gap)} more {metric.replace('_count', '')}(s)"
            for metric, gap in target_metrics.items()
            if gap.status == "behind"
        ]

        return BenchmarkComparison(
            target_metrics=target_metrics,
            overall_competitiveness=competitiveness,
            competitive_advantages=advantages,
            improvement_areas=improvement_areas,
        )

    def _calculate_competitiveness(self, metrics: dict[str, MetricGap]) -> int:
        """Calculate overall competitiveness score (0-100)."""
        scores = []

        for gap in metrics.values():
            if gap.status == "ahead":
                scores.append(100)
            elif gap.status == "at_target":
                scores.append(100)
            else:
                # Penalize based on gap size
                if isinstance(gap.current, int) and isinstance(gap.top_performers_avg, int):
                    if gap.top_performers_avg > 0:
                        ratio = gap.current / gap.top_performers_avg
                        scores.append(int(ratio * 100))
                    else:
                        scores.append(0)

        return int(sum(scores) / max(len(scores), 1))

    def analyze_content_structure(self, content: str) -> ContentStructureScore:
        """
        Analyze content structure for AI parsing optimization.

        Args:
            content: Generated content

        Returns:
            ContentStructureScore with structure analysis
        """
        # Count headings by level
        heading_hierarchy = {
            "h1": len(re.findall(r'^# ', content, re.MULTILINE)),
            "h2": len(re.findall(r'^## ', content, re.MULTILINE)),
            "h3": len(re.findall(r'^### ', content, re.MULTILINE)),
            "h4": len(re.findall(r'^#### ', content, re.MULTILINE)),
        }

        # Check for heading issues
        heading_issues = []
        if heading_hierarchy["h1"] == 0:
            heading_issues.append("Missing H1 heading")
        if heading_hierarchy["h1"] > 1:
            heading_issues.append("Multiple H1 headings (should be only one)")
        if heading_hierarchy["h2"] == 0:
            heading_issues.append("No H2 subheadings (recommended for structure)")

        # Count lists
        list_usage = {
            "bullet_lists": len(re.findall(r'^\s*[-*+] ', content, re.MULTILINE)),
            "numbered_lists": len(re.findall(r'^\s*\d+\. ', content, re.MULTILINE)),
        }

        # Count tables (markdown tables)
        table_usage = len(re.findall(r'^\|.*\|$', content, re.MULTILINE)) // 3  # Rough estimate

        # Calculate structure quality score
        structure_score = self._calculate_structure_score(
            heading_hierarchy,
            heading_issues,
            list_usage,
            table_usage,
        )

        # Generate recommendation
        recommendation = self._generate_structure_recommendation(
            heading_hierarchy,
            list_usage,
            table_usage,
        )

        return ContentStructureScore(
            heading_hierarchy=heading_hierarchy,
            heading_issues=heading_issues,
            list_usage=list_usage,
            table_usage=table_usage,
            structure_quality_score=structure_score,
            recommendation=recommendation,
        )

    def _calculate_structure_score(
        self,
        headings: dict[str, int],
        issues: list[str],
        lists: dict[str, int],
        tables: int,
    ) -> int:
        """Calculate structure quality score (0-100)."""
        score = 100

        # Deduct for heading issues
        score -= len(issues) * 10

        # Reward good heading hierarchy
        if headings["h1"] == 1 and headings["h2"] >= 2:
            score += 10

        # Reward list usage
        total_lists = lists.get("bullet_lists", 0) + lists.get("numbered_lists", 0)
        if total_lists >= 2:
            score += 10

        # Reward table usage
        if tables > 0:
            score += 10

        return max(0, min(100, score))

    def _generate_structure_recommendation(
        self,
        headings: dict[str, int],
        lists: dict[str, int],
        tables: int,
    ) -> str:
        """Generate recommendation for improving structure."""
        recommendations = []

        if headings["h2"] < 2:
            recommendations.append("Add more H2 subheadings to improve scannability")

        total_lists = lists.get("bullet_lists", 0) + lists.get("numbered_lists", 0)
        if total_lists == 0:
            recommendations.append("Use bullet or numbered lists for better readability")

        if tables == 0:
            recommendations.append("Consider adding comparison tables for complex information")

        return "; ".join(recommendations) if recommendations else "Structure is well-optimized"


# Singleton instance
geo_insights_analyzer = GEOInsightsAnalyzer()
