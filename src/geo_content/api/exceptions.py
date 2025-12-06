"""
Custom exceptions for GEO Content Platform API.

Provides structured error handling with error codes and user-friendly messages.
"""

from fastapi import HTTPException, status


class GEOContentError(Exception):
    """Base exception for GEO Content Platform errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    user_message: str = "An unexpected error occurred"

    def __init__(
        self,
        detail: str | None = None,
        user_message: str | None = None,
    ):
        self.detail = detail or self.user_message
        if user_message:
            self.user_message = user_message
        super().__init__(self.detail)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "error_code": self.error_code,
                "message": self.user_message,
                "detail": self.detail,
            },
        )


class ExternalServiceError(GEOContentError):
    """Error when an external service (LLM, search) fails."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "EXTERNAL_SERVICE_ERROR"
    user_message = "An external service is temporarily unavailable"

    def __init__(
        self,
        service_name: str,
        detail: str | None = None,
    ):
        self.service_name = service_name
        super().__init__(
            detail=detail or f"Service '{service_name}' is unavailable",
            user_message=f"The {service_name} service is temporarily unavailable. Please try again later.",
        )


class ExternalServiceTimeoutError(ExternalServiceError):
    """Error when an external service times out."""

    error_code = "EXTERNAL_SERVICE_TIMEOUT"

    def __init__(self, service_name: str, timeout_seconds: int):
        super().__init__(
            service_name=service_name,
            detail=f"Service '{service_name}' timed out after {timeout_seconds}s",
        )
        self.user_message = f"The {service_name} service took too long to respond. Please try again."


class ContentGenerationError(GEOContentError):
    """Error during content generation workflow."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "CONTENT_GENERATION_ERROR"
    user_message = "Content generation failed"


class ResearchError(ContentGenerationError):
    """Error during the research phase."""

    error_code = "RESEARCH_ERROR"
    user_message = "Research phase failed. Please check your references and try again."


class EvaluationError(ContentGenerationError):
    """Error during content evaluation."""

    error_code = "EVALUATION_ERROR"
    user_message = "Content evaluation failed. Please try again."


class ValidationError(GEOContentError):
    """Error when request validation fails."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"
    user_message = "Invalid request data"


class RateLimitError(GEOContentError):
    """Error when rate limit is exceeded."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"
    user_message = "Too many requests. Please wait before trying again."

    def __init__(self, retry_after: int | None = None):
        self.retry_after = retry_after
        detail = f"Rate limit exceeded. Retry after {retry_after}s" if retry_after else "Rate limit exceeded"
        super().__init__(detail=detail)


class JobNotFoundError(GEOContentError):
    """Error when a job is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "JOB_NOT_FOUND"
    user_message = "Job not found"

    def __init__(self, job_id: str):
        self.job_id = job_id
        super().__init__(
            detail=f"Job '{job_id}' not found",
            user_message=f"The requested job '{job_id}' was not found.",
        )


class JobQueueFullError(GEOContentError):
    """Error when the job queue is full."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "JOB_QUEUE_FULL"
    user_message = "The system is currently at capacity. Please try again later."


class DatabaseError(GEOContentError):
    """Error when database operations fail."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "DATABASE_ERROR"
    user_message = "A database error occurred. Please try again."


class FileUploadError(GEOContentError):
    """Error during file upload."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "FILE_UPLOAD_ERROR"
    user_message = "File upload failed"

    def __init__(self, filename: str, reason: str):
        self.filename = filename
        super().__init__(
            detail=f"Failed to upload '{filename}': {reason}",
            user_message=f"Could not upload file '{filename}'. {reason}",
        )


class CircuitBreakerOpenError(ExternalServiceError):
    """Error when circuit breaker is open."""

    error_code = "CIRCUIT_BREAKER_OPEN"

    def __init__(self, service_name: str):
        super().__init__(
            service_name=service_name,
            detail=f"Circuit breaker open for service '{service_name}'",
        )
        self.user_message = f"The {service_name} service is temporarily disabled due to repeated failures. Please try again later."
