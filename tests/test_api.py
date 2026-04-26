# tests/test_api.py
# License: CC BY-NC-SA 4.0
import pytest
import requests
from httpx import AsyncClient, ASGITransport
from api_server import app
from unittest.mock import patch, AsyncMock
import httpx

# Set all tests in this file to be treated as asynchronous
pytestmark = pytest.mark.asyncio


@patch('api_server.requests.get')
async def test_health_check_ollama_unavailable(mock_requests_get):
    """Test GET /health when Ollama is unavailable."""
    mock_requests_get.side_effect = requests.exceptions.ConnectionError
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        response = await ac.get("/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama service unavailable"


@patch('api_server.requests.get')
async def test_list_models_ollama_unavailable(mock_requests_get):
    """Test GET /models when Ollama is unavailable."""
    mock_requests_get.side_effect = requests.exceptions.ConnectionError
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        response = await ac.get("/models")
    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama service unavailable"


@patch('api_server.httpx.AsyncClient')  # Patch the AsyncClient class
async def test_generate_ollama_connection_error(mock_async_client_class):
    """Test POST /generate when Ollama connection fails."""
    mock_instance = AsyncMock()
    # Breaking the long line for flake8
    mock_enter = mock_async_client_class.return_value.__aenter__
    mock_enter.return_value = mock_instance
    mock_instance.post.side_effect = httpx.ConnectError("Connection refused")

    transport = ASGITransport(app=app)
    payload = {"prompt": "Test prompt", "max_tokens": 50}
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        response = await ac.post("/generate", json=payload)
    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama service unavailable"
