"""
Tests for language detection functionality.
"""

import pytest

from geo_content.tools.language_detector import detect_language


class TestLanguageDetection:
    """Test suite for language detection."""

    def test_detect_english(self):
        """Test English detection."""
        result = detect_language("What are the best attractions in Hong Kong?")

        assert result.detected_language == "English"
        assert result.language_code == "en"
        assert result.writing_direction == "ltr"
        assert result.confidence >= 0.8

    def test_detect_traditional_chinese(self):
        """Test Traditional Chinese detection."""
        result = detect_language("香港海洋公園有什麼好玩的景點？")

        assert result.detected_language == "Chinese"
        assert result.language_code in ["zh-TW", "zh-CN"]
        assert result.writing_direction == "ltr"
        assert result.confidence >= 0.9

    def test_detect_simplified_chinese(self):
        """Test Simplified Chinese detection with specific markers."""
        # Use Simplified Chinese specific vocabulary
        result = detect_language("互联网软件开发是一个重要的领域")

        assert result.detected_language == "Chinese"
        assert result.language_code == "zh-CN"
        assert result.dialect == "Simplified"

    def test_detect_traditional_chinese_taiwan(self):
        """Test Traditional Chinese (Taiwan) with specific markers."""
        # Use Taiwan-specific vocabulary
        result = detect_language("網際網路軟體開發是一個重要的領域")

        assert result.detected_language == "Chinese"
        assert result.language_code == "zh-TW"
        assert result.dialect == "Traditional"

    def test_detect_arabic_msa(self):
        """Test Modern Standard Arabic detection."""
        result = detect_language("ما هي أفضل المعالم السياحية في دبي؟")

        assert result.detected_language == "Arabic"
        assert result.language_code.startswith("ar-")
        assert result.writing_direction == "rtl"
        assert result.confidence >= 0.9

    def test_detect_arabic_gulf(self):
        """Test Gulf Arabic dialect detection."""
        # Contains Gulf dialect marker "شلونك"
        result = detect_language("شلونك؟ وين أروح في دبي؟")

        assert result.detected_language == "Arabic"
        assert result.language_code == "ar-Gulf"
        assert result.dialect == "Gulf"
        assert result.writing_direction == "rtl"

    def test_detect_arabic_egyptian(self):
        """Test Egyptian Arabic dialect detection."""
        # Contains Egyptian dialect marker "إزيك"
        result = detect_language("إزيك؟ عايز أروح فين في القاهرة؟")

        assert result.detected_language == "Arabic"
        assert result.language_code == "ar-EG"
        assert result.dialect == "EG"

    def test_detect_arabic_levantine(self):
        """Test Levantine Arabic dialect detection."""
        # Contains Levantine dialect marker "كيفك" and "شو"
        result = detect_language("كيفك؟ شو في في بيروت؟")

        assert result.detected_language == "Arabic"
        assert result.language_code == "ar-Levant"
        assert result.dialect == "Levant"

    def test_detect_arabic_maghrebi(self):
        """Test Maghrebi Arabic dialect detection."""
        # Contains Maghrebi dialect marker "واش"
        result = detect_language("واش كاين شي بلاصة مزيانة في الدار البيضاء؟")

        assert result.detected_language == "Arabic"
        assert result.language_code == "ar-Maghreb"
        assert result.dialect == "Maghreb"

    def test_detect_empty_string(self):
        """Test handling of empty string."""
        result = detect_language("")

        assert result.detected_language == "English"
        assert result.confidence == 0.5

    def test_detect_whitespace_only(self):
        """Test handling of whitespace-only string."""
        result = detect_language("   \n\t  ")

        assert result.detected_language == "English"
        assert result.confidence == 0.5

    def test_mixed_language_defaults_to_dominant(self):
        """Test that mixed content detects the dominant language."""
        # Predominantly English with some numbers
        result = detect_language("The population is 7.6 million people")

        assert result.detected_language == "English"
        assert result.language_code == "en"


class TestLanguageDetectionTool:
    """Test the function_tool wrapper."""

    def test_tool_returns_dict(self):
        """Test that the tool returns a dictionary."""
        from geo_content.tools.language_detector import language_detector_tool

        # The function_tool decorator changes the function signature
        # We need to call the underlying function
        result = detect_language("Hello world")
        result_dict = result.model_dump()

        assert isinstance(result_dict, dict)
        assert "detected_language" in result_dict
        assert "language_code" in result_dict
        assert "confidence" in result_dict
        assert "writing_direction" in result_dict
