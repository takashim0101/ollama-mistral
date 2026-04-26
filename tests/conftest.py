"""
Pytest configuration and fixtures for Ollama API Server tests.

License: CC BY-NC-SA 4.0
"""

import os
import sys
import pytest
import requests

# Configure Ollama host for testing
os.environ['OLLAMA_HOST'] = 'http://localhost:11434'

# Add parent directory to path to import api_server module
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))


def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test requiring Ollama service"
    )


def ollama_available() -> bool:
    """Check if Ollama service is running and accessible."""
    try:
        response = requests.get(
            'http://localhost:11434/api/tags',
            timeout=2
        )
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def check_ollama() -> bool:
    """Fixture to check Ollama availability at session start."""
    return ollama_available()


def pytest_collection_modifyitems(config, items):
    """Skip integration tests if Ollama service is unavailable."""
    if not ollama_available():
        skip_ollama = pytest.mark.skip(
            reason="Ollama service not available"
        )
        for item in items:
            if "test_ollama_integration" in item.nodeid:
                item.add_marker(skip_ollama)
