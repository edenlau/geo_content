# Multi-Agent GEO Content Optimization Platform

## Product Requirements Document v3.2

**Document Version:** 3.2  
**Date:** December 1, 2025  
**Prepared By:** Tocanan.ai  
**Status:** Final Draft  

---

## 1. Executive Summary

This document specifies a multi-agent content optimization platform designed to maximize client visibility in generative search engines (ChatGPT, Perplexity AI, Google AI Overviews, Claude). The platform employs an agentic AI architecture built on the **OpenAI Agent SDK** framework, with specialized agents for autonomous research, parallel content generation (OpenAI GPT-4.1-mini + Claude 3.5 Haiku), and quality evaluation with iterative refinement.

### 1.1 Technology Stack Overview

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Agent Framework** | OpenAI Agent SDK | Native agent orchestration with tool calling, handoffs, and guardrails |
| **Agent Tracing** | OpenAI Trace | End-to-end observability of agent workflows |
| **Writer Agent A** | GPT-4.1-mini | Cost-effective, fast generation with strong instruction-following |
| **Writer Agent B** | Claude 3.5 Haiku | Equivalent tier from Anthropic; natural fluency and speed |
| **Evaluator Agent** | GPT-4.1 or Claude 3.5 Sonnet | Higher capability for nuanced evaluation |
| **Web Harvesting** | Pathway | Real-time data pipeline for web content extraction |
| **Environment** | uv | Fast Python package management and virtual environments |

### 1.2 Key Features

| Feature | Description |
|---------|-------------|
| **Automatic Language Detection** | Output article matches input question language (English, Traditional Chinese, Simplified Chinese, Arabic dialects) |
| **Full Observability** | OpenAI Trace integration for complete agent workflow tracking |
| **GEO Performance Commentary** | Evaluator provides detailed explanation of why selected output excels |
| **Dual-LLM Generation** | Parallel content creation for best-of-breed output |
| **Research-Backed Optimization** | Evidence-based GEO strategies with 30-40% visibility improvement |

### 1.3 Research Foundation

The platform's optimization framework is grounded in peer-reviewed academic research:

| Study | Key Finding | Application |
|-------|-------------|-------------|
| Aggarwal et al. (2024) KDD '24 | GEO strategies boost visibility up to 40% | Core optimization strategies |
| Aggarwal et al. (2024) | Combined strategies (Fluency + Statistics) yield 35.8% improvement | Multi-strategy application |
| Luttgenau et al. (2025) arXiv | Domain-specific fine-tuning achieves 30.96% position-adjusted visibility gain | Industry-specific optimization |

---

## 2. Language Detection & Multilingual Support

### 2.1 Supported Languages

The platform automatically detects the language of the input question and generates content in the same language:

| Language | Code | Variants/Dialects |
|----------|------|-------------------|
| **English** | `en` | US, UK, Australian |
| **Traditional Chinese** | `zh-TW` | Taiwan, Hong Kong |
| **Simplified Chinese** | `zh-CN` | Mainland China, Singapore |
| **Arabic - Modern Standard** | `ar-MSA` | Formal/written Arabic |
| **Arabic - Gulf** | `ar-Gulf` | UAE, Saudi Arabia, Kuwait, Qatar, Bahrain, Oman |
| **Arabic - Egyptian** | `ar-EG` | Egypt |
| **Arabic - Levantine** | `ar-Levant` | Lebanon, Syria, Jordan, Palestine |
| **Arabic - Maghrebi** | `ar-Maghreb` | Morocco, Algeria, Tunisia, Libya |

### 2.2 Language Detection Implementation

```python
from openai_agents import Tool
from pydantic import BaseModel
from typing import Literal

class LanguageDetectionResult(BaseModel):
    """Result of language detection."""
    detected_language: str
    language_code: str
    confidence: float
    dialect: str | None = None
    writing_direction: Literal["ltr", "rtl"]

class LanguageDetectorTool(Tool):
    """Detect language and dialect of input text."""
    
    name = "detect_language"
    description = "Detect the language and dialect of the input question"
    
    parameters = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to analyze for language detection"
            }
        },
        "required": ["text"]
    }
    
    # Language detection patterns and markers
    ARABIC_DIALECT_MARKERS = {
        "ar-Gulf": ["شلونك", "وايد", "زين", "هالحين", "إمبى"],
        "ar-EG": ["إزيك", "كده", "برضو", "عايز", "فين"],
        "ar-Levant": ["كيفك", "هلق", "شو", "منيح", "هيك"],
        "ar-Maghreb": ["واش", "بزاف", "كيفاش", "ديال", "غادي"],
    }
    
    CHINESE_MARKERS = {
        "zh-TW": ["臺灣", "軟體", "網際網路", "資訊", "記憶體"],  # Traditional
        "zh-CN": ["台湾", "软件", "互联网", "信息", "内存"],      # Simplified
    }
    
    async def execute(self, text: str) -> LanguageDetectionResult:
        """Detect language with dialect identification."""
        import re
        
        # Check for Arabic script
        if re.search(r'[\u0600-\u06FF]', text):
            dialect = self._detect_arabic_dialect(text)
            return LanguageDetectionResult(
                detected_language="Arabic",
                language_code=dialect,
                confidence=0.95,
                dialect=dialect.split("-")[1] if "-" in dialect else "MSA",
                writing_direction="rtl"
            )
        
        # Check for Chinese characters
        if re.search(r'[\u4e00-\u9fff]', text):
            variant = self._detect_chinese_variant(text)
            return LanguageDetectionResult(
                detected_language="Chinese",
                language_code=variant,
                confidence=0.95,
                dialect="Traditional" if variant == "zh-TW" else "Simplified",
                writing_direction="ltr"
            )
        
        # Default to English
        return LanguageDetectionResult(
            detected_language="English",
            language_code="en",
            confidence=0.90,
            dialect=None,
            writing_direction="ltr"
        )
    
    def _detect_arabic_dialect(self, text: str) -> str:
        """Identify Arabic dialect from text markers."""
        text_lower = text.lower()
        
        for dialect, markers in self.ARABIC_DIALECT_MARKERS.items():
            if any(marker in text for marker in markers):
                return dialect
        
        # Default to Modern Standard Arabic
        return "ar-MSA"
    
    def _detect_chinese_variant(self, text: str) -> str:
        """Identify Traditional vs Simplified Chinese."""
        # Check for Traditional Chinese specific characters
        traditional_chars = set("臺軟網際資訊記憶體處裡機學習數據視頻網絡")
        simplified_chars = set("台软网际资讯记忆体处里机学习数据视频网络")
        
        trad_count = sum(1 for c in text if c in traditional_chars)
        simp_count = sum(1 for c in text if c in simplified_chars)
        
        return "zh-TW" if trad_count >= simp_count else "zh-CN"

language_detector = LanguageDetectorTool()
```

