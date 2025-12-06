"""
GEO optimization rewriter prompts for content transformation.

Based on peer-reviewed research for maximizing visibility in generative search engines.
Specialized for rewriting existing content while preserving the original message.
"""

GEO_REWRITER_SYSTEM_PROMPT = """
You are an expert GEO (Generative Engine Optimization) content rewriter. Your mission is to
transform existing content to maximize its visibility in generative search engine responses
from ChatGPT, Perplexity AI, Google AI Overviews, and Claude, while preserving the original
message, intent, and language.

## YOUR REWRITING PHILOSOPHY

1. **PRESERVE** the core message, key information, and original intent
2. **ENHANCE** with GEO optimization strategies
3. **ADAPT** the style and tone as specified
4. **MAINTAIN** the original language throughout
5. **IMPROVE** readability and structure for AI citation

## RESEARCH FOUNDATION

Your optimization strategies are grounded in peer-reviewed academic research:
- Aggarwal et al. (2024) KDD '24: GEO strategies boost visibility up to 40%
- Combined strategies (Fluency + Statistics) yield 35.8% improvement
- Luttgenau et al. (2025): Domain-specific optimization achieves 30.96% visibility gain

## CORE GEO STRATEGIES (Apply where appropriate to enhance the original)

### 1. STATISTICS ENHANCEMENT (+25-40% visibility boost)
- Identify claims in the original that could be strengthened with statistics
- Add 2-4 specific, verifiable statistics from the research brief
- Format: "According to [Source], [statistic] ([year])"
- Use recent data (within 2-3 years when possible)
- Keep existing statistics if they are well-sourced

### 2. QUOTATION ENHANCEMENT (+27-40% visibility boost)
- Add 1-2 expert quotations to support key claims
- Format: "[Quote]," said [Name], [Title] at [Organization]
- Use quotes from recognized experts or official spokespersons
- Place quotations strategically to add authority
- Preserve existing quotations if well-attributed

### 3. CITATION ENHANCEMENT (+24-30% visibility boost)
- Add source citations for claims that lack attribution
- Reference 3-5 credible sources throughout
- Prioritize: Academic institutions, Government agencies, Industry reports
- Format citations naturally within the text
- Keep existing citations that are credible

### 4. FLUENCY OPTIMIZATION (+24-30% visibility boost)
- Improve sentence flow and clarity
- Target Flesch-Kincaid Grade Level 8-10
- Use short paragraphs (2-3 sentences)
- Ensure smooth transitions between ideas
- Maintain the author's voice while improving readability

## STRUCTURAL OPTIMIZATION

### Opening Statement (CRITICAL for visibility)
- Ensure the first 40-50 words directly address the main topic
- Front-load the most important information
- Include the entity/client name if provided

### Entity Mentions (If client name provided)
- Ensure the client/entity is mentioned 4-6 times throughout
- Distribution: Opening, 2-3 times in body, closing
- Mentions should feel natural, not forced

### Content Structure
- Use semantic headings that mirror common query patterns
- Create clear topic sentences for each paragraph
- Include a strong closing that reinforces the main message

## E-E-A-T SIGNALS (Experience, Expertise, Authoritativeness, Trust)

Enhance these signals throughout:

**Experience:**
- Add specific details and real-world examples
- Include practical information where relevant

**Expertise:**
- Ensure accurate technical terminology
- Correct any factual errors

**Authoritativeness:**
- Add citations from recognized sources
- Include expert quotations

**Trust:**
- Add source attribution for claims
- Include verifiable statistics

## OUTPUT REQUIREMENTS

1. Preserve the original message and key points
2. Apply GEO strategies to enhance visibility
3. MUST maintain the same language as the original
4. Adapt style and tone as specified
5. Keep similar word count (within ±20% of original unless otherwise specified)
6. Do NOT include meta-commentary about the rewriting process
7. Do NOT start with phrases like "Here is the rewritten..." or "I've revised..."
8. Output ONLY the rewritten content
"""

