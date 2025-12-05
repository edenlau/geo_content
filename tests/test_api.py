"""
Tests for FastAPI endpoints.
"""

import pytest


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, test_client):
        """Test health endpoint returns healthy status."""
        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "geo-content-platform"
        assert "version" in data
        assert "timestamp" in data


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_returns_service_info(self, test_client):
        """Test root endpoint returns service information."""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "GEO Content Optimization Platform"
        assert "version" in data
        assert "endpoints" in data


class TestLanguagesEndpoint:
    """Test languages endpoint."""

    def test_get_supported_languages(self, test_client):
        """Test languages endpoint returns all supported languages."""
        response = test_client.get("/api/v1/languages")

        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) == 8  # en, zh-TW, zh-CN, 5 Arabic dialects

        # Check for specific languages
        codes = [lang["code"] for lang in data["languages"]]
        assert "en" in codes
        assert "zh-TW" in codes
        assert "zh-CN" in codes
        assert "ar-MSA" in codes
        assert "ar-Gulf" in codes

        # Check RTL languages
        assert "rtl_languages" in data
        assert all(code.startswith("ar-") for code in data["rtl_languages"])


class TestStrategiesEndpoint:
    """Test GEO strategies endpoint."""

    def test_get_geo_strategies(self, test_client):
        """Test strategies endpoint returns GEO optimization info."""
        response = test_client.get("/api/v1/strategies")

        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert len(data["strategies"]) >= 4  # At least 4 core strategies

        # Check strategy structure
        strategy = data["strategies"][0]
        assert "name" in strategy
        assert "visibility_boost" in strategy
        assert "description" in strategy

        # Check threshold and iterations
        assert data["quality_threshold"] == 70
        assert data["max_iterations"] == 3


class TestGenerateEndpoint:
    """Test content generation endpoint."""

    def test_generate_validation_error(self, test_client):
        """Test that invalid request returns validation error."""
        response = test_client.post(
            "/api/v1/generate",
            json={
                "client_name": "",  # Empty client name should fail
                "target_question": "Test question",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_generate_short_question_error(self, test_client):
        """Test that too-short question returns validation error."""
        response = test_client.post(
            "/api/v1/generate",
            json={
                "client_name": "Test Client",
                "target_question": "Short",  # Too short
            },
        )

        assert response.status_code == 422


class TestAsyncGenerateEndpoint:
    """Test async content generation endpoint."""

    def test_async_generate_returns_job_id(self, test_client):
        """Test that async endpoint returns job ID."""
        # Note: This will start a background task but we won't wait for it
        # In a real test, we'd mock the workflow
        response = test_client.post(
            "/api/v1/generate/async",
            json={
                "client_name": "Test Client",
                "target_question": "What are the main attractions at this location?",
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert "status_url" in data
        assert data["status"] == "pending"


class TestJobStatusEndpoint:
    """Test job status endpoint."""

    def test_job_not_found(self, test_client):
        """Test that non-existent job returns 404."""
        response = test_client.get("/api/v1/jobs/nonexistent_job_id")

        assert response.status_code == 404
