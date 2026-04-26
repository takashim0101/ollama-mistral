import pytest
import requests


# Set markers for this test file
pytestmark = pytest.mark.integration


def test_ollama_generate():
    """Integration test: Test Ollama text generation endpoint directly"""
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'mistral',
            'prompt': 'Hello!',
            'stream': False
        },
        timeout=30
    )
    assert response.status_code == 200
    data = response.json()
    assert 'response' in data
    assert isinstance(data['response'], str)
    assert len(data['response']) > 0
    assert 'model' in data
    assert data['model'] == 'mistral'
