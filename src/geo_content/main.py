"""
FastAPI application entry point for GEO Content Platform.
"""

import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from geo_content.api.routes import router
from geo_content.config import settings

# Export API keys to environment for OpenAI Agents SDK
# The SDK reads directly from os.environ, not from Pydantic settings
os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
os.environ.setdefault("ANTHROPIC_API_KEY", settings.anthropic_api_key)


def setup_logging() -> logging.Logger:
    """
    Configure logging with both console and file handlers.

    Returns:
        Logger instance for the main module.
    """
    # Determine log level based on environment
    log_level = logging.INFO if settings.is_development else logging.WARNING
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates on reload
    root_logger.handlers.clear()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    # Create logs directory relative to project root
    project_root = Path(__file__).parent.parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "geo_content.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB per file
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)  # Always log INFO to file
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    return logging.getLogger(__name__)


# Configure logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting GEO Content Platform...")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log file: logs/geo_content.log")
    logger.info(f"Writer A Model: {settings.openai_model_writer}")
    logger.info(f"Writer B Model: {settings.anthropic_model_writer}")
    logger.info(f"Evaluator Model: {settings.openai_model_evaluator}")
    logger.info(f"Quality Threshold: {settings.quality_threshold}")
    logger.info(f"E-E-A-T Threshold: {settings.eeat_threshold}")
    logger.info(f"Max Iterations: {settings.max_iterations}")
    logger.info(f"Max Research Iterations: {settings.max_research_iterations}")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Shutting down GEO Content Platform...")


# Create FastAPI application
app = FastAPI(
    title="GEO Content Optimization Platform",
    description="""
    Multi-Agent GEO Content Optimization Platform

    This platform generates content optimized for visibility in generative search engines
    (ChatGPT, Perplexity AI, Google AI Overviews, Claude).

    ## Features

    - **Automatic Language Detection**: Supports English, Chinese (Traditional/Simplified),
      and Arabic dialects
    - **Dual-LLM Generation**: Parallel content creation using GPT-4.1 and Claude Sonnet 4
    - **Research-Backed Optimization**: Evidence-based GEO strategies with 30-40% visibility improvement
    - **Full Observability**: OpenAI Trace integration for complete workflow tracking
    - **GEO Performance Commentary**: Detailed explanation of optimization decisions

    ## Research Foundation

    - Aggarwal et al. (2024) KDD '24: GEO strategies boost visibility up to 40%
    - Luttgenau et al. (2025): Domain-specific optimization achieves 30.96% visibility gain

    ## API Documentation

    - **POST /api/v1/generate**: Generate GEO-optimized content (synchronous)
    - **POST /api/v1/generate/async**: Start async generation (returns job ID)
    - **GET /api/v1/jobs/{job_id}**: Check async job status
    - **GET /api/v1/languages**: List supported languages
    - **GET /api/v1/strategies**: List GEO optimization strategies
    """,
    version="3.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "GEO Content Optimization Platform",
        "version": "3.2.0",
        "documentation": "/docs",
        "api_base": "/api/v1",
        "endpoints": {
            "generate": "POST /api/v1/generate",
            "generate_async": "POST /api/v1/generate/async",
            "job_status": "GET /api/v1/jobs/{job_id}",
            "health": "GET /api/v1/health",
            "languages": "GET /api/v1/languages",
            "strategies": "GET /api/v1/strategies",
        },
    }


def run_server():
    """Run the server programmatically."""
    import uvicorn

    uvicorn.run(
        "geo_content.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
    )


if __name__ == "__main__":
    run_server()
