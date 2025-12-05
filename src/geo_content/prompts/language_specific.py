"""
Language-specific prompt additions for multilingual content generation.

Supports: English, Traditional Chinese, Simplified Chinese, and Arabic dialects.
"""

LANGUAGE_PROMPTS = {
    "en": """
### LANGUAGE: English
Write in fluent, natural English. Use American English spelling conventions
unless the context suggests British English is more appropriate.
Ensure clarity and professionalism throughout.
""",
    "zh-TW": """
### 語言：繁體中文（台灣）
使用繁體中文撰寫內容。採用台灣地區常用的詞彙和表達方式。
例如：使用「軟體」而非「软件」，「網際網路」而非「互联网」。
確保文章流暢自然，符合繁體中文閱讀習慣。

注意事項：
- 使用正式但親切的語調
- 適當使用台灣常見的專業術語
- 數字使用阿拉伯數字
- 保持段落簡潔明瞭
""",
    "zh-CN": """
### 语言：简体中文（中国大陆）
使用简体中文撰写内容。采用中国大陆地区常用的词汇和表达方式。
例如：使用「软件」而非「軟體」，「互联网」而非「網際網路」。
确保文章流畅自然，符合简体中文阅读习惯。

注意事项：
- 使用正式但易读的语调
- 适当使用大陆常见的专业术语
- 数字使用阿拉伯数字
- 保持段落简洁明了
""",
    "ar-MSA": """
### اللغة: العربية الفصحى الحديثة
اكتب بالعربية الفصحى الحديثة. استخدم أسلوباً رسمياً ومهنياً.
تأكد من صحة القواعد النحوية والإملائية.
اجعل المحتوى واضحاً وسهل القراءة.

ملاحظات:
- استخدم لغة رسمية ومهنية
- تأكد من صحة التشكيل عند الضرورة
- استخدم الأرقام العربية أو الهندية حسب السياق
- حافظ على تدفق الأفكار بشكل منطقي
""",
    "ar-Gulf": """
### اللغة: اللهجة الخليجية
اكتب باللهجة الخليجية مع الحفاظ على المهنية.
استخدم المصطلحات والتعبيرات الشائعة في دول الخليج العربي.
اجعل المحتوى مناسباً للجمهور في الإمارات والسعودية والكويت وقطر والبحرين وعمان.

ملاحظات:
- استخدم تعبيرات خليجية مألوفة عند المناسب
- حافظ على المهنية مع اللمسة المحلية
- استخدم الأرقام الهندية أو العربية
- اجعل النص واضحاً ومباشراً
""",
    "ar-EG": """
### اللغة: اللهجة المصرية
اكتب باللهجة المصرية مع الحفاظ على المهنية.
استخدم المصطلحات والتعبيرات الشائعة في مصر.
اجعل المحتوى واضحاً ومفهوماً للجمهور المصري.

ملاحظات:
- استخدم تعبيرات مصرية مألوفة عند المناسب
- حافظ على أسلوب ودي ومهني
- استخدم الأرقام العربية
- اجعل المحتوى سهل القراءة
""",
    "ar-Levant": """
### اللغة: اللهجة الشامية
اكتب باللهجة الشامية مع الحفاظ على المهنية.
استخدم المصطلحات والتعبيرات الشائعة في لبنان وسوريا والأردن وفلسطين.
اجعل المحتوى مناسباً لجمهور بلاد الشام.

ملاحظات:
- استخدم تعبيرات شامية مألوفة عند المناسب
- حافظ على أسلوب راقي ومهني
- استخدم الأرقام العربية
- اجعل النص سلساً وواضحاً
""",
    "ar-Maghreb": """
### اللغة: اللهجة المغاربية
اكتب باللهجة المغاربية مع الحفاظ على المهنية.
استخدم المصطلحات والتعبيرات الشائعة في المغرب والجزائر وتونس وليبيا.
اجعل المحتوى مفهوماً لجمهور شمال أفريقيا.

ملاحظات:
- استخدم تعبيرات مغاربية مألوفة عند المناسب
- يمكن المزج بين الفصحى واللهجة حسب السياق
- استخدم الأرقام العربية أو اللاتينية
- اجعل المحتوى واضحاً ومباشراً
""",
}


def get_localized_system_prompt(base_prompt: str, language_code: str) -> str:
    """
    Combine base GEO prompt with language-specific instructions.

    Args:
        base_prompt: The base system prompt
        language_code: Language code (e.g., 'en', 'zh-TW', 'ar-Gulf')

    Returns:
        Combined prompt with language instructions
    """
    # Get language-specific instructions, default to English
    language_instruction = LANGUAGE_PROMPTS.get(language_code, LANGUAGE_PROMPTS["en"])

    return f"""{base_prompt}

{language_instruction}

### CRITICAL LANGUAGE REQUIREMENT
The ENTIRE output MUST be written in the same language as the input question.
Do NOT mix languages. Maintain consistent language throughout the article.
Language code for this request: {language_code}
"""


def get_language_name(language_code: str) -> str:
    """
    Get human-readable language name from code.

    Args:
        language_code: Language code

    Returns:
        Human-readable language name
    """
    language_names = {
        "en": "English",
        "zh-TW": "Traditional Chinese (Taiwan)",
        "zh-CN": "Simplified Chinese (Mainland China)",
        "ar-MSA": "Modern Standard Arabic",
        "ar-Gulf": "Gulf Arabic",
        "ar-EG": "Egyptian Arabic",
        "ar-Levant": "Levantine Arabic",
        "ar-Maghreb": "Maghrebi Arabic",
    }
    return language_names.get(language_code, "English")
