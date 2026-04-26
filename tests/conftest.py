"""
Pytest configuration and fixtures for Ollama API Server tests.

This module provides:
    - pytest fixtures for testing
    - Custom markers for test organization
    - Ollama service availability detection
    - Automatic test skipping when Ollama is unavailable

Test Categories:
    - unit: Tests API endpoints with mocked Ollama responses
    - integration: Tests actual Ollama service integration (requires running Ollama)
"""

import os
import sys
import pytest
import requests

# Configure Ollama host for testing
os.environ['OLLAMA_HOST'] = 'http://localhost:11434'

# Add parent directory to path to import api_server module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def pytest_configure(config):
    """Register custom pytest markers.
    
    This hook is called after command line options have been parsed
    and all plugins and initial conftest files been loaded.
    
    Args:
        config: pytest Config object
    """
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test requiring Ollama service"
    )


def ollama_available() -> bool:
    """Check if Ollama service is running and accessible.
    
    Attempts a simple HTTP request to the Ollama API tags endpoint
    to verify service availability.
    
    Returns:
        bool: True if Ollama is accessible, False otherwise
    """
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
    """Fixture to check Ollama availability at session start.
    
    This fixture runs once per test session and provides Ollama
    availability status to test functions that need it.
    
    Returns:
        bool: True if Ollama is available, False otherwise
        
    Example:
        >>> def test_something(check_ollama):
        >>>     if check_ollama:
        >>>         # Ollama is available
        >>>         pass
    """
    return ollama_available()


def pytest_collection_modifyitems(config, items):
    """Skip integration tests if Ollama service is unavailable.
    
    This hook is called after test collection is performed. It automatically
    marks integration tests with skip if Ollama is not running.
    
    This approach allows the test suite to run successfully even when
    Ollama is not available, ensuring CI/CD doesn't fail due to
    external service dependencies.
    
    Args:
        config: pytest Config object
        items: list of collected test items
    """
    if not ollama_available():
        skip_ollama = pytest.mark.skip(
            reason="Ollama service not available"
        )
        for item in items:
            if "test_ollama_integration" in item.nodeid:
                item.add_marker(skip_ollama)
