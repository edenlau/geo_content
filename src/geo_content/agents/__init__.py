"""
Multi-agent system for GEO Content Platform.
"""

from geo_content.agents.base import create_agent, get_model_config
from geo_content.agents.evaluator_agent import EvaluatorAgent, evaluator_agent
from geo_content.agents.orchestrator import GEOContentWorkflow, generate_geo_content, geo_workflow
from geo_content.agents.research_agent import ResearchAgent, research_agent
from geo_content.agents.writer_agent_a import WriterAgentA, writer_agent_a
from geo_content.agents.writer_agent_b import WriterAgentB, writer_agent_b

__all__ = [
    # Base
    "create_agent",
    "get_model_config",
    # Research
    "ResearchAgent",
    "research_agent",
    # Writers
    "WriterAgentA",
    "writer_agent_a",
    "WriterAgentB",
    "writer_agent_b",
    # Evaluator
    "EvaluatorAgent",
    "evaluator_agent",
    # Orchestrator
    "GEOContentWorkflow",
    "geo_workflow",
    "generate_geo_content",
]
