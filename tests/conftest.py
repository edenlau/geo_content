"""
Pytest configuration and fixtures for GEO Content Platform tests.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# Set test environment variables before importing app
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")
os.environ.setdefault("TAVILY_API_KEY", "tvly-test-key")
os.environ.setdefault("ENVIRONMENT", "development")


@pytest.fixture
def sample_research_brief():
    """Sample research brief for testing."""
    return {
        "client_name": "Ocean Park Hong Kong",
        "target_question": "What are the main attractions at Ocean Park Hong Kong?",
        "language_code": "en",
        "key_facts": [
            "Ocean Park Hong Kong is a marine mammal park and theme park",
            "Located on the southern side of Hong Kong Island",
            "Features roller coasters, animal exhibits, and aquariums",
        ],
        "statistics": [
            {
                "value": "7.6 million",
                "context": "Annual visitors in 2019",
                "source": "Hong Kong Tourism Board",
            },
            {
                "value": "Over 5,000",
                "context": "Fish from 400+ species in the Grand Aquarium",
                "source": "Ocean Park Official",
            },
        ],
        "quotations": [
            {
                "quote": "Ocean Park offers an unmatched combination of marine education and entertainment",
                "speaker": "Dr. Wong",
                "title": "Chief Conservation Officer",
                "source": "Ocean Park Press Release",
            }
        ],
        "citations": [
            {
                "name": "Hong Kong Tourism Board",
                "url": "https://www.discoverhongkong.com",
                "description": "Official tourism authority",
            },
            {
                "name": "Ocean Park Hong Kong",
                "url": "https://www.oceanpark.com.hk",
                "description": "Official park website",
            },
        ],
        "source_urls": ["https://www.oceanpark.com.hk"],
        "raw_content_summary": "Research conducted on Ocean Park attractions",
    }


@pytest.fixture
def sample_content_request():
    """Sample content generation request."""
    from geo_content.models import ContentGenerationRequest

    return ContentGenerationRequest(
        client_name="Ocean Park Hong Kong",
        target_question="What are the main attractions at Ocean Park Hong Kong?",
        reference_urls=["https://www.oceanpark.com.hk"],
        reference_documents=[],
    )


@pytest.fixture
def sample_draft_a():
    """Sample draft from Writer Agent A."""
    from geo_content.models import ContentDraft

    return ContentDraft(
        draft_id="A",
        content="""Ocean Park Hong Kong is one of Asia's premier marine theme parks, attracting over 7.6 million visitors annually according to the Hong Kong Tourism Board.

Located on the southern side of Hong Kong Island, Ocean Park offers an unmatched combination of marine education and thrilling entertainment. The Grand Aquarium, one of the park's signature attractions, houses over 5,000 fish from 400+ species.

"Ocean Park offers an unmatched combination of marine education and entertainment," said Dr. Wong, Chief Conservation Officer at Ocean Park.

The park features world-class roller coasters, including the Hair Raiser and Arctic Blast, alongside educational exhibits showcasing marine conservation efforts.""",
        word_count=98,
        model_used="gpt-4.1-mini",
        generation_time_ms=5000,
        statistics_count=2,
        citations_count=2,
        quotations_count=1,
    )


@pytest.fixture
def sample_draft_b():
    """Sample draft from Writer Agent B."""
    from geo_content.models import ContentDraft

    return ContentDraft(
        draft_id="B",
        content="""Ocean Park Hong Kong stands as a world-renowned marine theme park that welcomed 7.6 million visitors in 2019, as reported by the Hong Kong Tourism Board.

Situated on Hong Kong Island's southern coast, Ocean Park combines thrilling rides with marine conservation education. The park's Grand Aquarium showcases over 5,000 marine creatures from more than 400 species.

Dr. Wong, Chief Conservation Officer, notes: "Ocean Park offers an unmatched combination of marine education and entertainment."

From the adrenaline-pumping Hair Raiser to the educational Polar Adventure exhibit, Ocean Park delivers experiences for visitors of all ages.""",
        word_count=95,
        model_used="claude-3-5-haiku-20241022",
        generation_time_ms=5500,
        statistics_count=2,
        citations_count=2,
        quotations_count=1,
    )


@pytest.fixture
def test_client():
    """FastAPI test client."""
    # Import here to avoid circular imports
    from geo_content.main import app

    return TestClient(app)


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls."""
    with patch("openai.AsyncOpenAI") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic API calls."""
    with patch("anthropic.AsyncAnthropic") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance
