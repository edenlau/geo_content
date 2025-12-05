"""
API routes for GEO Content Platform.

Supports both in-memory and SQLite job storage, local and S3 file uploads.
"""

import logging
import shutil
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response

from geo_content.api.dependencies import SettingsDep, WorkflowDep
from geo_content.agents.orchestrator import GEOContentWorkflow
from geo_content.config import settings
from geo_content.db import get_job_database
from geo_content.models import ContentGenerationRequest, ContentGenerationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["GEO Content"])

# In-memory job storage (fallback when SQLite not configured)
_job_storage: dict[str, dict[str, Any]] = {}

# Job history (last 10 completed jobs) - fallback
_job_history: deque[dict[str, Any]] = deque(maxlen=50)

# Local upload directory (fallback when S3 not configured)
UPLOAD_DIR = Path("/tmp/geo_content_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _get_s3_client():
    """Get boto3 S3 client if available."""
    if not settings.use_s3_uploads:
        return None
    try:
        import boto3
        return boto3.client("s3", region_name=settings.aws_region)
    except Exception as e:
        logger.warning(f"Could not create S3 client: {e}")
        return None


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns service status and version.
    """
    return {
        "status": "healthy",
        "service": "geo-content-platform",
        "version": "3.2.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
    }


@router.get("/health/deep")
async def deep_health_check() -> dict:
    """
    Deep health check endpoint.

    Verifies connectivity to all external services.
    """
    checks = {
        "api": "healthy",
        "database": "not_configured",
        "s3": "not_configured",
        "secrets_manager": "not_configured",
    }
    overall_status = "healthy"

    # Check SQLite database
    db = get_job_database()
    if db:
        try:
            # Simple query to verify database
            db.get_recent_jobs(limit=1)
            checks["database"] = "healthy"
        except Exception as e:
            checks["database"] = f"unhealthy: {e}"
            overall_status = "degraded"

    # Check S3 access
    if settings.use_s3_uploads:
        try:
            import boto3
            s3 = boto3.client("s3", region_name=settings.aws_region)
            s3.head_bucket(Bucket=settings.s3_bucket_uploads)
            checks["s3"] = "healthy"
        except Exception as e:
            checks["s3"] = f"unhealthy: {e}"
            overall_status = "degraded"

    # Check Secrets Manager (in production)
    if settings.is_production:
        try:
            import boto3
            sm = boto3.client("secretsmanager", region_name=settings.aws_region)
            sm.describe_secret(SecretId=settings.aws_secret_name)
            checks["secrets_manager"] = "healthy"
        except Exception as e:
            checks["secrets_manager"] = f"unhealthy: {e}"
            # Don't mark as degraded if secrets already loaded

    return {
        "status": overall_status,
        "service": "geo-content-platform",
        "version": "3.2.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
        "checks": checks,
    }


@router.post(
    "/generate",
    response_model=ContentGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate GEO-optimized content",
    description="""
    Generate content optimized for generative search engines.

    This endpoint:
    1. Detects the language of the input question
    2. Conducts research using web search and provided references
    3. Generates two content drafts in parallel (GPT-4.1-mini + Claude 3.5 Haiku)
    4. Evaluates and selects the best draft
    5. Returns the optimized content with GEO performance commentary
    """,
)
async def generate_content(
    request: ContentGenerationRequest,
    workflow: WorkflowDep,
) -> ContentGenerationResponse:
    """
    Generate GEO-optimized content.

    Args:
        request: Content generation request with client name, question, and references
        workflow: Injected workflow orchestrator

    Returns:
        ContentGenerationResponse with optimized content and analysis
    """
    try:
        logger.info(f"Generating content for client: {request.client_name}")
        logger.info(f"Target question: {request.target_question[:100]}...")

        response = await workflow.generate_content(request)

        logger.info(f"Content generated successfully. Job ID: {response.job_id}")
        logger.info(f"Selected draft: {response.selected_draft}, Score: {response.evaluation_score}")

        return response

    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}",
        )


@router.post(
    "/generate/async",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate content asynchronously",
    description="Start content generation in background and return job ID for polling.",
)
async def generate_content_async(
    request: ContentGenerationRequest,
    workflow: WorkflowDep,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Start asynchronous content generation.

    Returns immediately with a job ID that can be used to check status.
    """
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    created_at = datetime.utcnow().isoformat()

    # Use SQLite if configured, otherwise in-memory
    db = get_job_database()
    if db:
        db.create_job(job_id, request.model_dump())
    else:
        _job_storage[job_id] = {
            "status": "pending",
            "created_at": created_at,
            "request": request.model_dump(),
            "result": None,
            "error": None,
        }

    logger.info(
        f"[{job_id}] Async job created: client='{request.client_name}', "
        f"question='{request.target_question[:50]}...'"
    )

    # Add background task
    background_tasks.add_task(_run_generation, job_id, request, workflow)

    return {
        "job_id": job_id,
        "status": "pending",
        "status_url": f"/api/v1/jobs/{job_id}",
        "message": "Content generation started. Poll the status URL for results.",
    }


async def _run_generation(
    job_id: str,
    request: ContentGenerationRequest,
    workflow: GEOContentWorkflow,
) -> None:
    """Background task to run content generation."""
    db = get_job_database()

    try:
        logger.info(f"[{job_id}] Status transition: pending -> processing")

        if db:
            db.update_job_status(job_id, "processing")
        else:
            _job_storage[job_id]["status"] = "processing"

        response = await workflow.generate_content(request)

        if db:
            db.complete_job(job_id, response.model_dump())
        else:
            _job_storage[job_id]["status"] = "completed"
            _job_storage[job_id]["result"] = response.model_dump()
            _job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()

            # Add to job history
            _job_history.append({
                "job_id": job_id,
                "client_name": request.client_name,
                "target_question": request.target_question[:100] + ("..." if len(request.target_question) > 100 else ""),
                "evaluation_score": response.evaluation_score,
                "word_count": response.word_count,
                "completed_at": datetime.utcnow().isoformat(),
                "generation_time_ms": response.generation_time_ms,
            })

        logger.info(
            f"[{job_id}] Status transition: processing -> completed "
            f"(word_count={response.word_count}, score={response.evaluation_score:.1f}, "
            f"time={response.generation_time_ms}ms)"
        )

    except Exception as e:
        logger.error(f"[{job_id}] Status transition: processing -> failed ({e})")

        if db:
            db.fail_job(job_id, str(e))
        else:
            _job_storage[job_id]["status"] = "failed"
            _job_storage[job_id]["error"] = str(e)
            _job_storage[job_id]["completed_at"] = datetime.utcnow().isoformat()


@router.get(
    "/jobs/{job_id}",
    summary="Get job status",
    description="Check the status of an asynchronous content generation job.",
)
async def get_job_status(job_id: str) -> dict:
    """
    Get the status of a content generation job.
    """
    db = get_job_database()

    if db:
        job = db.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )
        return job
    else:
        if job_id not in _job_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        job = _job_storage[job_id]

        response = {
            "job_id": job_id,
            "status": job["status"],
            "created_at": job["created_at"],
        }

        if job["status"] == "completed":
            response["result"] = job["result"]
            response["completed_at"] = job.get("completed_at")
        elif job["status"] == "failed":
            response["error"] = job["error"]
            response["completed_at"] = job.get("completed_at")

        return response


