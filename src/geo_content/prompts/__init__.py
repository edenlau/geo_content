"""
Prompts for GEO Content Platform agents.
"""

from geo_content.prompts.geo_writer import (
    GEO_WRITER_SYSTEM_PROMPT,
    get_writer_prompt,
)
from geo_content.prompts.language_specific import (
    LANGUAGE_PROMPTS,
    get_localized_system_prompt,
)

__all__ = [
    "GEO_WRITER_SYSTEM_PROMPT",
    "get_writer_prompt",
    "LANGUAGE_PROMPTS",
    "get_localized_system_prompt",
]