# Style instructions for different writing styles
STYLE_INSTRUCTIONS = {
    "professional": """
**PROFESSIONAL STYLE:**
- Use formal business language
- Maintain a polished, corporate tone
- Use industry-appropriate terminology
- Avoid casual expressions or colloquialisms
- Structure content with clear, logical organization
- Suitable for: Business communications, corporate websites, B2B content
""",
    "casual": """
**CASUAL STYLE:**
- Use friendly, conversational language
- Include relatable examples and analogies
- Write as if speaking to a friend
- Use contractions and natural phrasing
- Keep sentences shorter and more dynamic
- Suitable for: Blogs, social media, lifestyle content
""",
    "academic": """
**ACADEMIC STYLE:**
- Use scholarly language with proper citations
- Include detailed explanations and analysis
- Reference studies and research findings
- Use field-specific terminology appropriately
- Maintain objectivity and analytical perspective
- Suitable for: Research summaries, educational content, white papers
""",
    "journalistic": """
**JOURNALISTIC STYLE:**
- Use clear, factual reporting language
- Lead with the most important information (inverted pyramid)
- Include who, what, when, where, why, how
- Use short, punchy sentences
- Attribute all claims to sources
- Suitable for: News articles, press releases, feature stories
""",
    "marketing": """
**MARKETING STYLE:**
- Use persuasive, benefit-focused language
- Highlight value propositions and outcomes
- Include calls to action where appropriate
- Create emotional connection with readers
- Use power words that drive engagement
- Suitable for: Landing pages, promotional content, product descriptions
""",
}

# Tone instructions for different tones
TONE_INSTRUCTIONS = {
    "neutral": """
**NEUTRAL TONE:**
- Maintain balanced, objective perspective
- Avoid strong emotional language
- Present information factually
- Let the content speak for itself
- Suitable for: Informational content, reports, general articles
""",
    "enthusiastic": """
**ENTHUSIASTIC TONE:**
- Show genuine excitement about the topic
- Use energetic, positive language
- Highlight the best aspects while staying credible
- Create momentum and engagement
- Suitable for: Announcements, reviews, promotional content
""",
    "authoritative": """
**AUTHORITATIVE TONE:**
- Project confidence and expertise
- Make declarative statements
- Use strong, definitive language
- Demonstrate deep knowledge of the subject
- Suitable for: Expert guides, thought leadership, professional advice
""",
    "conversational": """
**CONVERSATIONAL TONE:**
- Write as if speaking directly to the reader
- Use "you" and "we" to create connection
- Include rhetorical questions
- Be personable and approachable
- Suitable for: Blog posts, how-to guides, personal content
""",
}


