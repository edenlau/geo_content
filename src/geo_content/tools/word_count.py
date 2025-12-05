"""
Language-aware word counting utility.

Handles word counting for CJK (Chinese, Japanese, Korean) languages
which don't use spaces between words.
"""

import re
import unicodedata


def count_words(text: str, language_code: str = "en") -> int:
    """
    Count words in text with language awareness.

    For CJK languages (Chinese, Japanese, Korean), counts characters
    since these languages don't use spaces between words.
    For other languages, uses standard whitespace-based word counting.

    Args:
        text: The text to count words in
        language_code: Language code (e.g., "en", "zh-TW", "ja", "ko")

    Returns:
        Word count (or character count for CJK)
    """
    if not text:
        return 0

    # Check if CJK language
    if language_code.startswith(("zh", "ja", "ko")):
        return _count_cjk_characters(text)
    else:
        return _count_words_standard(text)


def _count_cjk_characters(text: str) -> int:
    """
    Count meaningful characters in CJK text.

    Excludes whitespace and punctuation, counts only actual content characters.
    """
    count = 0
    for char in text:
        # Skip whitespace
        if char.isspace():
            continue
        # Skip punctuation (both ASCII and Unicode)
        category = unicodedata.category(char)
        if category.startswith("P"):  # Punctuation categories
            continue
        # Skip ASCII symbols
        if category.startswith("S"):  # Symbol categories
            continue
        count += 1
    return count


def _count_words_standard(text: str) -> int:
    """
    Count words using standard whitespace splitting.

    Used for space-delimited languages like English, Arabic, etc.
    """
    return len(text.split())


def get_word_count_target(target_words: int, language_code: str) -> int:
    """
    Adjust word count target for the language.

    For CJK languages, the target is in characters, not words.
    A rough conversion: 1 English word ≈ 2 Chinese characters on average.

    Args:
        target_words: Target word count in English
        language_code: Language code

    Returns:
        Adjusted target for the language
    """
    if language_code.startswith(("zh", "ja", "ko")):
        # For CJK: target is in characters
        # 1 English word ≈ 2 CJK characters on average
        return int(target_words * 2)
    return target_words
