"""
Language detection tool for GEO Content Platform.

Supports:
- English (en)
- Traditional Chinese (zh-TW)
- Simplified Chinese (zh-CN)
- Arabic - Modern Standard (ar-MSA)
- Arabic - Gulf (ar-Gulf)
- Arabic - Egyptian (ar-EG)
- Arabic - Levantine (ar-Levant)
- Arabic - Maghrebi (ar-Maghreb)
"""

import re
from typing import Literal

from agents import function_tool

from geo_content.models import LanguageDetectionResult


# Arabic dialect markers for detection
ARABIC_DIALECT_MARKERS: dict[str, list[str]] = {
    "ar-Gulf": ["شلونك", "وايد", "زين", "هالحين", "إمبى", "يالله", "خوش"],
    "ar-EG": ["إزيك", "كده", "برضو", "عايز", "فين", "إيه", "ازاي"],
    "ar-Levant": ["كيفك", "هلق", "شو", "منيح", "هيك", "كتير", "هلأ"],
    "ar-Maghreb": ["واش", "بزاف", "كيفاش", "ديال", "غادي", "مزيان", "لاباس"],
}

# Traditional Chinese specific characters (not found in Simplified)
TRADITIONAL_CHINESE_CHARS = set(
    "臺軟網際資訊記憶體處裡機學習數據視頻網絡繁體書寫語電腦運國際環節點開發實現圖書館醫學經濟"
    "學歷認證藝術設計營銷廣告財務會計銀審計稅務證券保險貸款匯款轉賬儲蓄業務員工程師應聘"
)

# Simplified Chinese specific characters (not found in Traditional)
SIMPLIFIED_CHINESE_CHARS = set(
    "台软网际资讯记忆体处里机学习数据视频网络简体书写语电脑运国际环节点开发实现图书馆医学经济"
    "学历认证艺术设计营销广告财务会计银审计税务证券保险贷款汇款转账储蓄业务员工程师应聘"
)

# Language-specific vocabulary markers for Traditional Chinese (Taiwan)
TRADITIONAL_CHINESE_VOCAB = [
    "軟體",  # software (TW: 軟體, CN: 软件)
    "網際網路",  # internet (TW: 網際網路, CN: 互联网)
    "資訊",  # information (TW: 資訊, CN: 信息)
    "記憶體",  # memory (TW: 記憶體, CN: 内存)
    "視訊",  # video (TW: 視訊, CN: 视频)
    "伺服器",  # server (TW: 伺服器, CN: 服务器)
    "程式",  # program (TW: 程式, CN: 程序)
]

# Simplified Chinese vocabulary markers
SIMPLIFIED_CHINESE_VOCAB = [
    "软件",  # software
    "互联网",  # internet
    "信息",  # information
    "内存",  # memory
    "视频",  # video
    "服务器",  # server
    "程序",  # program
]

SupportedLanguageCode = Literal[
    "en", "zh-TW", "zh-CN", "ar-MSA", "ar-Gulf", "ar-EG", "ar-Levant", "ar-Maghreb"
]


def _detect_arabic_dialect(text: str) -> str:
    """
    Identify Arabic dialect from text markers.

    Args:
        text: Arabic text to analyze

    Returns:
        Arabic dialect code (ar-MSA, ar-Gulf, ar-EG, ar-Levant, ar-Maghreb)
    """
    for dialect_code, markers in ARABIC_DIALECT_MARKERS.items():
        if any(marker in text for marker in markers):
            return dialect_code

    # Default to Modern Standard Arabic if no dialect markers found
    return "ar-MSA"


def _detect_chinese_variant(text: str) -> str:
    """
    Identify Traditional vs Simplified Chinese.

    Uses both character set analysis and vocabulary markers.

    Args:
        text: Chinese text to analyze

    Returns:
        Chinese variant code (zh-TW or zh-CN)
    """
    # Count Traditional vs Simplified specific characters
    trad_char_count = sum(1 for c in text if c in TRADITIONAL_CHINESE_CHARS)
    simp_char_count = sum(1 for c in text if c in SIMPLIFIED_CHINESE_CHARS)

    # Check for vocabulary markers
    trad_vocab_count = sum(1 for vocab in TRADITIONAL_CHINESE_VOCAB if vocab in text)
    simp_vocab_count = sum(1 for vocab in SIMPLIFIED_CHINESE_VOCAB if vocab in text)

    # Combine scores (vocabulary is weighted higher as it's more reliable)
    trad_score = trad_char_count + (trad_vocab_count * 3)
    simp_score = simp_char_count + (simp_vocab_count * 3)

    return "zh-TW" if trad_score >= simp_score else "zh-CN"


def detect_language(text: str) -> LanguageDetectionResult:
    """
    Detect the language and dialect of input text.

    Supports English, Traditional/Simplified Chinese, and Arabic dialects.

    Args:
        text: Text to analyze for language detection

    Returns:
        LanguageDetectionResult with language code, confidence, dialect, and writing direction
    """
    if not text or not text.strip():
        return LanguageDetectionResult(
            detected_language="English",
            language_code="en",
            confidence=0.5,
            dialect=None,
            writing_direction="ltr",
        )

    # Check for Arabic script (Unicode range: 0600-06FF)
    if re.search(r"[\u0600-\u06FF]", text):
        dialect_code = _detect_arabic_dialect(text)
        dialect_name = dialect_code.split("-")[1] if "-" in dialect_code else "MSA"

        return LanguageDetectionResult(
            detected_language="Arabic",
            language_code=dialect_code,
            confidence=0.95,
            dialect=dialect_name,
            writing_direction="rtl",
        )

    # Check for Chinese characters (CJK Unified Ideographs: 4E00-9FFF)
    if re.search(r"[\u4e00-\u9fff]", text):
        variant_code = _detect_chinese_variant(text)
        dialect_name = "Traditional" if variant_code == "zh-TW" else "Simplified"

        return LanguageDetectionResult(
            detected_language="Chinese",
            language_code=variant_code,
            confidence=0.95,
            dialect=dialect_name,
            writing_direction="ltr",
        )

    # Check for Japanese (Hiragana/Katakana) - not in PRD scope but useful for detection
    if re.search(r"[\u3040-\u309f\u30a0-\u30ff]", text):
        # If Japanese detected, still default to English as it's not supported
        pass

    # Check for Korean (Hangul) - not in PRD scope but useful for detection
    if re.search(r"[\uac00-\ud7af\u1100-\u11ff]", text):
        # If Korean detected, still default to English as it's not supported
        pass

    # Default to English
    return LanguageDetectionResult(
        detected_language="English",
        language_code="en",
        confidence=0.90,
        dialect=None,
        writing_direction="ltr",
    )


@function_tool
def language_detector_tool(text: str) -> dict:
    """
    Detect the language and dialect of the input text.

    This tool analyzes text to determine its language, supporting:
    - English
    - Traditional Chinese (Taiwan/Hong Kong)
    - Simplified Chinese (Mainland China/Singapore)
    - Arabic dialects (MSA, Gulf, Egyptian, Levantine, Maghrebi)

    Args:
        text: The text to analyze for language detection

    Returns:
        Dictionary with detected_language, language_code, confidence, dialect, and writing_direction
    """
    result = detect_language(text)
    return result.model_dump()