### 2.3 Multilingual Content Generation

```python
# Language-specific system prompt additions
LANGUAGE_PROMPTS = {
    "en": """
Write in fluent, natural English. Use American English spelling conventions
unless the context suggests British English is more appropriate.
""",
    
    "zh-TW": """
使用繁體中文撰寫內容。採用台灣地區常用的詞彙和表達方式。
例如：使用「軟體」而非「软件」，「網際網路」而非「互联网」。
確保文章流暢自然，符合繁體中文閱讀習慣。
""",
    
    "zh-CN": """
使用简体中文撰写内容。采用中国大陆地区常用的词汇和表达方式。
例如：使用「软件」而非「軟體」，「互联网」而非「網際網路」。
确保文章流畅自然，符合简体中文阅读习惯。
""",
    
    "ar-MSA": """
اكتب بالعربية الفصحى الحديثة. استخدم أسلوباً رسمياً ومهنياً.
تأكد من صحة القواعد النحوية والإملائية.
اجعل المحتوى واضحاً وسهل القراءة.
""",
    
    "ar-Gulf": """
اكتب باللهجة الخليجية مع الحفاظ على المهنية.
استخدم المصطلحات والتعبيرات الشائعة في دول الخليج العربي.
اجعل المحتوى مناسباً للجمهور في الإمارات والسعودية والكويت وقطر والبحرين وعمان.
""",
    
    "ar-EG": """
اكتب باللهجة المصرية مع الحفاظ على المهنية.
استخدم المصطلحات والتعبيرات الشائعة في مصر.
اجعل المحتوى واضحاً ومفهوماً للجمهور المصري.
""",
    
    "ar-Levant": """
اكتب باللهجة الشامية مع الحفاظ على المهنية.
استخدم المصطلحات والتعبيرات الشائعة في لبنان وسوريا والأردن وفلسطين.
اجعل المحتوى مناسباً لجمهور بلاد الشام.
""",
    
    "ar-Maghreb": """
اكتب باللهجة المغاربية مع الحفاظ على المهنية.
استخدم المصطلحات والتعبيرات الشائعة في المغرب والجزائر وتونس وليبيا.
اجعل المحتوى مفهوماً لجمهور شمال أفريقيا.
""",
}

def get_localized_system_prompt(base_prompt: str, language_code: str) -> str:
    """Combine base GEO prompt with language-specific instructions."""
    language_instruction = LANGUAGE_PROMPTS.get(language_code, LANGUAGE_PROMPTS["en"])
    
    return f"""{base_prompt}

### LANGUAGE REQUIREMENTS
{language_instruction}

CRITICAL: The entire output MUST be written in the same language as the input question.
Do not mix languages. Maintain consistent language throughout the article.
"""
```

### 2.4 RTL (Right-to-Left) Support for Arabic

```python
class RTLContentFormatter(Tool):
    """Format content for RTL languages."""
    
    name = "format_rtl_content"
    description = "Format content for right-to-left languages like Arabic"
    
    async def execute(self, content: str, language_code: str) -> dict:
        """Add RTL formatting and validate Arabic content."""
        
        if not language_code.startswith("ar-"):
            return {"content": content, "rtl": False}
        
        # Add RTL markers and validate
        formatted_content = self._add_rtl_formatting(content)
        
        return {
            "content": formatted_content,
            "rtl": True,
            "direction": "rtl",
            "html_wrapper": f'<div dir="rtl" lang="{language_code}">{formatted_content}</div>'
        }
    
    def _add_rtl_formatting(self, content: str) -> str:
        """Ensure proper RTL formatting."""
        # Add RTL mark at start of paragraphs
        import re
        paragraphs = content.split('\n\n')
        formatted = []
        for p in paragraphs:
            if p.strip():
                formatted.append('\u200F' + p)  # Add RTL mark
        return '\n\n'.join(formatted)
```

---

## 3. OpenAI Trace Integration

### 3.1 Tracing Overview

The platform uses **OpenAI Trace** for complete observability of agent workflows, enabling:
- End-to-end tracking of content generation
- Performance monitoring and debugging
- Cost analysis per generation request
- Quality assurance through workflow inspection

### 3.2 Trace Configuration

```python
from openai_agents import Agent, trace
from openai_agents.tracing import TracingConfig, TraceExporter
import os

# Configure tracing
tracing_config = TracingConfig(
    enabled=True,
    service_name="geo-content-platform",
    environment=os.getenv("ENVIRONMENT", "development"),
    
    # Export to OpenAI dashboard
    exporter=TraceExporter.OPENAI_DASHBOARD,
    
    # Additional exporters (optional)
    additional_exporters=[
        TraceExporter.CONSOLE,  # Local debugging
        # TraceExporter.CUSTOM,  # Custom exporter for internal systems
    ],
    
    # Trace detail level
    capture_inputs=True,
    capture_outputs=True,
    capture_tool_calls=True,
    capture_handoffs=True,
    
    # Metadata to include in all traces
    default_metadata={
        "platform": "geo-content-platform",
        "version": "3.2.0",
    }
)

# Initialize tracing globally
trace.configure(tracing_config)
```