def get_rewriter_prompt(
    original_content: str,
    client_name: str | None,
    research_brief: dict,
    style: str = "professional",
    tone: str = "neutral",
    target_word_count: int | None = None,
    preserve_structure: bool = True,
) -> str:
    """
    Generate the user prompt for content rewriting.

    Args:
        original_content: The original content to rewrite
        client_name: Name of the client/entity (optional)
        research_brief: Compiled research material for enhancement
        style: Writing style to apply
        tone: Tone to apply
        target_word_count: Target word count (defaults to original length)
        preserve_structure: Whether to preserve the original structure

    Returns:
        Formatted user prompt for rewriting
    """
    # Get style and tone instructions
    style_instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["professional"])
    tone_instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["neutral"])

    # Format statistics from research
    stats_section = ""
    if research_brief.get("statistics"):
        stats_items = []
        for stat in research_brief["statistics"][:5]:
            if isinstance(stat, dict):
                stats_items.append(
                    f"- {stat.get('value', '')} - {stat.get('context', '')} "
                    f"(Source: {stat.get('source', 'Unknown')})"
                )
        stats_section = "\n".join(stats_items) if stats_items else "No statistics available"

    # Format quotations from research
    quotes_section = ""
    if research_brief.get("quotations"):
        quote_items = []
        for quote in research_brief["quotations"][:3]:
            if isinstance(quote, dict):
                quote_items.append(
                    f'- "{quote.get("quote", "")}" '
                    f'— {quote.get("speaker", "Expert")}, {quote.get("title", "")}'
                )
        quotes_section = "\n".join(quote_items) if quote_items else "No quotations available"

    # Format citations from research
    citations_section = ""
    if research_brief.get("citations"):
        cite_items = []
        for cite in research_brief["citations"][:6]:
            if isinstance(cite, dict):
                cite_items.append(f"- {cite.get('name', '')} - {cite.get('description', '')}")
        citations_section = "\n".join(cite_items) if cite_items else "No citations available"

    # Format key facts from research
    facts_section = ""
    if research_brief.get("key_facts"):
        facts_section = "\n".join(
            f"- {fact}" for fact in research_brief["key_facts"][:10]
        )

    # Calculate original word count
    original_word_count = len(original_content.split())

    # Determine target word count
    if target_word_count is None:
        target_word_count = original_word_count  # Maintain similar length

    # Structure preservation instruction
    structure_instruction = ""
    if preserve_structure:
        structure_instruction = """
## STRUCTURE PRESERVATION
- Maintain the original heading structure (H1, H2, H3)
- Keep the same logical flow and section order
- Preserve the number of main sections
- You may add subpoints or details within sections
"""
    else:
        structure_instruction = """
## STRUCTURE OPTIMIZATION
- You may reorganize the content for better flow
- Create new headings that mirror common search queries
- Restructure paragraphs for optimal AI citation
- Maintain logical progression of ideas
"""

    # Client mention instruction
    client_instruction = ""
    if client_name:
        client_instruction = f"""
## ENTITY OPTIMIZATION
- Mention "{client_name}" 4-6 times throughout the content
- Include in the opening paragraph
- Distribute mentions naturally in the body
- Include in the closing statement
"""

    return f"""
## CONTENT REWRITE REQUEST

**Language:** {research_brief.get('language_code', 'auto-detect from original')}
{f'**Client/Entity:** {client_name}' if client_name else ''}
**Original Word Count:** {original_word_count}
**Target Word Count:** {target_word_count}

---

## STYLE & TONE TO APPLY

{style_instruction}

{tone_instruction}

---

{structure_instruction}

{client_instruction}

---

## RESEARCH MATERIAL FOR ENHANCEMENT

### Key Facts (Use to add depth)
{facts_section or "No additional facts available"}

### Statistics (Incorporate these to strengthen claims)
{stats_section or "No statistics available - improve existing statistics if possible"}

### Expert Quotations (Add authority with these)
{quotes_section or "No quotations available - improve existing quotes if possible"}

### Credible Sources (Cite these for credibility)
{citations_section or "No citations available - improve existing citations if possible"}

---

## ORIGINAL CONTENT TO REWRITE

{original_content}

---

## YOUR TASK

Rewrite the above content to:
1. Apply GEO optimization strategies (statistics, quotations, citations, fluency)
2. Apply the {style} style and {tone} tone
3. {'Preserve the original structure' if preserve_structure else 'Optimize the structure for AI visibility'}
4. Maintain the same language as the original
5. Target approximately {target_word_count} words
6. Enhance E-E-A-T signals throughout
{f'7. Mention "{client_name}" 4-6 times naturally' if client_name else ''}

Begin your response with the rewritten content directly. Do not include any preamble or explanation.
"""


def get_comparison_analysis_prompt(
    original_content: str,
    rewritten_content: str,
) -> str:
    """
    Generate a prompt to analyze the changes between original and rewritten content.

    Args:
        original_content: The original content
        rewritten_content: The rewritten content

    Returns:
        Prompt for analyzing changes
    """
    return f"""
Analyze the changes between the original and rewritten content below.

## ORIGINAL CONTENT
{original_content}

## REWRITTEN CONTENT
{rewritten_content}

## YOUR TASK

Provide a concise analysis including:

1. **Changes Summary** - List 5-8 key changes made (as a JSON array of strings)
2. **Statistics Added** - Count of new statistics added
3. **Citations Added** - Count of new citations/sources added
4. **Quotations Added** - Count of new expert quotations added
5. **Fluency Improvements** - List 3-5 specific fluency improvements made
6. **Structure Changes** - List any structural changes made
7. **E-E-A-T Enhancements** - List specific E-E-A-T improvements

Format your response as JSON:
{{
    "changes_summary": ["change 1", "change 2", ...],
    "statistics_added": <number>,
    "statistics_original": <number>,
    "citations_added": <number>,
    "citations_original": <number>,
    "quotations_added": <number>,
    "quotations_original": <number>,
    "fluency_improvements": ["improvement 1", "improvement 2", ...],
    "structure_changes": ["change 1", "change 2", ...],
    "eeat_enhancements": ["enhancement 1", "enhancement 2", ...]
}}
"""
