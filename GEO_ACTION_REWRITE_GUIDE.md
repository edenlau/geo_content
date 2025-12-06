# Tocanan GEO Action - Rewrite Feature Guide

**Transform Existing Content for Maximum AI Visibility**

Version 1.0 | December 2025

---

## Table of Contents

1. [What is Content Rewriting?](#part-1-what-is-content-rewriting)
2. [How to Use the Rewrite Feature](#part-2-how-to-use-rewrite)
3. [Understanding Your Results](#part-3-understanding-results)
4. [Best Practices](#part-4-best-practices)
5. [Troubleshooting](#part-5-troubleshooting)

---

# Part 1: What is Content Rewriting?

## The Rewrite Feature: Transform Your Existing Content

The **Rewrite** feature takes your existing content—from a URL or uploaded file—and transforms it with GEO (Generative Engine Optimization) strategies while preserving the original message and language.

### When to Use Rewrite vs Generate

| Use Case | Feature | Why |
|----------|---------|-----|
| Create new content from scratch | **Generate** | Need original content for a target question |
| Optimize existing blog post | **Rewrite** | Already have content, want to improve AI visibility |
| Enhance published article | **Rewrite** | Want to add citations, statistics, and E-E-A-T signals |
| Repurpose competitor content | **Rewrite** | Transform with your style and entity focus |
| Update outdated content | **Rewrite** | Modernize with new data and GEO optimizations |
| Convert document to web-ready | **Rewrite** | Transform PDF/DOCX to optimized web content |

---

## How Rewrite Works

The Rewrite workflow follows these steps:

1. **Content Extraction** - Fetches content from URL or parses uploaded file
2. **Language Detection** - Identifies and preserves the original language
3. **Research Enhancement** - Gathers additional facts, statistics, and citations from reference materials
4. **GEO Rewriting** - Transforms content with your chosen style/tone while applying all 4 GEO strategies
5. **Evaluation** - Scores the rewritten content using the o4-mini reasoning model
6. **Comparison** - Shows before/after analysis with applied optimizations

---

## The Technology Behind Rewrite

| Component | Technology | Purpose |
|-----------|------------|---------|
| Content Parser | Pathway | Extracts text from URLs, PDFs, DOCX files |
| Research Agent | GPT-5 | Gathers supporting facts and statistics |
| Rewriter Agent A | GPT-5 | Rewrites with GEO optimizations |
| Rewriter Agent B | Claude Sonnet 4.5 | Alternative rewrite for comparison |
| Evaluator | o4-mini | Scores and selects best rewrite |

---

# Part 2: How to Use the Rewrite Feature

## Step 1: Access the Rewrite Tab

Navigate to: **https://geoaction.tocanan.ai**

Click the **"Rewrite"** tab in the navigation header.

---

## Step 2: Provide Source Content

You have **two options** for providing content to rewrite:

### Option A: Enter a URL

1. Enter the full URL of the content you want to rewrite
2. Click the **"Preview"** button to fetch and preview the content
3. Verify the preview shows the correct content, word count, and language

**Tips:**
- Ensure the URL is publicly accessible (not behind a paywall or login)
- The platform will automatically extract the main content from the page
- Works best with article pages, blog posts, and structured content

**Example:**
```
https://www.example.com/blog/cloud-computing-guide
```

### Option B: Upload a File

1. Click **"Upload File"** button
2. Select a file from your computer
3. Supported formats: PDF, DOCX, DOC, TXT, MD

**Tips:**
- Maximum file size: 10MB
- For PDFs, ensure text is selectable (not scanned images)
- Multi-page documents are fully supported

---

## Step 3: Choose Writing Style

Select a **writing style** that matches your target audience:

| Style | Description | Best For |
|-------|-------------|----------|
| **Professional** | Formal business language | Corporate content, B2B, official communications |
| **Casual** | Friendly, conversational | Blogs, social media, consumer-facing content |
| **Academic** | Scholarly with citations | Research papers, whitepapers, educational content |
| **Journalistic** | News reporting style | Press releases, news articles, industry reports |
| **Marketing** | Persuasive, benefit-focused | Landing pages, product descriptions, sales content |

---

## Step 4: Choose Tone

Select a **tone** that matches your brand voice:

| Tone | Description | Best For |
|------|-------------|----------|
| **Neutral** | Balanced and objective | Informational content, guides, documentation |
| **Enthusiastic** | Energetic and positive | Product launches, announcements, promotional content |
| **Authoritative** | Expert and confident | Thought leadership, expert advice, industry analysis |
| **Conversational** | Direct and personal | Customer communications, FAQs, support content |

---

## Step 5: Configure Options

### Preserve Structure
- **Checked (default):** Maintains the original heading hierarchy and section organization
- **Unchecked:** Allows the rewriter to restructure content for better flow

**Recommendation:** Keep checked for most use cases, especially if the original structure is logical.

---

### Target Word Count

**Option 1: Use Original Length**
- Checked (default): Output will match the original content length
- Best for: Replacing existing content without layout changes

**Option 2: Custom Word Count**
- Uncheck "Use original content length"
- Adjust slider from 100 to 5,000 words
- Best for: Expanding brief content or condensing long articles

---

### Client/Entity Name (Optional)

Enter the organization, brand, or person you want to optimize visibility for.

**Why it matters:** The rewriter will naturally integrate 4-8 mentions of this entity throughout the content, optimizing for AI citation when users search for that entity.

**Examples:**
- "Ocean Park Hong Kong"
- "Tocanan Digital Marketing"
- "Dr. Sarah Chen, AI Specialist"

---

### Reference URLs (Optional but Recommended)

Add 1-5 URLs containing additional research material to enhance your rewrite.

**Why it matters:** The rewriter uses these to:
- Add relevant statistics with source attribution
- Include expert quotations
- Enhance credibility with authoritative citations

**Best practices:**
- Include official sources (government, academic)
- Add industry research reports
- Include recent news articles on the topic

---

### Reference Files (Optional)

Upload additional PDF, DOCX, or TXT files for research enhancement.

**Use cases:**
- Annual reports with statistics
- Research studies with data
- Internal documents with proprietary information

---

### Language Override (Optional)

By default, the rewriter preserves the original language. Override only if you want to translate.

**Supported languages:**
- English (US, UK, Australian)
- Traditional Chinese (zh-TW)
- Simplified Chinese (zh-CN)
- Arabic dialects (MSA, Gulf, Egyptian, Levantine, Maghrebi)

---

## Step 6: Submit and Monitor

Click **"Rewrite with GEO Optimization"** button.

You'll see:
1. **Job ID:** Unique identifier (e.g., `rewrite_abc123`)
2. **Elapsed Time:** Real-time progress timer
3. **Status Updates:**
   - Extracting content...
   - Researching enhancements...
   - Rewriting with GEO optimizations...
   - Evaluating quality...
   - Finalizing comparison...

**Typical processing time:** 45-120 seconds (varies by content length and references)

---

# Part 3: Understanding Your Results

## A. Content Comparison

### What You'll See:

A **side-by-side comparison** showing:

| Original | Rewritten |
|----------|-----------|
| Original content | GEO-optimized version |
| Word count | New word count |
| | Changes applied |

### Key Metrics:

- **Original Word Count:** Length of source content
- **Rewritten Word Count:** Length after optimization
- **Changes Summary:** List of transformations applied

---

## B. Optimizations Applied

A detailed breakdown of **what was enhanced**:

### Statistics Added
- Count of new data points added
- Source attributions included
- Example: "Added 4 statistics from 3 sources"

### Citations Added
- New authoritative references
- Source diversity (government, academic, industry)
- Example: "Added 5 citations including 2 government sources"

### Quotations Added
- Expert quotes with attribution
- Industry authorities and specialists
- Example: "Added 2 expert quotations"

### Fluency Improvements
- Sentence restructuring
- Readability enhancements
- Grade level improvements

### Structure Changes
- Heading additions/modifications
- List formatting improvements
- Paragraph organization

### E-E-A-T Enhancements
- Experience signals added
- Expertise demonstrations
- Authority citations
- Trust-building elements

---

## C. Evaluation Scores

Same scoring system as Generate:

| Score Range | Quality | Interpretation |
|-------------|---------|----------------|
| **85-100** | Excellent | Publish as-is |
| **70-84** | Good | Minor improvements recommended |
| **60-69** | Fair | Address High Priority items |
| **<60** | Needs Work | Consider re-rewriting with better references |

---

## D. GEO Commentary

Detailed analysis explaining:
- Why the rewritten content will perform better
- Strategy-by-strategy effectiveness ratings
- E-E-A-T score breakdown
- Selection rationale (if multiple rewrites compared)

---

## E. GEO Insights (5 Cards)

Same actionable insights as Generate:

1. **Implementation Checklist** - Priority actions to take
2. **Benchmark Comparison** - Competitiveness vs top content
3. **Keyword & Entity Analysis** - Entity mention optimization
4. **Source Quality Analysis** - Citation credibility audit
5. **Content Structure Score** - Format optimization

---

## F. Download Options

After rewriting, you can:

1. **Copy Rewritten Content** - Copy to clipboard
2. **Download as Markdown** - Save as .md file
3. **Download Comparison** - Full before/after document
4. **Export Schema Markup** - JSON-LD for your webpage

---

# Part 4: Best Practices

## Before Rewriting

### Provide High-Quality Source Content
- Ensure source URL is accessible and loads correctly
- For uploads, use clean, well-formatted documents
- Avoid PDFs with poor OCR or scanned images

### Add Reference Materials
- **Critical:** Without reference URLs/files, the rewriter can only optimize structure and fluency
- **With references:** Can add statistics, citations, and expert quotes
- **Best results:** 3-5 high-authority reference URLs

### Choose Appropriate Style/Tone Combination

| Content Type | Recommended Style | Recommended Tone |
|--------------|-------------------|------------------|
| Corporate blog | Professional | Authoritative |
| Product landing page | Marketing | Enthusiastic |
| Technical guide | Academic | Neutral |
| News article | Journalistic | Neutral |
| Consumer blog | Casual | Conversational |

---

## After Rewriting

### Verify Factual Accuracy
- Check all statistics are correct
- Verify quotation attributions
- Confirm source links work

### Review Entity Mentions
- Ensure your entity is mentioned 4-8 times
- Check mentions feel natural, not forced
- Replace with pronouns if repetitive

### Implement High Priority Checklist Items
- Address all red (High Priority) items before publishing
- Focus on citation and statistic gaps first

### Compare Word Counts
- If significantly shorter/longer than original, review for completeness
- Ensure key messages weren't cut

---

## Common Mistakes to Avoid

### Using Low-Quality Source Content
**Problem:** Rewriting poorly written content produces marginally improved output.
**Fix:** Consider using Generate for new content instead, or manually improve source first.

### Skipping Reference URLs
**Problem:** Without references, no new statistics or citations can be added.
**Fix:** Always add 3-5 reference URLs from authoritative sources.

### Wrong Style/Tone for Audience
**Problem:** Academic style for casual blog alienates readers.
**Fix:** Match style and tone to your target audience and platform.

### Ignoring the Comparison
**Problem:** Publishing without reviewing what changed.
**Fix:** Always read the changes summary and verify key messages remain intact.

---

# Part 5: Troubleshooting

## Problem: URL Preview Fails

### Symptoms:
- "Failed to fetch URL content" error
- Preview shows wrong content
- Empty preview

### Solutions:
1. **Check URL is accessible:**
   - Open in incognito/private browser
   - Ensure no login required
   - Verify not behind paywall

2. **Try different URL:**
   - Some sites block automated access
   - Use article permalink, not homepage
   - Avoid URLs with excessive tracking parameters

3. **Upload file instead:**
   - Copy content to Word/PDF
   - Upload the file

---

## Problem: Rewritten Content Missing Key Information

### Symptoms:
- Important points from original not in rewrite
- Content seems incomplete
- Word count significantly lower

### Solutions:
1. **Increase target word count:**
   - Uncheck "Use original content length"
   - Set higher word count target

2. **Check source content quality:**
   - Ensure important sections weren't in headers/footers
   - Verify PDF text extraction worked properly

3. **Add key points as reference:**
   - Create a text file with must-include information
   - Upload as reference file

---

## Problem: Style/Tone Doesn't Match Expectations

### Symptoms:
- Output too formal/informal
- Tone feels wrong for brand
- Style inconsistent

### Solutions:
1. **Try different combination:**
   - Professional + Conversational = formal but friendly
   - Casual + Authoritative = approachable expertise
   - Marketing + Enthusiastic = high-energy promotional

2. **Provide style examples:**
   - Add your best content as reference URL
   - Rewriter will incorporate patterns

3. **Post-rewrite editing:**
   - Treat as strong first draft
   - Adjust specific phrases for brand voice

---

## Problem: Low Evaluation Score

### Symptoms:
- Score below 70
- Multiple low category scores
- Checklist shows many High Priority items

### Solutions:
1. **Add more reference URLs:**
   - Include government/academic sources
   - Add industry research reports
   - Provide statistics-rich content

2. **Re-rewrite with better inputs:**
   - Clear form and start fresh
   - Use higher-quality source content
   - Add comprehensive reference materials

3. **Manually enhance:**
   - Implement all High Priority checklist items
   - Add missing citations/statistics manually

---

## Problem: Processing Takes Too Long

### Symptoms:
- Stuck on "Processing..." for >3 minutes
- No progress updates
- Eventually times out

### Solutions:
1. **Check content length:**
   - Very long content (>3000 words) takes longer
   - Consider splitting into sections

2. **Reduce reference complexity:**
   - Too many large PDFs slow processing
   - Limit to 3-5 focused references

3. **Retry:**
   - Refresh page and submit again
   - Backend may have experienced temporary issue

---

# Appendix: Quick Reference

## Style + Tone Combinations

| Combination | Result | Best For |
|-------------|--------|----------|
| Professional + Neutral | Balanced corporate | Annual reports, policies |
| Professional + Authoritative | Expert business | Thought leadership |
| Casual + Conversational | Friendly chat | Consumer blogs, social |
| Academic + Neutral | Scholarly | Research, whitepapers |
| Journalistic + Neutral | News reporting | Press releases |
| Marketing + Enthusiastic | High energy | Product launches |

---

## Input Checklist

Before clicking "Rewrite":

- [ ] Source URL entered OR file uploaded
- [ ] URL preview shows correct content (if using URL)
- [ ] Style selected appropriate to audience
- [ ] Tone selected appropriate to brand
- [ ] Preserve structure set correctly
- [ ] Word count configured (or using original)
- [ ] Reference URLs added (3-5 recommended)
- [ ] Client/entity name entered (for visibility optimization)

---

## Output Checklist

Before publishing rewritten content:

- [ ] Reviewed comparison - key messages preserved
- [ ] Checked evaluation score (aim for 75+)
- [ ] Implemented all High Priority checklist items
- [ ] Verified statistics and citations are accurate
- [ ] Confirmed entity mentions are natural
- [ ] Copied schema markup for webpage injection
- [ ] Downloaded backup copy

---

**Platform URL:** https://geoaction.tocanan.ai

**Related Guide:** [GEO Action User Guide](./GEO_ACTION_USER_GUIDE.md) - For Generate feature

---

**Document Version:** 1.0 | December 2025

**Last Updated:** December 6, 2025

**Platform Version:** GEO Action v3.3.0
