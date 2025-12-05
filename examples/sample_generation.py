#!/usr/bin/env python3
"""
Sample script demonstrating GEO content generation.

This script shows how to use the GEO Content Platform programmatically.
"""

import asyncio
import json
from datetime import datetime

# Ensure you have set up your .env file with API keys before running
# cp .env.example .env
# Then fill in your API keys


async def main():
    """Run sample content generation."""
    from geo_content.agents.orchestrator import generate_geo_content
    from geo_content.models import ContentGenerationRequest

    print("=" * 60)
    print("GEO Content Optimization Platform - Sample Generation")
    print("=" * 60)
    print()

    # Create a sample request
    request = ContentGenerationRequest(
        client_name="Ocean Park Hong Kong",
        target_question="What are the main attractions at Ocean Park Hong Kong?",
        reference_urls=[
            "https://www.oceanpark.com.hk",
        ],
        reference_documents=[],
        language_override=None,  # Auto-detect language
    )

    print(f"Client: {request.client_name}")
    print(f"Question: {request.target_question}")
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    print("Generating GEO-optimized content...")
    print("(This may take 30-60 seconds)")
    print()

    try:
        # Generate content
        response = await generate_geo_content(request)

        # Display results
        print("=" * 60)
        print("GENERATION COMPLETE")
        print("=" * 60)
        print()

        print(f"Job ID: {response.job_id}")
        print(f"Trace ID: {response.trace_id}")
        print(f"Trace URL: {response.trace_url}")
        print()

        print("--- Language Detection ---")
        print(f"Language: {response.detected_language} ({response.language_code})")
        print(f"Direction: {response.writing_direction}")
        print()

        print("--- Evaluation Results ---")
        print(f"Selected Draft: {response.selected_draft}")
        print(f"Score: {response.evaluation_score}/100")
        print(f"Iterations: {response.evaluation_iterations}")
        print()

        print("--- GEO Analysis ---")
        for key, value in response.geo_analysis.items():
            print(f"  {key}: {value}")
        print()

        print("--- Generated Content ---")
        print("-" * 40)
        print(response.content)
        print("-" * 40)
        print()

        print(f"Word Count: {response.word_count}")
        print(f"Generation Time: {response.generation_time_ms}ms")
        print()

        print("--- Models Used ---")
        for agent, model in response.models_used.items():
            print(f"  {agent}: {model}")
        print()

        print("--- GEO Performance Commentary (Summary) ---")
        commentary = response.geo_commentary
        if "summary" in commentary:
            print(f"Assessment: {commentary['summary'].get('overall_assessment', 'N/A')[:200]}...")
            print(f"Visibility Boost: {commentary['summary'].get('predicted_visibility_improvement', 'N/A')}")
            print(f"Confidence: {commentary['summary'].get('confidence_level', 'N/A')}")
        print()

        print("--- Key Strengths ---")
        for strength in commentary.get("key_strengths", [])[:3]:
            print(f"  • {strength[:100]}...")
        print()

        # Save full response to file
        output_file = "sample_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str, ensure_ascii=False)
        print(f"Full response saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Make sure you have:")
        print("1. Created .env file with your API keys")
        print("2. Installed all dependencies: uv sync")
        print("3. Set OPENAI_API_KEY and ANTHROPIC_API_KEY")
        raise


def run_sync_example():
    """Synchronous example using the API client."""
    import httpx

    print("=" * 60)
    print("GEO Content Platform - API Client Example")
    print("=" * 60)
    print()

    # Assumes the API server is running on localhost:8000
    base_url = "http://localhost:8000"

    # Check health
    print("Checking API health...")
    try:
        response = httpx.get(f"{base_url}/api/v1/health")
        response.raise_for_status()
        print(f"API Status: {response.json()['status']}")
    except Exception as e:
        print(f"API not available: {e}")
        print("Start the API server first: python -m geo_content.main")
        return

    # Get supported languages
    print("\nSupported Languages:")
    response = httpx.get(f"{base_url}/api/v1/languages")
    for lang in response.json()["languages"]:
        print(f"  - {lang['name']} ({lang['code']})")

    # Generate content (async endpoint for demo)
    print("\nStarting async content generation...")
    response = httpx.post(
        f"{base_url}/api/v1/generate/async",
        json={
            "client_name": "Ocean Park Hong Kong",
            "target_question": "What makes Ocean Park Hong Kong special?",
        },
    )

    if response.status_code == 202:
        job_data = response.json()
        print(f"Job started: {job_data['job_id']}")
        print(f"Check status at: {job_data['status_url']}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        run_sync_example()
    else:
        asyncio.run(main())