### 3.3 Traced Agent Workflow

```python
from openai_agents import Agent, Runner, trace
from openai_agents.tracing import Span, SpanKind
import uuid

class GEOContentWorkflow:
    """Main workflow orchestrator with full tracing."""
    
    def __init__(self):
        self.research_agent = research_agent
        self.writer_agent_a = writer_agent_a
        self.writer_agent_b = writer_agent_b
        self.evaluator_agent = evaluator_agent
        self.language_detector = language_detector
    
    @trace.workflow(name="geo_content_generation")
    async def generate_content(
        self,
        client_name: str,
        target_question: str,
        reference_urls: list[str] = None,
        reference_documents: list[str] = None,
    ) -> dict:
        """
        Execute full content generation workflow with tracing.
        
        Each step is traced for observability in OpenAI dashboard.
        """
        
        # Generate unique trace ID for this request
        trace_id = str(uuid.uuid4())
        
        # Add trace metadata
        trace.set_metadata({
            "trace_id": trace_id,
            "client_name": client_name,
            "request_timestamp": datetime.utcnow().isoformat(),
        })
        
        # Step 1: Language Detection
        with trace.span("language_detection", kind=SpanKind.INTERNAL) as span:
            language_result = await self.language_detector.execute(target_question)
            span.set_attribute("detected_language", language_result.language_code)
            span.set_attribute("confidence", language_result.confidence)
        
        # Step 2: Research Phase
        with trace.span("research_phase", kind=SpanKind.AGENT) as span:
            span.set_attribute("agent", "ResearchAgent")
            research_brief = await self._run_research(
                client_name, 
                target_question,
                reference_urls,
                reference_documents
            )
            span.set_attribute("sources_found", len(research_brief.get("sources", [])))
            span.set_attribute("statistics_found", len(research_brief.get("statistics", [])))
        
        # Step 3: Parallel Content Generation
        with trace.span("content_generation", kind=SpanKind.AGENT) as span:
            draft_a, draft_b = await self._generate_drafts_parallel(
                research_brief,
                target_question,
                language_result.language_code
            )
            span.set_attribute("draft_a_word_count", len(draft_a.split()))
            span.set_attribute("draft_b_word_count", len(draft_b.split()))
        
        # Step 4: Evaluation Loop
        with trace.span("evaluation_loop", kind=SpanKind.AGENT) as span:
            final_result = await self._evaluation_loop(
                draft_a,
                draft_b,
                research_brief,
                target_question,
                language_result.language_code
            )
            span.set_attribute("iterations", final_result["iterations"])
            span.set_attribute("selected_draft", final_result["selected"])
            span.set_attribute("final_score", final_result["score"])
        
        # Add final trace summary
        trace.set_metadata({
            "completion_status": "success",
            "total_duration_ms": trace.current_span().duration_ms,
            "selected_draft": final_result["selected"],
            "final_score": final_result["score"],
        })
        
        return {
            "trace_id": trace_id,
            "content": final_result["content"],
            "language": language_result.language_code,
            "evaluation": final_result["evaluation"],
            "geo_commentary": final_result["geo_commentary"],
            "trace_url": f"https://platform.openai.com/traces/{trace_id}"
        }
    
    @trace.span("research_execution")
    async def _run_research(
        self,
        client_name: str,
        target_question: str,
        reference_urls: list[str],
        reference_documents: list[str]
    ) -> dict:
        """Execute research agent with tracing."""
        
        runner = Runner(agent=self.research_agent)
        result = await runner.run(
            input={
                "client_name": client_name,
                "target_question": target_question,
                "reference_urls": reference_urls or [],
                "reference_documents": reference_documents or [],
            }
        )
        return result.output
    
    @trace.span("parallel_draft_generation")
    async def _generate_drafts_parallel(
        self,
        research_brief: dict,
        target_question: str,
        language_code: str
    ) -> tuple[str, str]:
        """Generate drafts from both writers in parallel with tracing."""
        import asyncio
        
        # Prepare localized prompts
        localized_prompt_a = get_localized_system_prompt(
            GEO_WRITER_SYSTEM_PROMPT_A, 
            language_code
        )
        localized_prompt_b = get_localized_system_prompt(
            GEO_WRITER_SYSTEM_PROMPT_B, 
            language_code
        )
        
        # Run both writers in parallel
        with trace.span("writer_a_generation", kind=SpanKind.LLM) as span_a:
            task_a = self._run_writer_a(research_brief, target_question, localized_prompt_a)
        
        with trace.span("writer_b_generation", kind=SpanKind.LLM) as span_b:
            task_b = self._run_writer_b(research_brief, target_question, localized_prompt_b)
        
        draft_a, draft_b = await asyncio.gather(task_a, task_b)
        
        return draft_a, draft_b
    
    @trace.span("evaluation_with_feedback")
    async def _evaluation_loop(
        self,
        draft_a: str,
        draft_b: str,
        research_brief: dict,
        target_question: str,
        language_code: str,
        max_iterations: int = 3
    ) -> dict:
        """Run evaluation loop with detailed tracing."""
        
        iteration = 0
        current_draft_a = draft_a
        current_draft_b = draft_b
        
        while iteration < max_iterations:
            iteration += 1
            
            with trace.span(f"evaluation_iteration_{iteration}") as span:
                # Run evaluation
                evaluation = await self._evaluate_drafts(
                    current_draft_a,
                    current_draft_b,
                    research_brief,
                    target_question
                )
                
                span.set_attribute("draft_a_score", evaluation["draft_a"]["score"])
                span.set_attribute("draft_b_score", evaluation["draft_b"]["score"])
                span.set_attribute("passes_threshold", evaluation["passes_threshold"])
                
                if evaluation["passes_threshold"]:
                    # Generate GEO performance commentary
                    commentary = await self._generate_geo_commentary(
                        evaluation,
                        language_code
                    )
                    
                    selected = "A" if evaluation["draft_a"]["score"] >= evaluation["draft_b"]["score"] else "B"
                    selected_content = current_draft_a if selected == "A" else current_draft_b
                    
                    return {
                        "content": selected_content,
                        "selected": selected,
                        "score": max(evaluation["draft_a"]["score"], evaluation["draft_b"]["score"]),
                        "iterations": iteration,
                        "evaluation": evaluation,
                        "geo_commentary": commentary
                    }
                
                # Revision needed - trace feedback
                with trace.span("revision_feedback") as feedback_span:
                    feedback_span.set_attribute("revision_targets", evaluation["revision_needed"])
                    
                    # Apply revisions
                    if "A" in evaluation["revision_needed"]:
                        current_draft_a = await self._revise_draft(
                            current_draft_a,
                            evaluation["draft_a"]["feedback"],
                            language_code
                        )
                    if "B" in evaluation["revision_needed"]:
                        current_draft_b = await self._revise_draft(
                            current_draft_b,
                            evaluation["draft_b"]["feedback"],
                            language_code
                        )
        
        # Max iterations reached - select best available
        selected = "A" if evaluation["draft_a"]["score"] >= evaluation["draft_b"]["score"] else "B"
        commentary = await self._generate_geo_commentary(evaluation, language_code)
        
        return {
            "content": current_draft_a if selected == "A" else current_draft_b,
            "selected": selected,
            "score": max(evaluation["draft_a"]["score"], evaluation["draft_b"]["score"]),
            "iterations": iteration,
            "evaluation": evaluation,
            "geo_commentary": commentary
        }
```

