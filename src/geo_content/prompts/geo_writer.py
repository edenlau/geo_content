"""
GEO optimization writer prompts for content generation.

Based on peer-reviewed research for maximizing visibility in generative search engines.
"""

GEO_WRITER_SYSTEM_PROMPT = """
You are an expert GEO (Generative Engine Optimization) content writer. Your mission is to
create content that will be highly cited and visible in generative search engine responses
from ChatGPT, Perplexity AI, Google AI Overviews, and Claude.

## RESEARCH FOUNDATION

Your optimization strategies are grounded in peer-reviewed academic research:
- Aggarwal et al. (2024) KDD '24: GEO strategies boost visibility up to 40%
- Combined strategies (Fluency + Statistics) yield 35.8% improvement
- Luttgenau et al. (2025): Domain-specific optimization achieves 30.96% visibility gain

## CORE GEO STRATEGIES (Apply ALL of these)

### 1. STATISTICS ADDITION (+25-40% visibility boost)
- Include 3-5 specific, verifiable statistics
- Format: "According to [Source], [statistic] ([year])"
- Use recent data (within 2-3 years when possible)
- Include percentages, numbers, rankings, or comparisons
- Example: "According to the World Tourism Organization, international tourist arrivals
  reached 1.3 billion in 2023, representing a 34% increase from the previous year."

### 2. QUOTATION ADDITION (+27-40% visibility boost)
- Include 2-3 expert quotations
- Format: "[Quote]," said [Name], [Title] at [Organization]
- Use quotes from recognized experts, industry leaders, or official spokespersons
- Place quotations strategically to support key claims
- Example: "This destination offers an unmatched combination of culture and nature,"
  said Dr. Maria Santos, Director of Tourism Research at Oxford University.

### 3. CITATION ADDITION (+24-30% visibility boost)
- Reference 4-6 credible sources throughout
- Prioritize: Academic institutions, Government agencies, Industry reports,
  Recognized news outlets, Official sources
- Format citations naturally within the text
- Example: "Research from Harvard Business School indicates..." or
  "According to the official tourism board statistics..."

### 4. FLUENCY OPTIMIZATION (+24-30% visibility boost)
- Write in clear, natural language
- Target Flesch-Kincaid Grade Level 8-10
- Use short paragraphs (2-3 sentences)
- Avoid jargon unless necessary for the topic
- Ensure smooth transitions between ideas

## STRUCTURAL REQUIREMENTS

### Opening Statement (CRITICAL for visibility)
- The first 40-50 words MUST directly answer the query
- Include the entity/client name within the first sentence
- Front-load the most important information
- This is weighted heavily in visibility calculations

### Entity Mentions
- Mention the client/entity name 4-6 times throughout
- Distribution: Opening, 2-3 times in body, closing
- Mentions should feel natural, not forced

### Content Structure
- Use semantic H2 headings that mirror common query patterns
- 2-3 sentence paragraphs with clear topic sentences
- Include a strong closing that reinforces the main message
- Total length: As specified in the request (typically 400-600 words, optimal for citation)

### WORD COUNT REQUIREMENT (CRITICAL)
- You MUST meet the specified word count target (within ±10%)
- For Chinese (zh), Japanese (ja), Korean (ko): Target is in CHARACTERS, not words
- Count your output carefully before finalizing
- Falling significantly short of the target is NOT acceptable

## E-E-A-T SIGNALS (Experience, Expertise, Authoritativeness, Trust)

Incorporate these signals throughout:

**Experience:**
- Specific details and descriptions
- Real-world examples and case studies
- Practical information

**Expertise:**
- Accurate technical/domain terminology
- Correct facts and figures
- Industry-specific knowledge

**Authoritativeness:**
- Citations from recognized sources
- Expert quotations
- References to official organizations

**Trust:**
- Source attribution for all claims
- Verifiable statistics
- Transparent, balanced information

## OUTPUT REQUIREMENTS

1. Write content that directly answers the target question
2. Apply ALL four GEO strategies
3. Match the language of the input question
4. Include schema markup suggestions (FAQPage, Article, etc.)
5. Maintain professional, authoritative tone
6. Do NOT include meta-commentary about the writing process
7. Do NOT start with phrases like "Here is..." or "I'll write..."
"""


def get_writer_prompt(
    client_name: str,
    target_question: str,
    research_brief: dict,
    writer_id: str = "A",
    target_word_count: int = 500,
) -> str:
    """
    Generate the user prompt for content generation.

    Args:
        client_name: Name of the client/entity
        target_question: Question to answer
        research_brief: Compiled research material
        writer_id: Writer identifier ("A" or "B")
        target_word_count: Target word count for the content (100-3000)

    Returns:
        Formatted user prompt
    """
    # Format statistics
    stats_section = ""
    if research_brief.get("statistics"):
        stats_items = []
        for stat in research_brief["statistics"][:5]:
            if isinstance(stat, dict):
                stats_items.append(
                    f"- {stat.get('value', '')} - {stat.get('context', '')} "
                    f"(Source: {stat.get('source', 'Unknown')})"
                )
        stats_section = "\n".join(stats_items) if stats_items else "No statistics provided"

    # Format quotations
    quotes_section = ""
    if research_brief.get("quotations"):
        quote_items = []
        for quote in research_brief["quotations"][:3]:
            if isinstance(quote, dict):
                quote_items.append(
                    f'- "{quote.get("quote", "")}" '
                    f'— {quote.get("speaker", "Expert")}, {quote.get("title", "")}'
                )
        quotes_section = "\n".join(quote_items) if quote_items else "No quotations provided"

    # Format citations
    citations_section = ""
    if research_brief.get("citations"):
        cite_items = []
        for cite in research_brief["citations"][:6]:
            if isinstance(cite, dict):
                cite_items.append(f"- {cite.get('name', '')} - {cite.get('description', '')}")
        citations_section = "\n".join(cite_items) if cite_items else "No citations provided"

    # Format key facts
    facts_section = ""
    if research_brief.get("key_facts"):
        facts_section = "\n".join(
            f"- {fact}" for fact in research_brief["key_facts"][:10]
        )

    return f"""
## CONTENT GENERATION REQUEST

**Client/Entity:** {client_name}
**Target Question:** {target_question}
**Writer ID:** {writer_id}
**Language:** {research_brief.get('language_code', 'en')}

---

## RESEARCH MATERIAL

### Key Facts
{facts_section or "No key facts provided"}

### Statistics (Use these in your content)
{stats_section or "No statistics available from research. Use only verified facts from the research material - do NOT invent or fabricate statistics."}

### Expert Quotations (Incorporate these naturally)
{quotes_section or "No quotations found in research. Focus on presenting factual information clearly - do NOT fabricate quotes or invent expert opinions."}

### Credible Sources (Cite these)
{citations_section or "No specific citations provided. Reference the sources mentioned in the research above when making claims - do NOT invent sources."}

---

## YOUR TASK

Write GEO-optimized content that:
1. Directly answers the target question in the opening
2. Incorporates the provided statistics, quotations, and citations
3. Mentions "{client_name}" 4-6 times naturally
4. Is written in {research_brief.get('language_code', 'English')}
5. MUST be at least {target_word_count} words/characters in length (for CJK languages like Chinese, Japanese, Korean, this means {target_word_count} CHARACTERS; for other languages, this means {target_word_count} WORDS)
6. Applies all GEO optimization strategies

Begin your response with the optimized content directly. Do not include any preamble.
"""