@router.get(
    "/languages",
    summary="Get supported languages",
    description="List all supported languages and their codes.",
)
async def get_supported_languages() -> dict:
    """Get list of supported languages."""
    return {
        "languages": [
            {"code": "en", "name": "English", "variants": ["US", "UK", "Australian"]},
            {"code": "zh-TW", "name": "Traditional Chinese", "region": "Taiwan, Hong Kong"},
            {"code": "zh-CN", "name": "Simplified Chinese", "region": "Mainland China, Singapore"},
            {"code": "ar-MSA", "name": "Modern Standard Arabic", "region": "Formal/Written"},
            {"code": "ar-Gulf", "name": "Gulf Arabic", "region": "UAE, Saudi Arabia, Kuwait, Qatar, Bahrain, Oman"},
            {"code": "ar-EG", "name": "Egyptian Arabic", "region": "Egypt"},
            {"code": "ar-Levant", "name": "Levantine Arabic", "region": "Lebanon, Syria, Jordan, Palestine"},
            {"code": "ar-Maghreb", "name": "Maghrebi Arabic", "region": "Morocco, Algeria, Tunisia, Libya"},
        ],
        "auto_detection": True,
        "rtl_languages": ["ar-MSA", "ar-Gulf", "ar-EG", "ar-Levant", "ar-Maghreb"],
    }


@router.get(
    "/strategies",
    summary="Get GEO strategies",
    description="List GEO optimization strategies and their expected impact.",
)
async def get_geo_strategies() -> dict:
    """Get information about GEO optimization strategies."""
    return {
        "strategies": [
            {
                "name": "Statistics Addition",
                "visibility_boost": "+25-40%",
                "description": "Include verifiable statistics with sources and dates",
                "research": "Aggarwal et al. (2024) KDD '24",
            },
            {
                "name": "Quotation Addition",
                "visibility_boost": "+27-40%",
                "description": "Include expert quotations with full attribution",
                "research": "Aggarwal et al. (2024) KDD '24",
            },
            {
                "name": "Citation Addition",
                "visibility_boost": "+24-30%",
                "description": "Reference credible sources throughout",
                "research": "Aggarwal et al. (2024) KDD '24",
            },
            {
                "name": "Fluency Optimization",
                "visibility_boost": "+24-30%",
                "description": "Write in clear, natural language (Grade Level 8-10)",
                "research": "Aggarwal et al. (2024) KDD '24",
            },
            {
                "name": "Combined Strategies",
                "visibility_boost": "+35.8%",
                "description": "Fluency + Statistics combined effect",
                "research": "Aggarwal et al. (2024)",
            },
        ],
        "quality_threshold": 80,
        "max_iterations": 3,
    }