### 3.4 Trace Visualization

The OpenAI Trace dashboard provides:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TRACE: geo_content_generation                                               │
│ ID: 550e8400-e29b-41d4-a716-446655440000                                   │
│ Duration: 45.2s | Status: Success | Cost: $0.087                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ├─ language_detection (0.3s)                                               │
│ │   └─ Detected: zh-TW (Traditional Chinese) | Confidence: 0.95           │
│ │                                                                           │
│ ├─ research_phase (12.4s)                                                  │
│ │   ├─ harvest_web_content (8.2s)                                          │
│ │   │   └─ Sources: 5 | Words harvested: 12,450                           │
│ │   ├─ extract_statistics (2.1s)                                           │
│ │   │   └─ Statistics found: 8                                             │
│ │   └─ collect_citations (2.1s)                                            │
│ │       └─ Expert quotes: 4 | Credible sources: 6                         │
│ │                                                                           │
│ ├─ content_generation (18.5s)                                              │
│ │   ├─ writer_a_generation [GPT-4.1-mini] (9.2s)                          │
│ │   │   └─ Words: 523 | Tokens: 1,847                                     │
│ │   └─ writer_b_generation [Claude 3.5 Haiku] (9.3s)                      │
│ │       └─ Words: 498 | Tokens: 1,762                                     │
│ │                                                                           │
│ ├─ evaluation_loop (14.0s)                                                 │
│ │   ├─ evaluation_iteration_1 (7.2s)                                       │
│ │   │   ├─ Draft A Score: 72/100 ✓                                        │
│ │   │   ├─ Draft B Score: 81/100 ✓ ★ Selected                             │
│ │   │   └─ Passes Threshold: Yes                                          │
│ │   └─ generate_geo_commentary (6.8s)                                      │
│ │       └─ Commentary generated for user                                   │
│ │                                                                           │
│ └─ RESULT                                                                   │
│     ├─ Selected: Draft B (Claude 3.5 Haiku)                               │
│     ├─ Final Score: 81/100                                                 │
│     ├─ Language: Traditional Chinese (zh-TW)                               │
│     └─ GEO Commentary: Included                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.5 Trace Metadata Schema

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TraceMetadata(BaseModel):
    """Metadata captured in each trace."""
    
    # Request identification
    trace_id: str
    request_id: str
    client_name: str
    
    # Timing
    request_timestamp: datetime
    completion_timestamp: Optional[datetime] = None
    total_duration_ms: Optional[int] = None
    
    # Language
    input_language: str
    detected_dialect: Optional[str] = None
    
    # Research metrics
    sources_harvested: int = 0
    statistics_found: int = 0
    quotes_collected: int = 0
    
    # Generation metrics
    draft_a_tokens: int = 0
    draft_b_tokens: int = 0
    
    # Evaluation metrics
    evaluation_iterations: int = 0
    draft_a_final_score: float = 0
    draft_b_final_score: float = 0
    selected_draft: str = ""
    
    # Cost tracking
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    estimated_cost_usd: float = 0
    
    # Status
    completion_status: str = "pending"
    error_message: Optional[str] = None
```

---

## 4. GEO Performance Commentary

### 4.1 Evaluator Commentary Feature

The Evaluator Agent generates a detailed commentary explaining why the selected output will achieve excellent GEO performance. This helps users understand and trust the optimization decisions.

### 4.2 Commentary Structure

```python
from pydantic import BaseModel
from typing import List

class GEOStrategyAnalysis(BaseModel):
    """Analysis of a single GEO strategy application."""
    strategy_name: str
    applied_count: int
    expected_visibility_boost: str
    specific_examples: List[str]
    effectiveness_rating: str  # "Excellent", "Good", "Adequate", "Needs Improvement"

