"""
GEO Performance Commentary prompts.

Generates detailed explanations of why content will perform well in generative search engines.
"""

GEO_COMMENTARY_SYSTEM_PROMPT = """
You are a GEO (Generative Engine Optimization) expert analyst. Your task is to
provide a detailed, educational commentary explaining why the selected content
will achieve excellent visibility in generative search engines.

## YOUR ANALYSIS MUST INCLUDE:

### 1. OVERALL ASSESSMENT
Provide a clear summary of the content's GEO performance potential.
Include a predicted visibility improvement percentage based on the strategies applied.
Reference the research basis for your predictions.

### 2. GEO STRATEGY ANALYSIS
For each strategy applied, explain:
- What was done (with specific examples from the content)
- Expected visibility impact (cite research: Statistics +25-40%, Quotations +27-40%, etc.)
- Effectiveness rating (Excellent/Good/Adequate/Needs Improvement)

### 3. E-E-A-T SIGNAL ANALYSIS
Identify specific signals for each dimension:
- **Experience:** Case studies, real examples, testimonials
- **Expertise:** Technical accuracy, domain terminology
- **Authoritativeness:** Citations, expert quotes, industry references
- **Trustworthiness:** Verified statistics, source attribution, transparency

IMPORTANT: The overall_eeat_score MUST be an integer from 0 to 10 (NOT 0-100).
Use this scale: 0-2=Poor, 3-4=Below Average, 5-6=Average, 7-8=Good, 9-10=Excellent.

### 4. KEY STRENGTHS
List the top 3-5 strengths that will drive GEO performance.
Be specific with examples from the content.

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

## OUTPUT REQUIREMENTS

- Provide the analysis in a clear, readable format
- Use specific examples from the actual content
- Reference research-backed visibility improvements for each strategy
- Be educational - help the user understand GEO optimization
- Match the language of the content being analyzed
"""


def get_commentary_prompt(
    selected_content: str,
    alternative_content: str,
    selected_draft: str,
    selected_score: float,
    alternative_score: float,
    evaluation_details: dict,
    language_code: str,
) -> str:
    """
    Generate the prompt for GEO performance commentary.

    Args:
        selected_content: Content of the selected draft
        alternative_content: Content of the alternative draft
        selected_draft: "A" or "B"
        selected_score: Score of selected draft
        alternative_score: Score of alternative draft
        evaluation_details: Detailed evaluation data
        language_code: Language code for output

    Returns:
        Formatted commentary prompt
    """
    language_instruction = _get_commentary_language_instruction(language_code)

    return f"""
## SELECTED CONTENT (Draft {selected_draft}):

{selected_content}

---

## ALTERNATIVE CONTENT (Draft {"B" if selected_draft == "A" else "A"}):

{alternative_content}

---

## EVALUATION SCORES:
- Selected Draft ({selected_draft}) Score: {selected_score}/100
- Alternative Draft Score: {alternative_score}/100
- Score Difference: {selected_score - alternative_score:.1f}

## DETAILED EVALUATION DATA:
{_format_evaluation_details(evaluation_details)}

---

{language_instruction}

## YOUR TASK

Provide a comprehensive GEO performance commentary explaining why the selected
content will achieve excellent visibility in generative search engines.

Output your commentary as JSON with this structure:

```json
{{
  "overall_assessment": "Summary of GEO performance potential",
  "predicted_visibility_improvement": "X-Y%",
  "confidence_level": "High/Medium/Low",

  "strategy_analysis": [
    {{
      "strategy_name": "Statistics Addition",
      "applied_count": 0,
      "expected_visibility_boost": "+25-40%",
      "specific_examples": ["example1", "example2"],
      "effectiveness_rating": "Excellent/Good/Adequate/Needs Improvement",
      "research_reference": "Aggarwal et al. (2024)"
    }}
  ],

  "eeat_analysis": {{
    "experience_signals": ["signal1", "signal2"],
    "expertise_signals": ["signal1", "signal2"],
    "authority_signals": ["signal1", "signal2"],
    "trust_signals": ["signal1", "signal2"],
    "overall_eeat_score": 7,
    "eeat_summary": "Summary of E-E-A-T performance"
  }},

  "structure_analysis": {{
    "opening_effectiveness": "Assessment",
    "opening_word_count": 0,
    "answers_query_directly": true/false,
    "structure_quality": "Assessment",
    "entity_mention_analysis": "Assessment",
    "entity_mention_count": 0
  }},

  "key_strengths": ["strength1", "strength2", "strength3"],

  "comparison": {{
    "selected_draft": "A/B",
    "selected_score": 0,
    "alternative_score": 0,
    "score_difference": 0,
    "selection_rationale": "Explanation",
    "comparative_advantages": ["advantage1", "advantage2"]
  }},

  "enhancement_suggestions": ["suggestion1", "suggestion2"]
}}
```
"""


def _get_commentary_language_instruction(language_code: str) -> str:
    """Get language instruction for commentary output."""
    instructions = {
        "zh-TW": "請使用繁體中文撰寫評論分析。",
        "zh-CN": "请使用简体中文撰写评论分析。",
        "ar-MSA": "يرجى كتابة التحليل والتعليقات باللغة العربية الفصحى.",
        "ar-Gulf": "يرجى كتابة التحليل والتعليقات باللهجة الخليجية.",
        "ar-EG": "يرجى كتابة التحليل والتعليقات باللهجة المصرية.",
        "ar-Levant": "يرجى كتابة التحليل والتعليقات باللهجة الشامية.",
        "ar-Maghreb": "يرجى كتابة التحليل والتعليقات باللهجة المغاربية.",
    }
    return instructions.get(language_code, "Write the commentary in English.")


def _format_evaluation_details(details: dict) -> str:
    """Format evaluation details for the prompt."""
    if not details:
        return "No detailed evaluation data available."

    lines = []

    if "draft_a" in details:
        lines.append("### Draft A Evaluation:")
        da = details["draft_a"]
        if "scores" in da:
            lines.append(f"- Statistics: {da['scores'].get('statistics_score', 'N/A')}")
            lines.append(f"- Citations: {da['scores'].get('citations_score', 'N/A')}")
            lines.append(f"- Quotations: {da['scores'].get('quotations_score', 'N/A')}")
            lines.append(f"- Fluency: {da['scores'].get('fluency_score', 'N/A')}")
        lines.append(f"- Overall: {da.get('overall_score', 'N/A')}")

    if "draft_b" in details:
        lines.append("\n### Draft B Evaluation:")
        db = details["draft_b"]
        if "scores" in db:
            lines.append(f"- Statistics: {db['scores'].get('statistics_score', 'N/A')}")
            lines.append(f"- Citations: {db['scores'].get('citations_score', 'N/A')}")
            lines.append(f"- Quotations: {db['scores'].get('quotations_score', 'N/A')}")
            lines.append(f"- Fluency: {db['scores'].get('fluency_score', 'N/A')}")
        lines.append(f"- Overall: {db.get('overall_score', 'N/A')}")

    return "\n".join(lines)
