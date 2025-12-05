"""
RTL (Right-to-Left) formatting tool for Arabic content.

Handles proper RTL text formatting and reshaping for Arabic languages.
"""

from agents import function_tool

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    ARABIC_SUPPORT_AVAILABLE = True
except ImportError:
    ARABIC_SUPPORT_AVAILABLE = False


def format_rtl_content(content: str, language_code: str) -> dict:
    """
    Format content for RTL languages like Arabic.

    Adds RTL markers and provides HTML wrapper for proper display.

    Args:
        content: The content to format
        language_code: The language code (e.g., 'ar-MSA', 'ar-Gulf')

    Returns:
        Dictionary with formatted content and RTL metadata
    """
    # Only process Arabic languages
    if not language_code.startswith("ar-"):
        return {
            "content": content,
            "rtl": False,
            "direction": "ltr",
            "html_wrapper": content,
            "reshaped": False,
        }

    # Add RTL formatting
    formatted_content = _add_rtl_formatting(content)

    # Reshape Arabic text if library is available
    reshaped_content = formatted_content
    if ARABIC_SUPPORT_AVAILABLE:
        try:
            reshaped_content = _reshape_arabic(formatted_content)
        except Exception:
            # Fall back to non-reshaped if reshaping fails
            reshaped_content = formatted_content

    # Generate HTML wrapper
    html_wrapper = f'<div dir="rtl" lang="{language_code}">{formatted_content}</div>'

    return {
        "content": formatted_content,
        "reshaped_content": reshaped_content,
        "rtl": True,
        "direction": "rtl",
        "html_wrapper": html_wrapper,
        "language_code": language_code,
        "reshaped": ARABIC_SUPPORT_AVAILABLE,
    }


def _add_rtl_formatting(content: str) -> str:
    """
    Add RTL markers to content for proper display.

    Adds Right-to-Left Mark (RLM, U+200F) at the start of paragraphs.

    Args:
        content: Raw content text

    Returns:
        Content with RTL markers added
    """
    RTL_MARK = "\u200F"  # Right-to-Left Mark

    # Split by double newlines (paragraphs)
    paragraphs = content.split("\n\n")
    formatted = []

    for paragraph in paragraphs:
        if paragraph.strip():
            # Add RTL mark at the start of each paragraph
            formatted.append(RTL_MARK + paragraph)
        else:
            formatted.append(paragraph)

    return "\n\n".join(formatted)


def _reshape_arabic(text: str) -> str:
    """
    Reshape Arabic text for proper display.

    Arabic characters change shape based on their position in a word.
    This function ensures proper character shaping.

    Args:
        text: Arabic text to reshape

    Returns:
        Reshaped Arabic text
    """
    if not ARABIC_SUPPORT_AVAILABLE:
        return text

    try:
        # Reshape the Arabic text
        reshaped_text = arabic_reshaper.reshape(text)
        # Apply BiDi algorithm for proper display order
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception:
        # Return original if reshaping fails
        return text


def generate_rtl_css() -> str:
    """
    Generate CSS styles for RTL content display.

    Returns:
        CSS string for RTL styling
    """
    return """
    .rtl-content {
        direction: rtl;
        text-align: right;
        font-family: 'Arial', 'Tahoma', 'Traditional Arabic', sans-serif;
        line-height: 1.8;
    }

    .rtl-content h1, .rtl-content h2, .rtl-content h3 {
        text-align: right;
    }

    .rtl-content ul, .rtl-content ol {
        padding-right: 2em;
        padding-left: 0;
    }

    .rtl-content blockquote {
        border-right: 4px solid #ccc;
        border-left: none;
        padding-right: 1em;
        padding-left: 0;
        margin-right: 1em;
        margin-left: 0;
    }
    """


@function_tool
def rtl_formatter_tool(content: str, language_code: str) -> dict:
    """
    Format content for right-to-left (RTL) languages like Arabic.

    This tool:
    - Adds RTL markers for proper text display
    - Reshapes Arabic characters for correct rendering
    - Provides HTML wrapper with proper dir and lang attributes

    Args:
        content: The content to format
        language_code: The language code (e.g., 'ar-MSA', 'ar-Gulf', 'ar-EG')

    Returns:
        Dictionary with formatted content, RTL flag, direction, and HTML wrapper
    """
    return format_rtl_content(content, language_code)