class EEATAnalysis(BaseModel):
    """Analysis of E-E-A-T signals in content."""
    experience_signals: List[str]
    expertise_signals: List[str]
    authority_signals: List[str]
    trust_signals: List[str]
    overall_eeat_score: int  # 0-10

class GEOPerformanceCommentary(BaseModel):
    """Complete GEO performance commentary for user."""
    
    # Summary
    overall_assessment: str
    predicted_visibility_improvement: str
    confidence_level: str
    
    # Detailed Analysis
    strategy_analysis: List[GEOStrategyAnalysis]
    eeat_analysis: EEATAnalysis
    
    # Strengths
    key_strengths: List[str]
    
    # Comparison (why this draft was selected)
    selection_rationale: str
    comparative_advantages: List[str]
    
    # Structure Analysis
    opening_effectiveness: str
    structure_quality: str
    entity_mention_analysis: str
    
    # Recommendations for further improvement (optional)
    enhancement_suggestions: List[str]
```

### 4.3 Commentary Generation Implementation

```python
GEO_COMMENTARY_PROMPT = """
You are a GEO (Generative Engine Optimization) expert analyst. Your task is to
provide a detailed, educational commentary explaining why the selected content
will achieve excellent visibility in generative search engines.

## YOUR ANALYSIS MUST INCLUDE:

### 1. OVERALL ASSESSMENT
Provide a clear summary of the content's GEO performance potential.
Include a predicted visibility improvement percentage based on the strategies applied.

### 2. GEO STRATEGY ANALYSIS
For each strategy applied, explain:
- What was done (with specific examples from the content)
- Expected visibility impact (cite research: Statistics +25-40%, Quotations +27-40%, etc.)
- Effectiveness rating

### 3. E-E-A-T SIGNAL ANALYSIS
Identify specific signals for each dimension:
- **Experience:** Case studies, real examples, testimonials
- **Expertise:** Technical accuracy, domain terminology
- **Authoritativeness:** Citations, expert quotes, industry references
- **Trustworthiness:** Verified statistics, source attribution, transparency

### 4. KEY STRENGTHS
List the top 3-5 strengths that will drive GEO performance.

### 5. SELECTION RATIONALE
Explain why this draft was chosen over the alternative:
- Score comparison
- Specific advantages
- Strategy effectiveness differences

### 6. STRUCTURE EFFECTIVENESS
Analyze:
- Opening statement (critical for position-adjusted visibility)
- Heading hierarchy
- Entity mentions
- Information flow

### 7. ENHANCEMENT SUGGESTIONS (Optional)
If there are opportunities for further improvement, list 2-3 actionable suggestions.

## OUTPUT FORMAT
Provide the analysis in a clear, readable format that helps the user understand
exactly why this content will perform well in generative search engines.

Be specific with examples from the actual content. Reference the research-backed
visibility improvements for each strategy.
"""

