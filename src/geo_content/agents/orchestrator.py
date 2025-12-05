"""
Multi-Agent Orchestrator for GEO Content Platform.

Coordinates the full content generation workflow:
1. Language Detection
2. Research Phase
3. Parallel Content Generation
4. Evaluation Loop
5. GEO Commentary Generation
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Literal

from geo_content.agents.evaluator_agent import evaluator_agent
from geo_content.agents.research_agent import research_agent
from geo_content.agents.writer_agent_a import writer_agent_a
from geo_content.agents.writer_agent_b import writer_agent_b
from geo_content.config import settings
from geo_content.models import (
    ContentDraft,
    ContentGenerationRequest,
    ContentGenerationResponse,
    EnhancedSchemaMarkup,
    EvaluationResult,
    GEOInsights,
    GEOPerformanceCommentary,
    LanguageDetectionResult,
    MultiFormatExport,
    ResearchBrief,
    TraceMetadata,
)
from geo_content.tools.format_exporters import (
    enhanced_schema_generator,
    multi_format_exporter,
)
from geo_content.tools.geo_analyzers import geo_insights_analyzer
from geo_content.tools.language_detector import detect_language
from geo_content.tools.rtl_formatter import format_rtl_content

logger = logging.getLogger(__name__)


class GEOContentWorkflow:
    """
    Main workflow orchestrator for GEO content generation.

    Coordinates all agents in the content generation pipeline.
    """

    def __init__(self):
        """Initialize the workflow orchestrator."""
        self.research_agent = research_agent
        self.writer_a = writer_agent_a
        self.writer_b = writer_agent_b
        self.evaluator = evaluator_agent

    async def generate_content(
        self,
        request: ContentGenerationRequest,
    ) -> ContentGenerationResponse:
        """
        Execute the full content generation workflow.

        Args:
            request: Content generation request

        Returns:
            ContentGenerationResponse with optimized content
        """
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Initialize trace metadata
        trace_metadata = TraceMetadata(
            trace_id=trace_id,
            request_id=job_id,
            client_name=request.client_name,
            request_timestamp=datetime.utcnow(),
            input_language="",
            completion_status="pending",
        )

        try:
            # Step 1: Language Detection
            phase_start = time.time()
            logger.info(f"[{job_id}] Starting language detection")
            language_result = await self._detect_language(
                request.target_question,
                request.language_override,
            )
            trace_metadata.input_language = language_result.language_code
            trace_metadata.detected_dialect = language_result.dialect
            logger.info(
                f"[{job_id}] Language detection completed: {language_result.language_code} "
                f"(confidence={language_result.confidence:.2f}, {int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 2: Research Phase
            phase_start = time.time()
            logger.info(f"[{job_id}] Starting research phase")
            research_brief = await self._conduct_research(
                client_name=request.client_name,
                target_question=request.target_question,
                reference_urls=request.reference_urls,
                reference_documents=request.reference_documents,
                language_code=language_result.language_code,
            )
            trace_metadata.sources_harvested = len(research_brief.source_urls)
            trace_metadata.statistics_found = len(research_brief.statistics)
            trace_metadata.quotes_collected = len(research_brief.quotations)
            logger.info(
                f"[{job_id}] Research phase completed: "
                f"sources={len(research_brief.source_urls)}, "
                f"facts={len(research_brief.key_facts)}, "
                f"stats={len(research_brief.statistics)}, "
                f"quotes={len(research_brief.quotations)} "
                f"({int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 3: Parallel Content Generation
            phase_start = time.time()
            logger.info(f"[{job_id}] Starting parallel content generation")
            draft_a, draft_b = await self._generate_drafts_parallel(
                client_name=request.client_name,
                target_question=request.target_question,
                research_brief=research_brief,
                target_word_count=request.target_word_count,
            )
            trace_metadata.draft_a_tokens = draft_a.word_count * 2  # Rough estimate
            trace_metadata.draft_b_tokens = draft_b.word_count * 2
            logger.info(
                f"[{job_id}] Parallel generation completed: "
                f"Draft A={draft_a.word_count} words, Draft B={draft_b.word_count} words "
                f"({int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 4: Evaluation Loop with E-E-A-T Enhancement
            phase_start = time.time()
            logger.info(f"[{job_id}] Starting evaluation loop")
            current_research_brief = research_brief
            current_draft_a = draft_a
            current_draft_b = draft_b
            research_iteration = 0

            while research_iteration <= settings.max_research_iterations:
                # Run evaluation loop
                final_result = await self._evaluation_loop(
                    draft_a=current_draft_a,
                    draft_b=current_draft_b,
                    target_question=request.target_question,
                    client_name=request.client_name,
                    language_code=language_result.language_code,
                    research_brief=current_research_brief,
                    target_word_count=request.target_word_count,
                )

                # Check E-E-A-T score
                eeat_score = final_result["commentary"].eeat_analysis.overall_eeat_score
                logger.info(
                    f"[{job_id}] E-E-A-T Score: {eeat_score}/10 "
                    f"(threshold: {settings.eeat_threshold})"
                )

                # If E-E-A-T score meets threshold or we've exhausted research iterations, break
                if eeat_score >= settings.eeat_threshold:
                    logger.info(f"[{job_id}] E-E-A-T threshold met")
                    break

                if research_iteration >= settings.max_research_iterations:
                    logger.info(
                        f"[{job_id}] Max research iterations reached "
                        f"({settings.max_research_iterations}), proceeding with current content"
                    )
                    break

                # E-E-A-T score below threshold - conduct focused research
                research_iteration += 1
                logger.info(
                    f"[{job_id}] E-E-A-T score below threshold, "
                    f"conducting additional research (iteration {research_iteration})"
                )

                # Conduct additional research focused on E-E-A-T gaps
                eeat_gaps = self._identify_eeat_gaps(final_result["commentary"].eeat_analysis)
                enhanced_research = await self._conduct_eeat_focused_research(
                    client_name=request.client_name,
                    target_question=request.target_question,
                    reference_urls=request.reference_urls,
                    language_code=language_result.language_code,
                    eeat_gaps=eeat_gaps,
                    existing_research=current_research_brief,
                )

                # Merge research briefs
                current_research_brief = self._merge_research_briefs(
                    current_research_brief, enhanced_research
                )

                # Regenerate drafts with enhanced research
                logger.info(f"[{job_id}] Regenerating drafts with enhanced research")
                current_draft_a, current_draft_b = await self._generate_drafts_parallel(
                    client_name=request.client_name,
                    target_question=request.target_question,
                    research_brief=current_research_brief,
                    target_word_count=request.target_word_count,
                )

            trace_metadata.evaluation_iterations = final_result["iterations"]
            trace_metadata.draft_a_final_score = final_result["draft_a_score"]
            trace_metadata.draft_b_final_score = final_result["draft_b_score"]
            trace_metadata.selected_draft = final_result["selected"]
            logger.info(
                f"[{job_id}] Evaluation loop completed: "
                f"iterations={final_result['iterations']}, "
                f"selected=Draft {final_result['selected']}, "
                f"score={final_result['score']:.1f} "
                f"({int((time.time() - phase_start) * 1000)}ms)"
            )

            # Step 5: Format content (RTL if Arabic)
            final_content = final_result["content"]
            if language_result.language_code.startswith("ar-"):
                rtl_result = format_rtl_content(final_content, language_result.language_code)
                final_content = rtl_result["content"]

            # Calculate totals
            total_time_ms = int((time.time() - start_time) * 1000)
            trace_metadata.total_duration_ms = total_time_ms
            trace_metadata.completion_status = "success"
            trace_metadata.completion_timestamp = datetime.utcnow()

            logger.info(
                f"[{job_id}] Workflow completed successfully: "
                f"total_time={total_time_ms}ms, word_count={len(final_content.split())}, "
                f"selected=Draft {final_result['selected']}"
            )

            # Step 6: Generate Enhanced GEO Insights
            logger.info(f"[{job_id}] Generating enhanced GEO insights")
            selected_draft_eval = (
                final_result["evaluation"].draft_a
                if final_result["selected"] == "A"
                else final_result["evaluation"].draft_b
            )
            geo_insights = self._generate_geo_insights(
                evaluation=final_result["evaluation"],
                selected_draft=selected_draft_eval,
                commentary=final_result["commentary"],
                research_brief=current_research_brief,
                content=final_content,
                client_name=request.client_name,
                target_question=request.target_question,
            )

            # Generate enhanced schema markup
            enhanced_schema = self._generate_enhanced_schema(
                client_name=request.client_name,
                target_question=request.target_question,
                content=final_content,
            )

            # Generate multi-format exports
            multi_format = self._generate_multi_format_export(
                content=final_content,
                schema_markup=enhanced_schema.article,
            )

            # Build response
            return ContentGenerationResponse(
                job_id=job_id,
                trace_id=trace_id,
                trace_url=f"https://platform.openai.com/traces/{trace_id}",
                detected_language=language_result.detected_language,
                language_code=language_result.language_code,
                dialect=language_result.dialect,
                writing_direction=language_result.writing_direction,
                content=final_content,
                word_count=len(final_content.split()),
                selected_draft=final_result["selected"],
                evaluation_score=final_result["score"],
                evaluation_iterations=final_result["iterations"],
                geo_commentary=final_result["commentary"].to_display_dict(),
                geo_insights=geo_insights.to_display_dict(),
                schema_markup=enhanced_schema.article,  # Keep backward compatibility
                geo_analysis={
                    "statistics_count": final_result["draft"].statistics_count,
                    "citations_count": final_result["draft"].citations_count,
                    "quotations_count": final_result["draft"].quotations_count,
                    "fluency_score": final_result["evaluation"].draft_a.scores.fluency_score
                    if final_result["selected"] == "A"
                    else final_result["evaluation"].draft_b.scores.fluency_score,
                    "eeat_score": final_result["commentary"].eeat_analysis.overall_eeat_score,
                },
                generation_time_ms=total_time_ms,
                models_used={
                    "research": settings.openai_model_writer,
                    "writer_a": settings.openai_model_writer,
                    "writer_b": settings.anthropic_model_writer,
                    "evaluator": settings.openai_model_evaluator,
                },
                timestamp=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"[{job_id}] Workflow error: {e}")
            trace_metadata.completion_status = "failed"
            trace_metadata.error_message = str(e)
            raise

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

    async def _generate_drafts_parallel(
        self,
        client_name: str,
        target_question: str,
        research_brief: ResearchBrief,
        target_word_count: int = 500,
    ) -> tuple[ContentDraft, ContentDraft]:
        """Generate drafts from both writers in parallel."""
        # Run both writers concurrently
        draft_a, draft_b = await asyncio.gather(
            self.writer_a.generate_content(
                client_name=client_name,
                target_question=target_question,
                research_brief=research_brief,
                target_word_count=target_word_count,
            ),
            self.writer_b.generate_content(
                client_name=client_name,
                target_question=target_question,
                research_brief=research_brief,
                target_word_count=target_word_count,
            ),
        )
        return draft_a, draft_b

    async def _evaluation_loop(
        self,
        draft_a: ContentDraft,
        draft_b: ContentDraft,
        target_question: str,
        client_name: str,
        language_code: str,
        research_brief: ResearchBrief,
        target_word_count: int = 500,
        max_iterations: int | None = None,
    ) -> dict:
        """
        Run evaluation loop with potential revisions.

        Args:
            draft_a: First draft
            draft_b: Second draft
            target_question: Target question
            client_name: Client name
            language_code: Language code
            research_brief: Research brief for revisions
            target_word_count: Target word count for revisions
            max_iterations: Maximum iterations (default from settings)

        Returns:
            Dictionary with final content, scores, and commentary
        """
        if max_iterations is None:
            max_iterations = settings.max_iterations

        iteration = 0
        current_draft_a = draft_a
        current_draft_b = draft_b
        evaluation: EvaluationResult | None = None

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Evaluation iteration {iteration}/{max_iterations}")

            # Evaluate both drafts
            evaluation = await self.evaluator.evaluate_drafts(
                draft_a=current_draft_a,
                draft_b=current_draft_b,
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
                logger.info(f"Revision needed for drafts: {evaluation.revision_needed}")

                # Regenerate drafts that need revision
                revision_tasks = []

                if "A" in evaluation.revision_needed:
                    revision_tasks.append(
                        self.writer_a.generate_content(
                            client_name=client_name,
                            target_question=target_question,
                            research_brief=research_brief,
                            target_word_count=target_word_count,
                        )
                    )
                else:
                    revision_tasks.append(asyncio.coroutine(lambda: current_draft_a)())

                if "B" in evaluation.revision_needed:
                    revision_tasks.append(
                        self.writer_b.generate_content(
                            client_name=client_name,
                            target_question=target_question,
                            research_brief=research_brief,
                            target_word_count=target_word_count,
                        )
                    )
                else:
                    revision_tasks.append(asyncio.coroutine(lambda: current_draft_b)())

                results = await asyncio.gather(*revision_tasks)
                current_draft_a = results[0]
                current_draft_b = results[1]

        # Select best draft
        selected_draft: Literal["A", "B"] = evaluation.selected_draft
        selected_content = current_draft_a if selected_draft == "A" else current_draft_b
        alternative_content = current_draft_b if selected_draft == "A" else current_draft_a

        # Generate GEO commentary
        commentary = await self.evaluator.generate_commentary(
            selected_content=selected_content.content,
            alternative_content=alternative_content.content,
            selected_draft=selected_draft,
            evaluation_result=evaluation,
            language_code=language_code,
        )

        return {
            "content": selected_content.content,
            "draft": selected_content,
            "selected": selected_draft,
            "score": evaluation.best_score,
            "draft_a_score": evaluation.draft_a.overall_score,
            "draft_b_score": evaluation.draft_b.overall_score,
            "iterations": iteration,
            "evaluation": evaluation,
            "commentary": commentary,
        }

    def _identify_eeat_gaps(self, eeat_analysis) -> list[str]:
        """
        Identify which E-E-A-T dimensions are weak.

        Args:
            eeat_analysis: EEATAnalysis from commentary

        Returns:
            List of E-E-A-T dimensions that need improvement
        """
        gaps = []

        # Check each dimension for weak signals
        if len(eeat_analysis.experience_signals) < 2:
            gaps.append("experience")
        if len(eeat_analysis.expertise_signals) < 2:
            gaps.append("expertise")
        if len(eeat_analysis.authority_signals) < 2:
            gaps.append("authority")
        if len(eeat_analysis.trust_signals) < 2:
            gaps.append("trust")

        # If overall score is low but no specific gaps, target all dimensions
        if not gaps and eeat_analysis.overall_eeat_score < 6:
            gaps = ["experience", "expertise", "authority", "trust"]

        return gaps

    async def _conduct_eeat_focused_research(
        self,
        client_name: str,
        target_question: str,
        reference_urls: list[str],
        language_code: str,
        eeat_gaps: list[str],
        existing_research: ResearchBrief,
    ) -> ResearchBrief:
        """
        Conduct additional research focused on E-E-A-T gaps.

        Args:
            client_name: Client/entity name
            target_question: Target question
            reference_urls: Reference URLs to search
            language_code: Language code
            eeat_gaps: List of E-E-A-T dimensions needing improvement
            existing_research: Existing research to build upon

        Returns:
            Enhanced ResearchBrief with E-E-A-T focused content
        """
        logger.info(f"Conducting E-E-A-T focused research for gaps: {eeat_gaps}")

        # Build focused research prompt based on gaps
        gap_instructions = []
        if "experience" in eeat_gaps:
            gap_instructions.append(
                "Find real-world examples, case studies, and practical details about the topic"
            )
        if "expertise" in eeat_gaps:
            gap_instructions.append(
                "Find technical details, industry-specific knowledge, and expert analysis"
            )
        if "authority" in eeat_gaps:
            gap_instructions.append(
                "Find citations from official sources, industry leaders, and recognized experts"
            )
        if "trust" in eeat_gaps:
            gap_instructions.append(
                "Find verifiable statistics, source attributions, and transparent information"
            )

        # Conduct focused research with enhanced instructions
        return await self.research_agent.conduct_research(
            client_name=client_name,
            target_question=f"{target_question} [Focus on: {', '.join(gap_instructions)}]",
            reference_urls=reference_urls,
            reference_documents=[],
            language_code=language_code,
        )

    def _merge_research_briefs(
        self,
        original: ResearchBrief,
        additional: ResearchBrief,
    ) -> ResearchBrief:
        """
        Merge two research briefs, combining their content.

        Args:
            original: Original research brief
            additional: Additional research to merge

        Returns:
            Merged ResearchBrief
        """
        # Combine key facts (avoid duplicates)
        combined_facts = list(original.key_facts)
        for fact in additional.key_facts:
            if fact not in combined_facts:
                combined_facts.append(fact)

        # Combine statistics (avoid duplicates based on value)
        combined_stats = list(original.statistics)
        existing_values = {s.value for s in original.statistics}
        for stat in additional.statistics:
            if stat.value not in existing_values:
                combined_stats.append(stat)

        # Combine quotations (avoid duplicates based on quote text)
        combined_quotes = list(original.quotations)
        existing_quotes = {q.quote for q in original.quotations}
        for quote in additional.quotations:
            if quote.quote not in existing_quotes:
                combined_quotes.append(quote)

        # Combine citations (avoid duplicates based on name)
        combined_citations = list(original.citations)
        existing_names = {c.name for c in original.citations}
        for citation in additional.citations:
            if citation.name not in existing_names:
                combined_citations.append(citation)

        # Combine source URLs
        combined_urls = list(set(original.source_urls + additional.source_urls))

        return ResearchBrief(
            client_name=original.client_name,
            target_question=original.target_question,
            language_code=original.language_code,
            key_facts=combined_facts[:15],  # Cap at 15
            statistics=combined_stats[:8],  # Cap at 8
            quotations=combined_quotes[:5],  # Cap at 5
            citations=combined_citations[:10],  # Cap at 10
            source_urls=combined_urls,
            raw_content_summary=f"{original.raw_content_summary}\n\n{additional.raw_content_summary}",
            total_words_harvested=original.total_words_harvested + additional.total_words_harvested,
        )

    def _generate_geo_insights(
        self,
        evaluation: EvaluationResult,
        selected_draft,
        commentary: GEOPerformanceCommentary,
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
    ) -> EnhancedSchemaMarkup:
        """Generate enhanced schema markup with multiple types."""
        # Article schema (always included)
        article_schema = enhanced_schema_generator.generate_article_schema(
            client_name=client_name,
            question=target_question,
            content=content,
        )

        # FAQ schema (if applicable)
        faq_schema = enhanced_schema_generator.generate_faq_schema(content)

        # HowTo schema (if applicable)
        howto_schema = enhanced_schema_generator.generate_howto_schema(
            content=content,
            question=target_question,
        )

        # Organization schema
        org_schema = enhanced_schema_generator.generate_organization_schema(client_name)

        return EnhancedSchemaMarkup(
            article=article_schema,
            faq=faq_schema,
            how_to=howto_schema,
            organization=org_schema,
            breadcrumb=None,  # Could be added based on context
        )

    def _generate_multi_format_export(
        self,
        content: str,
        schema_markup: dict,
    ) -> MultiFormatExport:
        """Generate multi-format exports."""
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

    def _generate_schema_markup(
        self,
        client_name: str,
        target_question: str,
        content: str,
    ) -> dict:
        """Generate Schema.org markup for the content."""
        # Extract first paragraph as description
        paragraphs = content.split("\n\n")
        description = paragraphs[0] if paragraphs else content[:200]

        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": target_question,
            "description": description[:200],
            "about": {
                "@type": "Thing",
                "name": client_name,
            },
            "articleBody": content,
            "datePublished": datetime.utcnow().isoformat(),
            "publisher": {
                "@type": "Organization",
                "name": "GEO Content Platform",
            },
        }


# Create default orchestrator instance
geo_workflow = GEOContentWorkflow()


async def generate_geo_content(
    request: ContentGenerationRequest,
) -> ContentGenerationResponse:
    """
    Convenience function to generate GEO-optimized content.

    Args:
        request: Content generation request

    Returns:
        ContentGenerationResponse with optimized content
    """
    return await geo_workflow.generate_content(request)
