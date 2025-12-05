# GEO Content Optimization Platform

Multi-Agent GEO Content Optimization Platform designed to maximize client visibility in generative search engines (ChatGPT, Perplexity AI, Google AI Overviews, Claude).

## Features

- **Automatic Language Detection**: Supports English, Chinese (Traditional/Simplified), and Arabic dialects
- **Dual-LLM Generation**: Parallel content creation using GPT-4.1-mini and Claude 3.5 Haiku
- **Research-Backed Optimization**: Evidence-based GEO strategies with 30-40% visibility improvement
- **Full Observability**: OpenAI Trace integration for complete workflow tracking
- **GEO Performance Commentary**: Detailed explanation of optimization decisions

## Research Foundation

| Study | Key Finding | Application |
|-------|-------------|-------------|
| Aggarwal et al. (2024) KDD '24 | GEO strategies boost visibility up to 40% | Core optimization strategies |
| Aggarwal et al. (2024) | Combined strategies (Fluency + Statistics) yield 35.8% improvement | Multi-strategy application |
| Luttgenau et al. (2025) arXiv | Domain-specific fine-tuning achieves 30.96% position-adjusted visibility gain | Industry-specific optimization |

## Technology Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | OpenAI Agents SDK |
| Writer Agent A | GPT-4.1-mini |
| Writer Agent B | Claude 3.5 Haiku |
| Evaluator | GPT-4.1 |
| Web Harvesting | Pathway |
| Package Manager | uv |
| API Framework | FastAPI |

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

```bash
# Clone the repository
cd geo_content

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync

# Copy environment template and fill in API keys
cp .env.example .env
# Edit .env with your API keys
```

### Required API Keys

Add these to your `.env` file:

```bash
OPENAI_API_KEY=sk-your-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
TAVILY_API_KEY=tvly-your-tavily-api-key  # Optional, for web search
```

## Usage

### API Server

Start the FastAPI server:

```bash
# Development mode with auto-reload
uvicorn geo_content.main:app --reload

# Or use the built-in runner
python -m geo_content.main
```

Access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/generate` | POST | Generate GEO-optimized content (sync) |
| `/api/v1/generate/async` | POST | Start async generation (returns job ID) |
| `/api/v1/jobs/{job_id}` | GET | Check async job status |
| `/api/v1/languages` | GET | List supported languages |
| `/api/v1/strategies` | GET | List GEO strategies |
| `/api/v1/health` | GET | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Ocean Park Hong Kong",
    "target_question": "What are the main attractions at Ocean Park Hong Kong?",
    "reference_urls": ["https://www.oceanpark.com.hk"]
  }'
```

### Programmatic Usage

```python
import asyncio
from geo_content.agents.orchestrator import generate_geo_content
from geo_content.models import ContentGenerationRequest

async def main():
    request = ContentGenerationRequest(
        client_name="Ocean Park Hong Kong",
        target_question="What are the main attractions at Ocean Park Hong Kong?",
        reference_urls=["https://www.oceanpark.com.hk"],
    )

    response = await generate_geo_content(request)

    print(f"Content: {response.content}")
    print(f"Score: {response.evaluation_score}/100")
    print(f"Selected: Draft {response.selected_draft}")

asyncio.run(main())
```

## Supported Languages

| Language | Code | Region |
|----------|------|--------|
| English | `en` | US, UK, Australian |
| Traditional Chinese | `zh-TW` | Taiwan, Hong Kong |
| Simplified Chinese | `zh-CN` | Mainland China, Singapore |
| Modern Standard Arabic | `ar-MSA` | Formal/Written |
| Gulf Arabic | `ar-Gulf` | UAE, Saudi Arabia, Kuwait, Qatar, Bahrain, Oman |
| Egyptian Arabic | `ar-EG` | Egypt |
| Levantine Arabic | `ar-Levant` | Lebanon, Syria, Jordan, Palestine |
| Maghrebi Arabic | `ar-Maghreb` | Morocco, Algeria, Tunisia, Libya |

## GEO Strategies Applied

| Strategy | Expected Visibility Boost |
|----------|--------------------------|
| Statistics Addition | +25-40% |
| Quotation Addition | +27-40% |
| Citation Addition | +24-30% |
| Fluency Optimization | +24-30% |
| Combined (Fluency + Statistics) | +35.8% |

## Architecture

```
User Input → Language Detection → Research Agent → Parallel Writers (A & B) → Evaluator → Output
                                         ↓                    ↓
                                    Web Search           GPT + Claude
                                    URL Harvest
                                    Doc Parsing
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=geo_content

# Run specific test file
pytest tests/test_language_detection.py
```

### Project Structure

```
geo-content-platform/
├── src/geo_content/
│   ├── agents/          # AI agents (Research, Writers, Evaluator)
│   ├── api/             # FastAPI routes
│   ├── models/          # Pydantic models
│   ├── pipeline/        # Pathway data pipeline
│   ├── prompts/         # LLM prompts
│   ├── tools/           # Agent tools
│   ├── config.py        # Configuration
│   └── main.py          # FastAPI app
├── tests/               # Test suite
├── examples/            # Usage examples
├── pyproject.toml       # Project configuration
└── .env.example         # Environment template
```

## License

MIT License - See LICENSE file for details.

## Version

3.2.0

---

*© 2025 Tocanan.ai. All rights reserved.*
