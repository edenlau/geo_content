"""
Base agent configuration for GEO Content Platform.

Provides common configuration and utilities for all agents.
"""

import logging
from typing import Any

from agents import Agent

from geo_content.config import settings

logger = logging.getLogger(__name__)


def get_model_config(agent_type: str) -> dict[str, Any]:
    """
    Get model configuration for a specific agent type.

    Args:
        agent_type: Type of agent ("writer_a", "writer_b", "evaluator", "research")

    Returns:
        Dictionary with model configuration
    """
    configs = {
        "research": {
            "model": settings.openai_model_writer,  # GPT-4.1-mini for research
            "temperature": 0.3,
            "max_tokens": 4096,
        },
        "writer_a": {
            "model": settings.openai_model_writer,  # GPT-4.1-mini
            "temperature": 0.7,
            "max_tokens": 8192,
        },
        "writer_b": {
            # Claude model - handled separately via Anthropic SDK
            "model": settings.anthropic_model_writer,  # claude-3-5-haiku
            "temperature": 0.7,
            "max_tokens": 8192,
        },
        "evaluator": {
            "model": settings.openai_model_evaluator,  # GPT-4.1
            "temperature": 0.2,
            "max_tokens": 4096,
        },
    }

    return configs.get(agent_type, configs["research"])


def create_agent(
    name: str,
    instructions: str,
    tools: list | None = None,
    handoffs: list | None = None,
    model: str | None = None,
    **kwargs,
) -> Agent:
    """
    Create an agent with standard configuration.

    Args:
        name: Agent name
        instructions: System instructions for the agent
        tools: List of tools available to the agent
        handoffs: List of agents this agent can hand off to
        model: Model to use (defaults to GPT-4.1-mini)
        **kwargs: Additional agent configuration

    Returns:
        Configured Agent instance
    """
    agent_config = {
        "name": name,
        "instructions": instructions,
        "model": model or settings.openai_model_writer,
    }

    if tools:
        agent_config["tools"] = tools

    if handoffs:
        agent_config["handoffs"] = handoffs

    # Merge additional configuration
    agent_config.update(kwargs)

    return Agent(**agent_config)


# Common prompt components
COMMON_INSTRUCTIONS = """
## IMPORTANT GUIDELINES

1. **Accuracy First**: Only include information that is factually accurate and verifiable.
2. **Source Attribution**: Always attribute statistics, quotes, and facts to their sources.
3. **Language Matching**: Generate content in the SAME language as the input question.
4. **Professional Tone**: Maintain a professional, authoritative tone throughout.
5. **E-E-A-T Signals**: Incorporate Experience, Expertise, Authoritativeness, and Trust signals.
"""

GEO_STRATEGY_SUMMARY = """
## GEO OPTIMIZATION STRATEGIES (Research-Backed)

Based on peer-reviewed research (Aggarwal et al. 2024, Luttgenau et al. 2025):

| Strategy | Expected Visibility Boost |
|----------|--------------------------|
| Statistics Addition | +25-40% |
| Quotation Addition | +27-40% |
| Citation Addition | +24-30% |
| Fluency Optimization | +24-30% |
| Combined Strategies | +35.8% (Fluency + Statistics) |

Apply these strategies to maximize visibility in generative search engines.
"""
