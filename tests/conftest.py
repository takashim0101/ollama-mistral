import os
import sys
import pytest
import requests

os.environ['OLLAMA_HOST'] = 'http://localhost:11434'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring Ollama service"
    )

def ollama_available():
    """Check if Ollama service is available"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        return response.status_code == 200
    except:
        return False

@pytest.fixture(scope="session")
def check_ollama():
    """Fixture to check Ollama availability"""
    return ollama_available()

def pytest_collection_modifyitems(config, items):
    """Skip integration tests if Ollama is not available"""
    if not ollama_available():
        skip_ollama = pytest.mark.skip(reason="Ollama service not available")
        for item in items:
            if "test_ollama_integration" in item.nodeid:
                item.add_marker(skip_ollama)
