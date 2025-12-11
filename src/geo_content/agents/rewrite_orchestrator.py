"""
Multi-Agent Orchestrator for Content Rewrite.

Coordinates the content rewrite workflow:
1. Source Content Extraction (URL or file)
2. Language Detection
3. Research Phase
4. Rewrite Generation with GEO optimizations
5. Evaluation Loop
6. Generate Comparison & GEO Insights
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime

from geo_content.agents.evaluator_agent import evaluator_agent
from geo_content.agents.research_agent import research_agent
from geo_content.agents.rewriter_agent import rewriter_agent
from geo_content.config import settings
from geo_content.models import (
    ContentDraft,
    GEOInsights,
    LanguageDetectionResult,
    ResearchBrief,
)
from geo_content.models.rewrite_schemas import (
    ContentRewriteRequest,
    ContentRewriteResponse,
    GEOOptimizationsApplied,
    RewriteComparison,
    UrlContentPreview,
)
from geo_content.pipeline.pathway_harvester import PathwayWebHarvester
from geo_content.tools.document_parser import parse_document
from geo_content.tools.format_exporters import (
    enhanced_schema_generator,
    multi_format_exporter,
)
from geo_content.tools.geo_analyzers import geo_insights_analyzer
from geo_content.tools.language_detector import detect_language
from geo_content.tools.rtl_formatter import format_rtl_content
from geo_content.tools.word_count import count_words

logger = logging.getLogger(__name__)


class GEORewriteWorkflow:
    """
    Main workflow orchestrator for GEO content rewriting.

    Coordinates all agents in the content rewrite pipeline.
    """

    def __init__(self):
        """Initialize the rewrite workflow orchestrator."""
        self.research_agent = research_agent
        self.rewriter = rewriter_agent
        self.evaluator = evaluator_agent

    async def rewrite_content(
        self,
        request: ContentRewriteRequest,
    ) -> ContentRewriteResponse:
        """
        Execute the full content rewrite workflow.

        Args:
            request: Content rewrite request

        Returns:
            ContentRewriteResponse with rewritten content and analysis
        """
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        job_id = f"rewrite_{uuid.uuid4().hex[:12]}"

        logger.info(f"[{job_id}] Starting content rewrite workflow")

        try:
            # Step 1: Extract source content
            phase_start = time.time()
            logger.info(f"[{job_id}] Extracting source content")
            original_content, source_title = await self._extract_source_content(request)
            original_word_count = count_words(original_content, "en")
            logger.info(
                f"[{job_id}] Source extraction completed: {original_word_count} words "
                f"({int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 2: Language Detection
            phase_start = time.time()
            logger.info(f"[{job_id}] Detecting language")
            language_result = await self._detect_language(
                original_content,
                request.language_override,
            )
            logger.info(
                f"[{job_id}] Language detection completed: {language_result.language_code} "
                f"(confidence={language_result.confidence:.2f}, {int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 3: Research Phase (enhance with additional facts/stats)
            phase_start = time.time()
            logger.info(f"[{job_id}] Starting research phase")

            # Extract topic from original content for research
            topic = self._extract_topic_from_content(original_content, source_title)

            research_brief = await self._conduct_research(
                client_name=request.client_name or "the subject",
                target_question=topic,
                reference_urls=request.reference_urls,
                reference_documents=request.reference_documents,
                language_code=language_result.language_code,
            )
            logger.info(
                f"[{job_id}] Research phase completed: "
                f"sources={len(research_brief.source_urls)}, "
                f"stats={len(research_brief.statistics)}, "
                f"quotes={len(research_brief.quotations)} "
                f"({int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 4: Rewrite with GEO optimizations
            phase_start = time.time()
            logger.info(f"[{job_id}] Starting content rewrite")
            rewritten_draft = await self.rewriter.rewrite_content(
                original_content=original_content,
                research_brief=research_brief,
                style=request.style,
                tone=request.tone,
                client_name=request.client_name,
                target_word_count=request.target_word_count,
                preserve_structure=request.preserve_structure,
            )
            logger.info(
                f"[{job_id}] Rewrite completed: {rewritten_draft.word_count} words "
                f"({int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 5: Evaluation Loop
            phase_start = time.time()
            logger.info(f"[{job_id}] Starting evaluation")
            final_result = await self._evaluation_loop(
                draft=rewritten_draft,
                target_question=topic,
                client_name=request.client_name or "the subject",
                language_code=language_result.language_code,
                research_brief=research_brief,
                original_content=original_content,
                style=request.style,
                tone=request.tone,
                target_word_count=request.target_word_count,
                preserve_structure=request.preserve_structure,
            )
            logger.info(
                f"[{job_id}] Evaluation completed: score={final_result['score']:.1f}, "
                f"iterations={final_result['iterations']} "
                f"({int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 6: Analyze optimizations applied
            phase_start = time.time()
            logger.info(f"[{job_id}] Analyzing optimizations")
            optimizations = await self.rewriter.analyze_changes(
                original_content=original_content,
                rewritten_content=final_result["content"],
                language_code=language_result.language_code,
            )

            # Generate changes summary
            changes_summary = self.rewriter.generate_changes_summary(
                original_content=original_content,
                rewritten_content=final_result["content"],
                optimizations=optimizations,
            )
            logger.info(
                f"[{job_id}] Optimization analysis completed "
                f"({int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 7: Format content (RTL if Arabic)
            final_content = final_result["content"]
            if language_result.language_code.startswith("ar-"):
                rtl_result = format_rtl_content(final_content, language_result.language_code)
                final_content = rtl_result["content"]

            # Step 8: Generate GEO Insights
            logger.info(f"[{job_id}] Generating GEO insights")
            geo_insights = self._generate_geo_insights(
                evaluation=final_result["evaluation"],
                selected_draft=final_result["draft_eval"],
                commentary=final_result["commentary"],
                research_brief=research_brief,
                content=final_content,
                client_name=request.client_name or "the subject",
                target_question=topic,
            )

            # Calculate totals
            total_time_ms = int((time.time() - start_time) * 1000)
            final_word_count = count_words(final_content, language_result.language_code)

            logger.info(
                f"[{job_id}] Rewrite workflow completed successfully: "
                f"total_time={total_time_ms}ms, "
                f"original_words={original_word_count}, "
                f"rewritten_words={final_word_count}"
            )

            # Build comparison
            comparison = RewriteComparison(
                original_content=original_content,
                original_word_count=original_word_count,
                original_language=language_result.detected_language,
                rewritten_content=final_content,
                rewritten_word_count=final_word_count,
                changes_summary=changes_summary,
            )

            # Build response
            return ContentRewriteResponse(
                job_id=job_id,
                trace_id=trace_id,
                trace_url=f"https://platform.openai.com/traces/{trace_id}",
                detected_language=language_result.detected_language,
                language_code=language_result.language_code,
                writing_direction=language_result.writing_direction,
                comparison=comparison,
                optimizations_applied=optimizations,
                style_applied=request.style,
                tone_applied=request.tone,
                evaluation_score=final_result["score"],
                evaluation_iterations=final_result["iterations"],
                geo_commentary=final_result["commentary"].to_display_dict(),
                geo_insights=geo_insights.to_display_dict() if geo_insights else None,
                generation_time_ms=total_time_ms,
                models_used={
                    "research": settings.openai_model_writer,
                    "rewriter": settings.openai_model_evaluator,
                    "evaluator": settings.openai_model_evaluator,
                },
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"[{job_id}] Rewrite workflow error: {e}")
            raise

    async def fetch_url_preview(self, url: str) -> UrlContentPreview:
        """
        Fetch and preview content from a URL.

        Args:
            url: URL to fetch content from

        Returns:
            UrlContentPreview with content and metadata
        """
        start_time = time.time()

        async with PathwayWebHarvester(timeout=30) as harvester:
            result = await harvester.harvest_url(url)

        if not result:
            raise ValueError(f"Failed to fetch content from URL: {url}")

        fetch_time_ms = int((time.time() - start_time) * 1000)

        # Detect language
        language_result = detect_language(result.content[:1000])

        # Create preview (first ~500 chars)
        preview = result.content[:500]
        if len(result.content) > 500:
            preview += "..."

        return UrlContentPreview(
            url=url,
            title=result.title or "Untitled",
            content_preview=preview,
            full_content=result.content,
            word_count=result.word_count,
            language=language_result.detected_language,
            fetch_time_ms=fetch_time_ms,
        )

    async def _extract_source_content(
        self,
        request: ContentRewriteRequest,
    ) -> tuple[str, str]:
        """
        Extract source content from URL, file, or text.

        Args:
            request: Content rewrite request

        Returns:
            Tuple of (content, title)
        """
        if request.source_url:
            # Fetch from URL
            async with PathwayWebHarvester(timeout=30) as harvester:
                result = await harvester.harvest_url(request.source_url)

            if not result:
                raise ValueError(f"Failed to fetch content from URL: {request.source_url}")

            return result.content, result.title or "Untitled"

        elif request.source_file_path:
            # Parse from file
            parsed = parse_document(request.source_file_path)
            if not parsed:
                raise ValueError(f"Failed to parse document: {request.source_file_path}")

            return parsed.content, parsed.title

        elif request.source_text:
            # Use provided text directly
            return request.source_text, "Provided Content"

        else:
            raise ValueError("No source content provided")

    async def _detect_language(
        self,
        text: str,
        override: str | None = None,
    ) -> LanguageDetectionResult:
        """Detect language or use override."""
        if override:
            return LanguageDetectionResult(
                detected_language=override,
                language_code=override,
                confidence=1.0,
                writing_direction="rtl" if override.startswith("ar-") else "ltr",
            )
        return detect_language(text)

    def _extract_topic_from_content(
        self,
        content: str,
        title: str,
    ) -> str:
        """
        Extract the main topic from content for research.

        Args:
            content: The content text
            title: The title of the content

        Returns:
            A topic/question suitable for research
        """
        # Use title if available and meaningful
        if title and len(title) > 10 and title != "Untitled":
            return f"Information about: {title}"

        # Otherwise, use first paragraph as topic
        paragraphs = content.split("\n\n")
        if paragraphs:
            first_para = paragraphs[0].strip()
            if len(first_para) > 50:
                # Truncate to reasonable length
                return f"Information about: {first_para[:200]}..."

        return "General topic from the provided content"

    async def _conduct_research(
        self,
        client_name: str,
        target_question: str,
        reference_urls: list[str],
        reference_documents: list[str],
        language_code: str,
    ) -> ResearchBrief:
        """Conduct research using the Research Agent."""
        return await self.research_agent.conduct_research(
            client_name=client_name,
            target_question=target_question,
            reference_urls=reference_urls,
            reference_documents=reference_documents,
            language_code=language_code,
        )

    async def _evaluation_loop(
        self,
        draft: ContentDraft,
        target_question: str,
        client_name: str,
        language_code: str,
        research_brief: ResearchBrief,
        original_content: str,
        style: str,
        tone: str,
        target_word_count: int | None,
        preserve_structure: bool,
        max_iterations: int | None = None,
    ) -> dict:
        """
        Run evaluation loop with potential revisions.

        For rewrite, we evaluate a single draft (not comparing two).
        """
        if max_iterations is None:
            max_iterations = settings.max_iterations

        iteration = 0
        current_draft = draft

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Evaluation iteration {iteration}/{max_iterations}")

            # Create a "dummy" second draft for evaluation (copy of first)
            # This allows reuse of the existing evaluator
            dummy_draft = ContentDraft(
                draft_id="B",
                content=current_draft.content,
                word_count=current_draft.word_count,
                model_used=current_draft.model_used,
                generation_time_ms=0,
                statistics_count=current_draft.statistics_count,
                citations_count=current_draft.citations_count,
                quotations_count=current_draft.quotations_count,
            )

            # Evaluate
            evaluation = await self.evaluator.evaluate_drafts(
                draft_a=current_draft,
                draft_b=dummy_draft,
                target_question=target_question,
                client_name=client_name,
                language_code=language_code,
            )

            # Check if we pass threshold
            if evaluation.passes_threshold:
                logger.info(f"Quality threshold passed at iteration {iteration}")
                break

            # If not last iteration, attempt revision
            if iteration < max_iterations and evaluation.revision_needed:
                logger.info(f"Revision needed for rewritten content")

                # Re-rewrite with updated research
                current_draft = await self.rewriter.rewrite_content(
                    original_content=original_content,
                    research_brief=research_brief,
                    style=style,
                    tone=tone,
                    client_name=client_name,
                    target_word_count=target_word_count,
                    preserve_structure=preserve_structure,
                )

        # Generate commentary
        commentary = await self.evaluator.generate_commentary(
            selected_content=current_draft.content,
            alternative_content=current_draft.content,  # Same content for rewrite
            selected_draft="A",
            evaluation_result=evaluation,
            language_code=language_code,
            verification_stats=research_brief.verification_stats if research_brief else None,
        )

        return {
            "content": current_draft.content,
            "draft": current_draft,
            "score": evaluation.draft_a.overall_score,
            "iterations": iteration,
            "evaluation": evaluation,
            "draft_eval": evaluation.draft_a,
            "commentary": commentary,
        }

    def _generate_geo_insights(
        self,
        evaluation,
        selected_draft,
        commentary,
        research_brief: ResearchBrief,
        content: str,
        client_name: str,
        target_question: str,
    ) -> GEOInsights:
        """Generate comprehensive GEO insights."""
        # Implementation checklist
        implementation_checklist = geo_insights_analyzer.generate_implementation_checklist(
            evaluation=evaluation,
            selected_draft=selected_draft,
            commentary=commentary,
        )

        # Source quality analysis
        source_analysis = geo_insights_analyzer.analyze_source_quality(
            research_brief=research_brief,
        )

        # Keyword and entity analysis
        keyword_analysis = geo_insights_analyzer.analyze_keywords_entities(
            content=content,
            client_name=client_name,
            target_question=target_question,
        )

        # Benchmark comparison
        benchmark_comparison = geo_insights_analyzer.generate_benchmark_comparison(
            selected_draft=selected_draft,
        )

        # Structure analysis
        structure_analysis = geo_insights_analyzer.analyze_content_structure(
            content=content,
        )

        # Enhanced schema markup
        enhanced_schema = self._generate_enhanced_schema(
            client_name=client_name,
            target_question=target_question,
            content=content,
        )

        # Multi-format export
        multi_format = self._generate_multi_format_export(
            content=content,
            schema_markup=enhanced_schema.article,
        )

        return GEOInsights(
            implementation_checklist=implementation_checklist,
            source_analysis=source_analysis,
            keyword_analysis=keyword_analysis,
            benchmark_comparison=benchmark_comparison,
            structure_analysis=structure_analysis,
            enhanced_schema=enhanced_schema,
            multi_format_export=multi_format,
        )

    def _generate_enhanced_schema(
        self,
        client_name: str,
        target_question: str,
        content: str,
    ):
        """Generate enhanced schema markup."""
        from geo_content.models import EnhancedSchemaMarkup

        article_schema = enhanced_schema_generator.generate_article_schema(
            client_name=client_name,
            question=target_question,
            content=content,
        )

        faq_schema = enhanced_schema_generator.generate_faq_schema(content)
        howto_schema = enhanced_schema_generator.generate_howto_schema(
            content=content,
            question=target_question,
        )
        org_schema = enhanced_schema_generator.generate_organization_schema(client_name)

        return EnhancedSchemaMarkup(
            article=article_schema,
            faq=faq_schema,
            how_to=howto_schema,
            organization=org_schema,
            breadcrumb=None,
        )

    def _generate_multi_format_export(
        self,
        content: str,
        schema_markup: dict,
    ):
        """Generate multi-format exports."""
        from geo_content.models import MultiFormatExport

        html = multi_format_exporter.export_html(content, schema_markup)
        markdown = multi_format_exporter.export_markdown(content)
        plain_text = multi_format_exporter.export_plain_text(content)
        json_ld = multi_format_exporter.export_json_ld(schema_markup)

        return MultiFormatExport(
            html=html,
            markdown=markdown,
            plain_text=plain_text,
            json_ld=json_ld,
        )


# Create default orchestrator instance
geo_rewrite_workflow = GEORewriteWorkflow()


async def rewrite_geo_content(
    request: ContentRewriteRequest,
) -> ContentRewriteResponse:
    """
    Convenience function to rewrite content with GEO optimizations.

    Args:
        request: Content rewrite request

    Returns:
        ContentRewriteResponse with rewritten content
    """
    return await geo_rewrite_workflow.rewrite_content(request)
