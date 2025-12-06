"""
SQLite database management for GEO Content Platform.

Provides persistent storage for jobs with automatic cleanup.
"""

import json
import logging
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Thread-local storage for connections
_local = threading.local()


class JobDatabase:
    """
    SQLite-based job storage with automatic cleanup.

    Maintains a maximum number of jobs and provides CRUD operations.
    """

    def __init__(self, db_path: str, max_jobs: int = 50):
        """
        Initialize the job database.

        Args:
            db_path: Path to SQLite database file
            max_jobs: Maximum number of jobs to retain
        """
        self.db_path = db_path
        self.max_jobs = max_jobs

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database schema
        self._init_schema()
        logger.info(f"JobDatabase initialized: {db_path} (max_jobs={max_jobs})")

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection with optimized settings."""
        if not hasattr(_local, "connection") or _local.connection is None:
            _local.connection = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # Wait up to 30s for locks
                check_same_thread=False,
            )
            _local.connection.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            _local.connection.execute("PRAGMA journal_mode=WAL")
            # Set busy timeout to wait for locks instead of failing immediately
            _local.connection.execute("PRAGMA busy_timeout=5000")
            # Enable foreign keys
            _local.connection.execute("PRAGMA foreign_keys=ON")
            logger.debug("Created new database connection for thread")
        return _local.connection

    def close_connection(self):
        """Close the thread-local database connection."""
        if hasattr(_local, "connection") and _local.connection is not None:
            try:
                _local.connection.close()
                logger.debug("Closed database connection for thread")
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")
            finally:
                _local.connection = None

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            with self._cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    @contextmanager
    def _cursor(self):
        """Context manager for database cursor with commit/rollback."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def _init_schema(self):
        """Create database tables if they don't exist."""
        with self._cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL DEFAULT 'pending',
                    request_json TEXT,
                    result_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)
            """)

    def create_job(self, job_id: str, request: dict) -> dict:
        """
        Create a new job.

        Args:
            job_id: Unique job identifier
            request: Job request data

        Returns:
            Created job record
        """
        created_at = datetime.utcnow().isoformat()
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO jobs (job_id, status, request_json, created_at)
                VALUES (?, 'pending', ?, ?)
                """,
                (job_id, json.dumps(request, cls=DateTimeEncoder), created_at),
            )

        # Cleanup old jobs if needed
        self._cleanup_old_jobs()

        return {
            "job_id": job_id,
            "status": "pending",
            "request": request,
            "created_at": created_at,
        }

    def get_job(self, job_id: str) -> dict | None:
        """
        Get a job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job record or None if not found
        """
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_dict(row)

    def update_job_status(self, job_id: str, status: str):
        """
        Update job status.

        Args:
            job_id: Job identifier
            status: New status
        """
        with self._cursor() as cursor:
            cursor.execute(
                "UPDATE jobs SET status = ? WHERE job_id = ?",
                (status, job_id),
            )

    def complete_job(self, job_id: str, result: dict):
        """
        Mark job as completed with result.

        Args:
            job_id: Job identifier
            result: Job result data
        """
        completed_at = datetime.utcnow().isoformat()
        with self._cursor() as cursor:
            cursor.execute(
                """
                UPDATE jobs
                SET status = 'completed', result_json = ?, completed_at = ?
                WHERE job_id = ?
                """,
                (json.dumps(result, cls=DateTimeEncoder), completed_at, job_id),
            )

    def fail_job(self, job_id: str, error: str):
        """
        Mark job as failed with error.

        Args:
            job_id: Job identifier
            error: Error message
        """
        completed_at = datetime.utcnow().isoformat()
        with self._cursor() as cursor:
            cursor.execute(
                """
                UPDATE jobs
                SET status = 'failed', error = ?, completed_at = ?
                WHERE job_id = ?
                """,
                (error, completed_at, job_id),
            )

    def get_recent_jobs(self, limit: int = 10) -> list[dict]:
        """
        Get recent completed jobs.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of recent job records
        """
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT job_id, status, request_json, result_json, created_at, completed_at
                FROM jobs
                WHERE status = 'completed'
                ORDER BY completed_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()

        return [self._row_to_summary(row) for row in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """Convert database row to dictionary."""
        result = {
            "job_id": row["job_id"],
            "status": row["status"],
            "created_at": row["created_at"],
        }

        if row["request_json"]:
            result["request"] = json.loads(row["request_json"])

        if row["result_json"]:
            result["result"] = json.loads(row["result_json"])

        if row["error"]:
            result["error"] = row["error"]

        if row["completed_at"]:
            result["completed_at"] = row["completed_at"]

        return result

    def _row_to_summary(self, row: sqlite3.Row) -> dict:
        """Convert database row to summary dictionary for history."""
        request = json.loads(row["request_json"]) if row["request_json"] else {}
        result = json.loads(row["result_json"]) if row["result_json"] else {}

        target_question = request.get("target_question", "")
        if len(target_question) > 100:
            target_question = target_question[:100] + "..."

        return {
            "job_id": row["job_id"],
            "client_name": request.get("client_name", "Unknown"),
            "target_question": target_question,
            "evaluation_score": result.get("evaluation_score", 0),
            "word_count": result.get("word_count", 0),
            "completed_at": row["completed_at"],
            "generation_time_ms": result.get("generation_time_ms", 0),
        }

    def _cleanup_old_jobs(self):
        """Remove old jobs exceeding max_jobs limit."""
        with self._cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM jobs")
            count = cursor.fetchone()["count"]

            if count > self.max_jobs:
                # Delete oldest jobs
                delete_count = count - self.max_jobs
                cursor.execute(
                    """
                    DELETE FROM jobs
                    WHERE job_id IN (
                        SELECT job_id FROM jobs
                        ORDER BY created_at ASC
                        LIMIT ?
                    )
                    """,
                    (delete_count,),
                )
                logger.info(f"Cleaned up {delete_count} old jobs")

    def clear_all_jobs(self) -> int:
        """
        Clear all completed jobs from history.

        Returns:
            Number of jobs deleted
        """
        with self._cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE status = 'completed'")
            count = cursor.fetchone()["count"]

            cursor.execute("DELETE FROM jobs WHERE status = 'completed'")
            logger.info(f"Cleared {count} completed jobs from history")

        return count


# Global database instance (initialized lazily)
_db_instance: JobDatabase | None = None


def get_job_database() -> JobDatabase | None:
    """
    Get the global job database instance.

    Returns:
        JobDatabase instance or None if not configured
    """
    global _db_instance

    if _db_instance is not None:
        return _db_instance

    # Import here to avoid circular imports
    from geo_content.config import settings

    if settings.use_sqlite:
        _db_instance = JobDatabase(settings.db_path, max_jobs=50)
        return _db_instance

    return None


def init_job_database(db_path: str, max_jobs: int = 50) -> JobDatabase:
    """
    Initialize the global job database.

    Args:
        db_path: Path to SQLite database file
        max_jobs: Maximum number of jobs to retain

    Returns:
        JobDatabase instance
    """
    global _db_instance
    _db_instance = JobDatabase(db_path, max_jobs)
    return _db_instance
