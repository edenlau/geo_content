"""
Configuration management for GEO Content Platform.

Uses Pydantic Settings for environment variable management with validation.
Supports AWS Secrets Manager for production deployments.
"""

import json
import logging
import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def get_aws_secrets(secret_name: str, region: str = "ap-southeast-1") -> dict | None:
    """
    Fetch secrets from AWS Secrets Manager.

    Args:
        secret_name: Name of the secret in Secrets Manager
        region: AWS region

    Returns:
        Dictionary of secrets or None if not available
    """
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ImportError:
        logger.debug("boto3 not available, skipping AWS Secrets Manager")
        return None
    except NoCredentialsError:
        logger.debug("No AWS credentials found, using environment variables")
        return None
    except ClientError as e:
        logger.debug(f"Could not fetch secret {secret_name}: {e}")
        return None
    except Exception as e:
        logger.debug(f"Error fetching AWS secrets: {e}")
        return None


def _load_secrets_to_env():
    """Load secrets from AWS Secrets Manager into environment variables."""
    # Only attempt if ENVIRONMENT is production or USE_AWS_SECRETS is set
    if os.environ.get("ENVIRONMENT") == "production" or os.environ.get("USE_AWS_SECRETS"):
        secrets = get_aws_secrets(
            secret_name=os.environ.get("AWS_SECRET_NAME", "geo-content/api-keys"),
            region=os.environ.get("AWS_REGION", "ap-southeast-1"),
        )
        if secrets:
            logger.info("Loaded API keys from AWS Secrets Manager")
            for key, value in secrets.items():
                if key not in os.environ:  # Don't override existing env vars
                    os.environ[key] = value


# Load secrets before Settings class is instantiated
_load_secrets_to_env()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # OpenAI Configuration
    # -------------------------------------------------------------------------
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for GPT models",
    )
    openai_model_writer: str = Field(
        default="gpt-5",
        description="OpenAI model for Writer Agent A and Research Agent",
    )
    openai_model_evaluator: str = Field(
        default="o4-mini",
        description="OpenAI model for Evaluator Agent (reasoning optimized)",
    )

    # -------------------------------------------------------------------------
    # Anthropic Configuration
    # -------------------------------------------------------------------------
    anthropic_api_key: str = Field(
        ...,
        description="Anthropic API key for Claude models",
    )
    anthropic_model_writer: str = Field(
        default="claude-sonnet-4-5-20241022",
        description="Anthropic model for Writer Agent B (Sonnet 4.5)",
    )

    # -------------------------------------------------------------------------
    # Web Search Configuration
    # -------------------------------------------------------------------------
    tavily_api_key: str = Field(
        default="",
        description="Tavily API key for web search",
    )

    # -------------------------------------------------------------------------
    # Perplexity AI Configuration (for grounded quote search)
    # -------------------------------------------------------------------------
    perplexity_api_key: str = Field(
        default="",
        description="Perplexity AI API key for grounded quote search",
    )
    perplexity_model: str = Field(
        default="llama-3.1-sonar-large-128k-online",
        description="Perplexity model for quote search (online model with citations)",
    )

    # -------------------------------------------------------------------------
    # Tracing Configuration
    # -------------------------------------------------------------------------
    openai_agents_disable_tracing: bool = Field(
        default=False,
        description="Set to True to disable OpenAI Agents tracing",
    )

    # -------------------------------------------------------------------------
    # Application Configuration
    # -------------------------------------------------------------------------
    max_iterations: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum evaluation iterations",
    )
    quality_threshold: int = Field(
        default=80,
        ge=0,
        le=100,
        description="Minimum quality score threshold (0-100)",
    )
    eeat_threshold: int = Field(
        default=6,
        ge=1,
        le=10,
        description="Minimum E-E-A-T score threshold (1-10). Below this triggers additional research.",
    )
    max_research_iterations: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum additional research iterations for low E-E-A-T scores",
    )
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment",
    )

    # -------------------------------------------------------------------------
    # API Server Configuration
    # -------------------------------------------------------------------------
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
    )
    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="API server port",
    )
    cors_origins: str = Field(
        default="https://geoaction.tocanan.ai,http://localhost:3000,http://localhost:8080",
        description="Comma-separated CORS allowed origins (production first)",
    )

    # -------------------------------------------------------------------------
    # AWS Configuration
    # -------------------------------------------------------------------------
    aws_region: str = Field(
        default="ap-southeast-1",
        description="AWS region for S3 and Secrets Manager",
    )
    s3_bucket_uploads: str = Field(
        default="",
        description="S3 bucket for file uploads (empty = use local storage)",
    )
    aws_secret_name: str = Field(
        default="geo-content/api-keys",
        description="AWS Secrets Manager secret name",
    )

    # -------------------------------------------------------------------------
    # Database Configuration
    # -------------------------------------------------------------------------
    db_path: str = Field(
        default="",
        description="Path to SQLite database file (empty = in-memory storage)",
    )

    # -------------------------------------------------------------------------
    # Resilience Configuration
    # -------------------------------------------------------------------------
    llm_timeout_seconds: int = Field(
        default=120,
        ge=10,
        le=600,
        description="Timeout for LLM API calls in seconds",
    )
    search_timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout for search API calls in seconds",
    )
    retry_max_attempts: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum retry attempts for external API calls",
    )
    retry_min_wait_seconds: int = Field(
        default=2,
        ge=1,
        le=30,
        description="Minimum wait time between retries in seconds",
    )
    retry_max_wait_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Maximum wait time between retries in seconds",
    )

    # -------------------------------------------------------------------------
    # Rate Limiting Configuration
    # -------------------------------------------------------------------------
    rate_limit_generate: str = Field(
        default="10/minute",
        description="Rate limit for content generation endpoints",
    )
    rate_limit_default: str = Field(
        default="60/minute",
        description="Default rate limit for other endpoints",
    )
    max_concurrent_jobs: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum concurrent background jobs",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def use_s3_uploads(self) -> bool:
        """Check if S3 should be used for uploads."""
        return bool(self.s3_bucket_uploads)

    @property
    def use_sqlite(self) -> bool:
        """Check if SQLite should be used for job storage."""
        return bool(self.db_path)


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Global settings instance for easy access
settings = get_settings()