@router.post(
    "/upload",
    summary="Upload reference files",
    description="Upload PDF or DOCX files to use as reference material for content generation.",
)
async def upload_files(
    files: list[UploadFile] = File(..., description="PDF or DOCX files to upload"),
) -> dict:
    """
    Upload reference files for content generation.

    Supports both local storage and S3.
    """
    uploaded_paths = []
    errors = []
    s3_client = _get_s3_client()

    for file in files:
        # Validate file type
        filename = file.filename or "unknown"
        suffix = Path(filename).suffix.lower()

        if suffix not in [".pdf", ".docx", ".doc", ".txt", ".md"]:
            errors.append(f"{filename}: Unsupported file type. Use PDF, DOCX, TXT, or MD.")
            continue

        # Check file size (max 10MB)
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if size > 10 * 1024 * 1024:
            errors.append(f"{filename}: File too large (max 10MB)")
            continue

        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"

        try:
            if s3_client:
                # Upload to S3
                s3_key = f"uploads/{unique_filename}"
                s3_client.upload_fileobj(
                    file.file,
                    settings.s3_bucket_uploads,
                    s3_key,
                    ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
                )
                uploaded_paths.append(f"s3://{settings.s3_bucket_uploads}/{s3_key}")
                logger.info(f"File uploaded to S3: {filename} -> {s3_key}")
            else:
                # Save locally
                file_path = UPLOAD_DIR / unique_filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                uploaded_paths.append(str(file_path))
                logger.info(f"File uploaded locally: {filename} -> {file_path}")

        except Exception as e:
            errors.append(f"{filename}: Upload failed - {str(e)}")
            logger.error(f"File upload error for {filename}: {e}")

    return {
        "uploaded_files": uploaded_paths,
        "upload_count": len(uploaded_paths),
        "storage": "s3" if s3_client else "local",
        "errors": errors if errors else None,
    }


@router.get(
    "/history",
    summary="Get job history",
    description="Get the last 50 completed content generation jobs.",
)
async def get_job_history() -> dict:
    """
    Get the history of recent content generation jobs.
    """
    db = get_job_database()

    if db:
        jobs = db.get_recent_jobs(limit=50)
        return {
            "jobs": jobs,
            "total_count": len(jobs),
            "storage": "sqlite",
        }
    else:
        return {
            "jobs": list(_job_history),
            "total_count": len(_job_history),
            "storage": "memory",
        }


@router.get(
    "/jobs/{job_id}/download",
    summary="Download generated content",
    description="Download the generated content as a markdown file.",
)
async def download_content(job_id: str) -> Response:
    """
    Download the generated content for a completed job.
    """
    db = get_job_database()

    if db:
        job = db.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )
        if job["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job {job_id} is not completed (status: {job['status']})",
            )
        result = job.get("result", {})
        request = job.get("request", {})
        completed_at = job.get("completed_at", "Unknown")
    else:
        if job_id not in _job_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        job = _job_storage[job_id]

        if job["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job {job_id} is not completed (status: {job['status']})",
            )

        result = job["result"]
        request = job["request"]
        completed_at = job.get("completed_at", "Unknown")

    # Create markdown content
    md_content = f"""# {result.get('geo_commentary', {}).get('summary', {}).get('overall_assessment', 'Generated Content')}

**Client:** {request.get('client_name', 'Unknown')}
**Target Question:** {request.get('target_question', 'Unknown')}
**Generated:** {completed_at}
**Evaluation Score:** {result.get('evaluation_score', 0):.1f}/100
**Word Count:** {result.get('word_count', 0)}
**Language:** {result.get('detected_language', 'Unknown')} ({result.get('language_code', 'Unknown')})

---

## Generated Content

{result.get('content', '')}

---

## GEO Analysis

- **Statistics Count:** {result.get('geo_analysis', {}).get('statistics_count', 0)}
- **Citations Count:** {result.get('geo_analysis', {}).get('citations_count', 0)}
- **Quotations Count:** {result.get('geo_analysis', {}).get('quotations_count', 0)}
- **Fluency Score:** {result.get('geo_analysis', {}).get('fluency_score', 0):.1f}
- **E-E-A-T Score:** {result.get('geo_analysis', {}).get('eeat_score', 0):.1f}/10

## Key Strengths

{chr(10).join(f'- {s}' for s in result.get('geo_commentary', {}).get('key_strengths', []))}

## Suggestions for Improvement

{chr(10).join(f'- {s}' for s in result.get('geo_commentary', {}).get('suggestions', []))}

---

*Generated by Tocanan GEO Content Generator*
*Job ID: {job_id}*
"""

    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="geo_content_{job_id}.md"',
        },
    )
