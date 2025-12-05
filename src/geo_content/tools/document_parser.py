"""
Document parsing tool for GEO Content Platform.

Supports PDF and DOCX document parsing for research input.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from agents import function_tool

logger = logging.getLogger(__name__)

# Try to import document parsing libraries
try:
    from pypdf import PdfReader

    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    PdfReader = None

try:
    from docx import Document as DocxDocument

    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    DocxDocument = None


@dataclass
class ParsedDocument:
    """Represents a parsed document."""

    file_path: str
    file_type: str
    title: str
    content: str
    word_count: int
    page_count: int | None
    metadata: dict

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "file_type": self.file_type,
            "title": self.title,
            "content": self.content,
            "word_count": self.word_count,
            "page_count": self.page_count,
            "metadata": self.metadata,
        }


def parse_pdf(file_path: str) -> ParsedDocument | None:
    """
    Parse a PDF document.

    Args:
        file_path: Path to the PDF file

    Returns:
        ParsedDocument or None if parsing fails
    """
    if not PDF_SUPPORT:
        logger.error("PDF support not available. Install pypdf.")
        return None

    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        reader = PdfReader(file_path)

        # Extract text from all pages
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        content = "\n\n".join(text_parts)
        word_count = len(content.split())

        # Extract metadata
        metadata = {}
        if reader.metadata:
            if reader.metadata.title:
                metadata["title"] = reader.metadata.title
            if reader.metadata.author:
                metadata["author"] = reader.metadata.author
            if reader.metadata.subject:
                metadata["subject"] = reader.metadata.subject
            if reader.metadata.creation_date:
                metadata["creation_date"] = str(reader.metadata.creation_date)

        title = metadata.get("title", path.stem)

        return ParsedDocument(
            file_path=file_path,
            file_type="pdf",
            title=title,
            content=content,
            word_count=word_count,
            page_count=len(reader.pages),
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return None


def parse_docx(file_path: str) -> ParsedDocument | None:
    """
    Parse a DOCX document.

    Args:
        file_path: Path to the DOCX file

    Returns:
        ParsedDocument or None if parsing fails
    """
    if not DOCX_SUPPORT:
        logger.error("DOCX support not available. Install python-docx.")
        return None

    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        doc = DocxDocument(file_path)

        # Extract text from paragraphs
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_parts.append(" | ".join(row_text))

        content = "\n\n".join(text_parts)
        word_count = len(content.split())

        # Extract metadata from core properties
        metadata = {}
        core_props = doc.core_properties
        if core_props.title:
            metadata["title"] = core_props.title
        if core_props.author:
            metadata["author"] = core_props.author
        if core_props.subject:
            metadata["subject"] = core_props.subject
        if core_props.created:
            metadata["created"] = str(core_props.created)
        if core_props.modified:
            metadata["modified"] = str(core_props.modified)

        title = metadata.get("title", path.stem)

        return ParsedDocument(
            file_path=file_path,
            file_type="docx",
            title=title,
            content=content,
            word_count=word_count,
            page_count=None,  # DOCX doesn't have fixed pages
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {e}")
        return None


def parse_text(file_path: str) -> ParsedDocument | None:
    """
    Parse a plain text document.

    Args:
        file_path: Path to the text file

    Returns:
        ParsedDocument or None if parsing fails
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        # Try different encodings
        content = None
        for encoding in ["utf-8", "utf-16", "latin-1"]:
            try:
                content = path.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            logger.error(f"Could not decode file: {file_path}")
            return None

        word_count = len(content.split())

        return ParsedDocument(
            file_path=file_path,
            file_type="txt",
            title=path.stem,
            content=content,
            word_count=word_count,
            page_count=None,
            metadata={"encoding": encoding},
        )

    except Exception as e:
        logger.error(f"Error parsing text file {file_path}: {e}")
        return None


def parse_document(file_path: str) -> ParsedDocument | None:
    """
    Parse a document based on its file extension.

    Supports: PDF, DOCX, TXT, MD

    Args:
        file_path: Path to the document

    Returns:
        ParsedDocument or None if parsing fails or format not supported
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return parse_pdf(file_path)
    elif suffix in [".docx", ".doc"]:
        return parse_docx(file_path)
    elif suffix in [".txt", ".md", ".markdown"]:
        return parse_text(file_path)
    else:
        logger.error(f"Unsupported file format: {suffix}")
        return None


def parse_documents(file_paths: list[str]) -> list[ParsedDocument]:
    """
    Parse multiple documents.

    Args:
        file_paths: List of file paths to parse

    Returns:
        List of ParsedDocument objects (excludes failed parses)
    """
    results = []
    for file_path in file_paths:
        parsed = parse_document(file_path)
        if parsed:
            results.append(parsed)
    return results


@function_tool
def document_parser_tool(file_path: str) -> dict:
    """
    Parse a document and extract its text content.

    Supports PDF, DOCX, and plain text files (TXT, MD).

    Args:
        file_path: Path to the document file to parse

    Returns:
        Dictionary with file_path, file_type, title, content, word_count,
        page_count, and metadata
    """
    result = parse_document(file_path)
    if result:
        return result.to_dict()
    return {
        "error": f"Failed to parse document: {file_path}",
        "file_path": file_path,
    }


@function_tool
def multi_document_parser_tool(file_paths: list[str]) -> dict:
    """
    Parse multiple documents and extract their text content.

    Supports PDF, DOCX, and plain text files (TXT, MD).

    Args:
        file_paths: List of file paths to parse

    Returns:
        Dictionary with parsed documents and summary statistics
    """
    results = parse_documents(file_paths)
    return {
        "documents": [doc.to_dict() for doc in results],
        "total_documents": len(results),
        "total_words": sum(doc.word_count for doc in results),
        "failed_count": len(file_paths) - len(results),
    }