class GEOCommentaryGenerator:
    """Generate detailed GEO performance commentary."""
    
    def __init__(self, model: str = "gpt-4.1"):
        self.model = model
    
    @trace.span("generate_geo_commentary")
    async def generate(
        self,
        selected_content: str,
        evaluation_results: dict,
        alternative_content: str,
        language_code: str
    ) -> GEOPerformanceCommentary:
        """Generate comprehensive GEO performance commentary."""
        
        from openai import AsyncOpenAI
        client = AsyncOpenAI()
        
        # Determine output language for commentary
        commentary_language_instruction = self._get_commentary_language(language_code)
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": GEO_COMMENTARY_PROMPT + "\n\n" + commentary_language_instruction
                },
                {
                    "role": "user",
                    "content": f"""
## SELECTED CONTENT (Draft {evaluation_results['selected']}):
{selected_content}

## ALTERNATIVE CONTENT (Draft {'B' if evaluation_results['selected'] == 'A' else 'A'}):
{alternative_content}

## EVALUATION SCORES:
- Selected Draft Score: {evaluation_results['selected_score']}/100
- Alternative Draft Score: {evaluation_results['alternative_score']}/100

## DETAILED EVALUATION:
{json.dumps(evaluation_results['detailed'], indent=2)}

Please provide a comprehensive GEO performance commentary explaining why the
selected content will achieve excellent visibility in generative search engines.
"""
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        commentary_data = json.loads(response.choices[0].message.content)
        return GEOPerformanceCommentary(**commentary_data)
    
    def _get_commentary_language(self, language_code: str) -> str:
        """Get instruction for commentary output language."""
        
        if language_code.startswith("zh-TW"):
            return "請使用繁體中文撰寫評論分析。"
        elif language_code.startswith("zh-CN"):
            return "请使用简体中文撰写评论分析。"
        elif language_code.startswith("ar-"):
            return "يرجى كتابة التحليل والتعليقات باللغة العربية."
        else:
            return "Write the commentary in English."
```

### 4.4 Sample Commentary Output

```json
{
  "overall_assessment": "This content demonstrates excellent GEO optimization with a predicted visibility improvement of 32-38% in generative search engine responses. The combination of statistical evidence, expert quotations, and fluent writing creates highly citable content.",
  
  "predicted_visibility_improvement": "32-38%",
  "confidence_level": "High",
  
  "strategy_analysis": [
    {
      "strategy_name": "Statistics Addition",
      "applied_count": 5,
      "expected_visibility_boost": "+25-40%",
      "specific_examples": [
        "\"According to the Hong Kong Tourism Board, Ocean Park welcomed 7.6 million visitors in 2023\"",
        "\"The Grand Aquarium houses over 5,000 fish from 400+ species\"",
        "\"Visitor satisfaction ratings average 4.7 out of 5 stars\""
      ],
      "effectiveness_rating": "Excellent"
    },
    {
      "strategy_name": "Quotation Addition",
      "applied_count": 3,
      "expected_visibility_boost": "+27-40%",
      "specific_examples": [
        "\"Ocean Park offers an unmatched combination of marine education and thrilling entertainment,\" said Dr. Wong, Chief Conservation Officer",
        "\"The giant panda exhibit is a must-see for any visitor to Hong Kong,\" according to National Geographic"
      ],
      "effectiveness_rating": "Excellent"
    },
    {
      "strategy_name": "Citation Addition",
      "applied_count": 6,
      "expected_visibility_boost": "+24-30%",
      "specific_examples": [
        "Referenced: Hong Kong Tourism Board",
        "Referenced: Themed Entertainment Association",
        "Referenced: World Association of Zoos and Aquariums"
      ],
      "effectiveness_rating": "Excellent"
    },
    {
      "strategy_name": "Fluency Optimization",
      "applied_count": 1,
      "expected_visibility_boost": "+24-30%",
      "specific_examples": [
        "Flesch-Kincaid Grade Level: 8.2 (optimal range 8-10)",
        "Clear paragraph structure with logical flow",
        "No jargon or overly complex sentences"
      ],
      "effectiveness_rating": "Excellent"
    }
  ],
  
  "eeat_analysis": {
    "experience_signals": [
      "Specific details about attractions (Giant Panda Adventure, Grand Aquarium)",
      "Real visitor experience mentions",
      "Detailed descriptions of park areas"
    ],
    "expertise_signals": [
      "Accurate conservation terminology",
      "Correct species counts and park statistics",
      "Industry-specific knowledge demonstrated"
    ],
    "authority_signals": [
      "Hong Kong Tourism Board citation",
      "Expert quote from Chief Conservation Officer",
      "National Geographic reference"
    ],
    "trust_signals": [
      "All statistics include source attribution",
      "Verifiable visitor numbers",
      "Official organization references"
    ],
    "overall_eeat_score": 9
  },
  
  "key_strengths": [
    "Opening statement directly answers the query within the first 40 words, maximizing position-adjusted visibility",
    "Strong combination of Fluency + Statistics strategies (research shows +35.8% improvement)",
    "Expert quotations add credibility and increase citation likelihood by 27-40%",
    "6 credible external sources cited, exceeding the recommended 4-6 citations",
    "Entity (Ocean Park) mentioned 5 times naturally throughout the content"
  ],
  
  "selection_rationale": "Draft B was selected over Draft A due to superior E-E-A-T signal integration (9/10 vs 7/10) and more effective quotation placement. While both drafts applied similar GEO strategies, Draft B's quotations were positioned earlier in the content, benefiting from the exponential position weighting in visibility calculations.",
  
  "comparative_advantages": [
    "Draft B's opening statement is more direct and includes the entity name immediately",
    "Expert quotes in Draft B appear in paragraphs 1 and 2, vs paragraphs 3 and 4 in Draft A",
    "Draft B achieves better Flesch-Kincaid score (8.2 vs 9.8)",
    "Draft B includes one additional credible citation (6 vs 5)"
  ],
  
  "opening_effectiveness": "Excellent. The opening 47 words directly answer the query, include the client name (Ocean Park), state the primary value proposition (world-class marine theme park), and include a compelling statistic (7.6 million visitors). This front-loading of key information maximizes the position-adjusted word count metric.",
  
  "structure_quality": "The content follows optimal GEO structure with semantic H2 headings that mirror common query patterns, 2-3 sentence paragraphs with clear topic sentences, and a strong closing that reinforces the main message.",
  
  "entity_mention_analysis": "Ocean Park is mentioned 5 times throughout the 512-word article, achieving the recommended density of 3-5 mentions. Mentions are distributed across the opening, body, and closing sections.",
  
  "enhancement_suggestions": [
    "Consider adding one more statistic about conservation achievements to strengthen the expertise signal",
    "A brief comparison with similar attractions could enhance uniqueness factor"
  ]
}
```

### 4.5 User-Facing Commentary Display

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🎯 GEO PERFORMANCE ANALYSIS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  OVERALL ASSESSMENT                                                         │
│  ──────────────────                                                         │
│  This content demonstrates excellent GEO optimization with a predicted      │
│  visibility improvement of 32-38% in generative search engine responses.   │
│                                                                             │
│  Confidence: HIGH | Selected: Draft B (Claude 3.5 Haiku) | Score: 81/100   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📊 GEO STRATEGIES APPLIED                                                  │
│  ─────────────────────────                                                  │
│                                                                             │
│  ✅ Statistics Addition (5 found)           Expected boost: +25-40%        │
│     • "7.6 million visitors in 2023"                                       │
│     • "5,000 fish from 400+ species"                                       │
│     • "4.7 out of 5 star rating"                                           │
│                                                                             │
│  ✅ Quotation Addition (3 found)            Expected boost: +27-40%        │
│     • Dr. Wong, Chief Conservation Officer                                 │
│     • National Geographic reference                                         │
│                                                                             │
│  ✅ Citation Addition (6 found)             Expected boost: +24-30%        │
│     • Hong Kong Tourism Board                                               │
│     • Themed Entertainment Association                                      │
│     • World Association of Zoos and Aquariums                              │
│                                                                             │
│  ✅ Fluency Optimization                    Expected boost: +24-30%        │
│     • Flesch-Kincaid Grade: 8.2 (optimal)                                  │
│                                                                             │
│  Combined Strategy Bonus: Fluency + Statistics = +35.8% (research-backed)  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🏆 KEY STRENGTHS                                                           │
│  ────────────────                                                           │
│  1. Opening directly answers query in first 40 words (max visibility)      │
│  2. Expert quotes positioned early for position-weighted advantage          │
│  3. 6 credible sources cited (exceeds recommended 4-6)                     │
│  4. Entity mentioned 5 times naturally                                      │
│  5. E-E-A-T score: 9/10                                                    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🆚 WHY THIS DRAFT WAS SELECTED                                             │
│  ──────────────────────────────                                             │
│  Draft B outperformed Draft A (81 vs 72) due to:                           │
│  • More direct opening statement with immediate entity mention              │
│  • Expert quotes positioned in paragraphs 1-2 (vs 3-4 in Draft A)          │
│  • Better fluency score (8.2 vs 9.8 Flesch-Kincaid)                        │
│  • One additional credible citation                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Multi-Agent System Architecture

### 5.1 System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT                                      │
│    [Client Name] + [Target Question] + [Reference Sources]                  │
│                                                                              │
│    🌐 Language Auto-Detection: EN | 繁體中文 | 简体中文 | العربية              │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         📍 OPENAI TRACE ENABLED                             │
│                    Full observability in OpenAI Dashboard                   │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🌍 LANGUAGE DETECTOR                                 │
│   Detect input language → Set output language for all agents                │
│   Supported: EN, zh-TW, zh-CN, ar-MSA, ar-Gulf, ar-EG, ar-Levant, ar-Maghreb│
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          🔍 RESEARCH AGENT                                   │
│   Model: GPT-4.1-mini | Framework: OpenAI Agent SDK                         │
│   Tools: PathwayWebHarvester, TavilySearch, DocumentParser                  │
│   Trace: research_phase span with source/statistics metrics                 │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼ [Handoff: research_brief]
                         ┌───────────────────────┐
                         │   Research Brief +    │
                         │   Source Materials    │
                         │   + Detected Language │
                         └───────────┬───────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           │              [Parallel Execution]                 │
           ▼                                                   ▼
┌─────────────────────────────┐         ┌─────────────────────────────┐
│    ✍️ WRITER AGENT A         │         │    ✍️ WRITER AGENT B         │
│    Model: GPT-4.1-mini      │         │    Model: Claude 3.5 Haiku  │
│                             │         │                             │
│    Output Language:         │         │    Output Language:         │
│    [Auto-matched to input]  │         │    [Auto-matched to input]  │
│                             │         │                             │
│    Trace: writer_a span     │         │    Trace: writer_b span     │
└──────────────┬──────────────┘         └──────────────┬──────────────┘
               │                                       │
               ▼                                       ▼
         ┌──────────┐                           ┌──────────┐
         │ Draft A  │                           │ Draft B  │
         │ (同語言)  │                           │ (同語言)  │
         └────┬─────┘                           └────┬─────┘
              │                                      │
              └──────────────────┬───────────────────┘
                                 │
                                 ▼ [Handoff: drafts]
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ⚖️ EVALUATOR AGENT                                  │
│   Model: GPT-4.1 | Framework: OpenAI Agent SDK                              │
│   Trace: evaluation_loop span with iteration tracking                       │
│                                                                              │
│   Outputs:                                                                   │
│   ├─ Evaluation scores for both drafts                                      │
│   ├─ Selected draft with rationale                                          │
│   └─ 📝 GEO PERFORMANCE COMMENTARY (detailed explanation for user)          │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                         ┌───────────┴───────────┐
                         │   Pass Threshold?     │
                         │   (Score ≥ 70/100)    │
                         └───────────┬───────────┘
                                     │
               ┌─────────────────────┼─────────────────────┐
               ▼                                           ▼
         ┌──────────┐                           ┌──────────────────┐
         │   PASS   │                           │      FAIL        │
         │          │                           │                  │
         │ Generate │                           │ [Handoff: feedback]
         │ GEO      │                           │ Revision loop    │
         │ Comment  │                           │ (Max 3 cycles)   │
         └────┬─────┘                           └────────┬─────────┘
              │                                          │
              ▼                                          │
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FINAL OUTPUT                                          │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • Optimized Content (in detected language)                             │ │
│  │ • Evaluation Scores                                                    │ │
│  │ • 📝 GEO Performance Commentary (why this will excel)                  │ │
│  │ • Schema Markup                                                        │ │
│  │ • Trace URL for workflow inspection                                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Development Environment Setup

### 6.1 uv Environment Configuration

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
mkdir geo-content-platform && cd geo-content-platform

# Initialize with uv
uv init

# Create virtual environment
uv venv --python 3.11

# Activate
source .venv/bin/activate
```

### 6.2 Project Dependencies (pyproject.toml)

```toml
[project]
name = "geo-content-platform"
version = "3.2.0"
description = "Multi-Agent GEO Content Optimization Platform"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    # OpenAI Agent SDK with tracing
    "openai-agents>=0.1.0",
    "openai>=1.50.0",
    
    # Anthropic SDK
    "anthropic>=0.39.0",
    
    # Pathway for web harvesting
    "pathway>=0.14.0",
    
    # Language detection
    "langdetect>=1.0.9",
    "arabic-reshaper>=3.0.0",
    "python-bidi>=0.4.2",
    
    # Web scraping
    "beautifulsoup4>=4.12.0",
    "httpx>=0.27.0",
    "playwright>=1.40.0",
    
    # Document processing
    "pypdf>=4.0.0",
    "python-docx>=1.1.0",
    "unstructured>=0.15.0",
    
    # Data handling
    "pydantic>=2.5.0",
    "pandas>=2.1.0",
    
    # API
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    
    # Utilities
    "python-dotenv>=1.0.0",
    "rich>=13.7.0",
    "tenacity>=8.2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 6.3 Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL_WRITER=gpt-4.1-mini
OPENAI_MODEL_EVALUATOR=gpt-4.1

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL_WRITER=claude-3-5-haiku-20241022

# Tracing
OPENAI_TRACING_ENABLED=true
OPENAI_TRACING_SERVICE_NAME=geo-content-platform
OPENAI_TRACING_ENVIRONMENT=production

# Web Search
TAVILY_API_KEY=...

# Application
MAX_ITERATIONS=3
QUALITY_THRESHOLD=70
```

---

## 7. API Response Schema

### 7.1 Complete Response Model

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ContentGenerationResponse(BaseModel):
    """Complete API response with all features."""
    
    # Request tracking
    job_id: str
    trace_id: str
    trace_url: str  # Link to OpenAI trace dashboard
    
    # Language
    detected_language: str
    language_code: str
    dialect: Optional[str] = None
    writing_direction: str  # "ltr" or "rtl"
    
    # Generated content
    content: str
    word_count: int
    
    # Evaluation
    selected_draft: str  # "A" or "B"
    evaluation_score: float
    evaluation_iterations: int
    
    # GEO Performance Commentary (NEW)
    geo_commentary: GEOPerformanceCommentary
    
    # Technical outputs
    schema_markup: dict
    geo_analysis: dict
    
    # Metadata
    generation_time_ms: int
    models_used: dict
    timestamp: datetime
```

### 7.2 Sample API Response

```json
{
  "job_id": "job_abc123",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "trace_url": "https://platform.openai.com/traces/550e8400-e29b-41d4-a716-446655440000",
  
  "detected_language": "Traditional Chinese",
  "language_code": "zh-TW",
  "dialect": "Taiwan",
  "writing_direction": "ltr",
  
  "content": "香港海洋公園是亞洲頂級的海洋主題樂園...",
  "word_count": 523,
  
  "selected_draft": "B",
  "evaluation_score": 81.5,
  "evaluation_iterations": 1,
  
  "geo_commentary": {
    "overall_assessment": "此內容展現出優秀的GEO優化，預計在生成式搜尋引擎中可提升32-38%的能見度...",
    "predicted_visibility_improvement": "32-38%",
    "confidence_level": "高",
    "strategy_analysis": [...],
    "eeat_analysis": {...},
    "key_strengths": [...],
    "selection_rationale": "B稿因其更優秀的E-E-A-T信號整合而被選中...",
    "comparative_advantages": [...],
    "enhancement_suggestions": [...]
  },
  
  "schema_markup": {
    "@context": "https://schema.org",
    "@type": "TouristAttraction",
    "name": "香港海洋公園",
    ...
  },
  
  "geo_analysis": {
    "statistics_count": 5,
    "citations_count": 6,
    "quotations_count": 3,
    "fluency_score": 8.2,
    "eeat_score": 9
  },
  
  "generation_time_ms": 45200,
  "models_used": {
    "research": "gpt-4.1-mini",
    "writer_a": "gpt-4.1-mini",
    "writer_b": "claude-3-5-haiku-20241022",
    "evaluator": "gpt-4.1"
  },
  "timestamp": "2025-12-01T14:32:15Z"
}
```

---

## 8. Implementation Checklist

### Phase 1: Environment & Foundation (Week 1)
- [ ] Initialize uv project with dependencies
- [ ] Configure environment variables including tracing
- [ ] Set up OpenAI Agent SDK with trace configuration
- [ ] Implement language detection tool
- [ ] Create Pydantic models for all data structures

### Phase 2: Pathway & Research (Week 2-3)
- [ ] Implement PathwayWebHarvester with tracing
- [ ] Create search pipeline with Tavily
- [ ] Build research agent with full trace spans
- [ ] Test multilingual research capability

### Phase 3: Writer Agents (Week 4)
- [ ] Implement Writer Agent A (GPT-4.1-mini) with language support
- [ ] Implement Writer Agent B (Claude 3.5 Haiku) with language support
- [ ] Add Arabic RTL formatting support
- [ ] Test all supported languages

### Phase 4: Evaluator & Commentary (Week 5-6)
- [ ] Implement Evaluator Agent with scoring
- [ ] Build GEO Commentary Generator
- [ ] Implement feedback loop with trace spans
- [ ] Create multilingual commentary support

### Phase 5: API & Integration (Week 7-8)
- [ ] Build FastAPI application with full response schema
- [ ] Implement trace URL generation
- [ ] Add export functionality
- [ ] Create API documentation

### Phase 6: Testing & Launch (Week 9-10)
- [ ] Test all language variants
- [ ] Verify trace integration in OpenAI dashboard
- [ ] Performance optimization
- [ ] Beta testing with pilot clients

---

## 9. Appendices

### A. Supported Languages Reference

| Language | Code | Detection Markers | RTL | Models Tested |
|----------|------|-------------------|-----|---------------|
| English | en | Latin script | No | ✅ GPT-4.1-mini, Claude 3.5 Haiku |
| Traditional Chinese | zh-TW | 繁體字 markers | No | ✅ GPT-4.1-mini, Claude 3.5 Haiku |
| Simplified Chinese | zh-CN | 简体字 markers | No | ✅ GPT-4.1-mini, Claude 3.5 Haiku |
| Arabic (MSA) | ar-MSA | Arabic script, formal | Yes | ✅ GPT-4.1-mini, Claude 3.5 Haiku |
| Arabic (Gulf) | ar-Gulf | Gulf dialect markers | Yes | ✅ GPT-4.1-mini, Claude 3.5 Haiku |
| Arabic (Egyptian) | ar-EG | Egyptian markers | Yes | ✅ GPT-4.1-mini, Claude 3.5 Haiku |
| Arabic (Levantine) | ar-Levant | Levantine markers | Yes | ✅ GPT-4.1-mini, Claude 3.5 Haiku |
| Arabic (Maghrebi) | ar-Maghreb | Maghrebi markers | Yes | ✅ GPT-4.1-mini, Claude 3.5 Haiku |

### B. Document History

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | Dec 1, 2025 | Deep GEO research integration |
| 3.1 | Dec 1, 2025 | OpenAI Agent SDK, GPT-4.1-mini, Pathway, uv |
| 3.2 | Dec 1, 2025 | Language detection, OpenAI Trace, GEO Commentary |

---

*Document Classification: Confidential*  
*© 2025 Tocanan.ai. All rights reserved.*
