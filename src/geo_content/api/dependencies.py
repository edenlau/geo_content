"""
FastAPI dependencies for GEO Content Platform.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from geo_content.agents.orchestrator import GEOContentWorkflow, geo_workflow
from geo_content.config import Settings, get_settings


def get_workflow() -> GEOContentWorkflow:
    """Get the GEO content workflow instance."""
    return geo_workflow


# Type aliases for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
WorkflowDep = Annotated[GEOContentWorkflow, Depends(get_workflow)]
