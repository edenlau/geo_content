"""
Multi-format export utilities for GEO content.

Provides content in various formats optimized for different platforms.
"""

import html
import json
import re
from typing import Any


class MultiFormatExporter:
    """Export content in multiple formats."""

    def export_html(self, content: str, schema_markup: dict) -> str:
        """
        Export content as semantic HTML.

        Args:
            content: Markdown content
            schema_markup: Schema.org markup

        Returns:
            HTML string with semantic markup
        """
        # Convert markdown to HTML (simplified)
        html_content = self._markdown_to_html(content)

        # Wrap in semantic HTML5 structure
        html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script type="application/ld+json">
{json.dumps(schema_markup, indent=2, ensure_ascii=False)}
    </script>
</head>
<body>
    <article class="geo-optimized-content">
{html_content}
    </article>
</body>
</html>"""

        return html_output

    def export_markdown(self, content: str) -> str:
        """
        Export content as clean markdown.

        Args:
            content: Content string

        Returns:
            Clean markdown string
        """
        # Content is already in markdown, but we can clean it
        cleaned = content.strip()

        # Ensure consistent line breaks
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        return cleaned

    def export_plain_text(self, content: str) -> str:
        """
        Export content as plain text.

        Args:
            content: Markdown content

        Returns:
            Plain text version
        """
        # Remove markdown formatting
        text = content

        # Remove headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Remove bold/italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)

        # Remove links but keep text
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

        # Remove list markers
        text = re.sub(r'^\s*[-*+]\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '• ', text, flags=re.MULTILINE)

        # Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def export_json_ld(self, schema_markup: dict) -> str:
        """
        Export schema markup as JSON-LD.

        Args:
            schema_markup: Schema.org markup dictionary

        Returns:
            JSON-LD string
        """
        return json.dumps(schema_markup, indent=2, ensure_ascii=False)

    def _markdown_to_html(self, markdown: str) -> str:
        """
        Convert markdown to HTML (simplified implementation).

        Args:
            markdown: Markdown content

        Returns:
            HTML string
        """
        lines = markdown.split('\n')
        html_lines = []
        in_list = False
        list_type = None

        for line in lines:
            # Escape HTML
            line = html.escape(line)

            # Headers
            if line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
                continue
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
                continue
            elif line.startswith('### '):
                html_lines.append(f'<h3>{line[4:]}</h3>')
                continue
            elif line.startswith('#### '):
                html_lines.append(f'<h4>{line[5:]}</h4>')
                continue

            # Lists
            bullet_match = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
            number_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)

            if bullet_match:
                if not in_list or list_type != 'ul':
                    if in_list:
                        html_lines.append(f'</{list_type}>')
                    html_lines.append('<ul>')
                    in_list = True
                    list_type = 'ul'
                html_lines.append(f'<li>{bullet_match.group(2)}</li>')
                continue
            elif number_match:
                if not in_list or list_type != 'ol':
                    if in_list:
                        html_lines.append(f'</{list_type}>')
                    html_lines.append('<ol>')
                    in_list = True
                    list_type = 'ol'
                html_lines.append(f'<li>{number_match.group(2)}</li>')
                continue
            else:
                if in_list:
                    html_lines.append(f'</{list_type}>')
                    in_list = False
                    list_type = None

            # Paragraphs
            if line.strip():
                # Bold and italic
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                line = re.sub(r'__(.+?)__', r'<strong>\1</strong>', line)
                line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
                line = re.sub(r'_(.+?)_', r'<em>\1</em>', line)

                # Links
                line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', line)

                html_lines.append(f'<p>{line}</p>')
            else:
                html_lines.append('')

        # Close any open list
        if in_list:
            html_lines.append(f'</{list_type}>')

        return '\n'.join(html_lines)


class EnhancedSchemaGenerator:
    """Generate enhanced schema markup with multiple types."""

    def generate_article_schema(
        self,
        client_name: str,
        question: str,
        content: str,
    ) -> dict[str, Any]:
        """Generate Schema.org Article markup."""
        # Extract first paragraph as description
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        description = paragraphs[0][:200] + "..." if paragraphs else content[:200]

        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": question,
            "description": description,
            "author": {
                "@type": "Organization",
                "name": client_name,
            },
            "publisher": {
                "@type": "Organization",
                "name": client_name,
            },
            "articleBody": content,
        }

    def generate_faq_schema(self, content: str) -> dict[str, Any] | None:
        """
        Generate FAQPage schema if Q&A structure detected.

        Args:
            content: Content to analyze

        Returns:
            FAQPage schema or None if no Q&A detected
        """
        # Detect Q&A patterns
        qa_pairs = self._extract_qa_pairs(content)

        if len(qa_pairs) < 2:
            return None

        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a,
                    },
                }
                for q, a in qa_pairs
            ],
        }

    def generate_howto_schema(self, content: str, question: str) -> dict[str, Any] | None:
        """
        Generate HowTo schema if step-by-step content detected.

        Args:
            content: Content to analyze
            question: Original question

        Returns:
            HowTo schema or None if no steps detected
        """
        # Detect step-by-step patterns
        steps = self._extract_steps(content)

        if len(steps) < 3:
            return None

        return {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": question,
            "step": [
                {
                    "@type": "HowToStep",
                    "name": f"Step {i+1}",
                    "text": step,
                }
                for i, step in enumerate(steps)
            ],
        }

    def generate_organization_schema(self, client_name: str) -> dict[str, Any]:
        """Generate Organization schema for client entity."""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": client_name,
        }

    def _extract_qa_pairs(self, content: str) -> list[tuple[str, str]]:
        """Extract Q&A pairs from content."""
        qa_pairs = []

        # Look for common Q&A patterns
        lines = content.split('\n')
        current_q = None
        current_a = []

        for line in lines:
            # Question patterns: "Q:", "Question:", headings with "?"
            if re.match(r'^(Q:|Question:|###?\s+.+\?)', line):
                if current_q and current_a:
                    qa_pairs.append((current_q, '\n'.join(current_a)))
                current_q = re.sub(r'^(Q:|Question:|###?\s+)', '', line).strip()
                current_a = []
            # Answer patterns: "A:", "Answer:"
            elif re.match(r'^(A:|Answer:)', line):
                current_a.append(re.sub(r'^(A:|Answer:)', '', line).strip())
            elif current_q and line.strip():
                current_a.append(line.strip())

        # Add last Q&A pair
        if current_q and current_a:
            qa_pairs.append((current_q, '\n'.join(current_a)))

        return qa_pairs

    def _extract_steps(self, content: str) -> list[str]:
        """Extract step-by-step instructions from content."""
        steps = []

        # Look for numbered lists or step patterns
        lines = content.split('\n')

        for line in lines:
            # Numbered list pattern: "1. ", "Step 1:", etc.
            if re.match(r'^\s*(\d+\.|\d+\))\s+', line):
                step_text = re.sub(r'^\s*(\d+\.|\d+\))\s+', '', line).strip()
                if step_text:
                    steps.append(step_text)
            # Explicit step pattern
            elif re.match(r'^Step \d+:', line, re.IGNORECASE):
                step_text = re.sub(r'^Step \d+:\s*', '', line, flags=re.IGNORECASE).strip()
                if step_text:
                    steps.append(step_text)

        return steps


# Singleton instances
multi_format_exporter = MultiFormatExporter()
enhanced_schema_generator = EnhancedSchemaGenerator()
