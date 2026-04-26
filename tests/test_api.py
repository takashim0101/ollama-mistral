# tests/test_api.py
import pytest
import requests # Added import for requests
from httpx import AsyncClient, ASGITransport
from api_server import app  # Import the FastAPI instance from main.py
from unittest.mock import patch, AsyncMock
import httpx # Import httpx for ConnectError

# Set all tests in this file to be treated as asynchronous
pytestmark = pytest.mark.asyncio

async def test_health_check():
    """Test for the GET /health endpoint"""
    # ASGITransport is used to test the app directly without starting a real server
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.get("/health")
    
    # Verify that the status code is 200 (OK)
    assert response.status_code == 200
    # Verify that the JSON response is as expected
    assert response.json()["status"] == "healthy"

async def test_generate_text():
    """Test for the POST /generate endpoint"""
    transport = ASGITransport(app=app)
    
    # Request payload for testing
    payload = {
        "prompt": "Hello, this is a test.",
        "max_tokens": 50
    }
    
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response structure defined in Pydantic (check if 'response' key exists)
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0  # Ensure it's not an empty string

async def test_generate_text_invalid_request():
    """Test for validation error (422)"""
    transport = ASGITransport(app=app)
    
    # Invalid payload missing the required 'prompt' field
    invalid_payload = {
        "max_tokens": 50
    }
    
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/generate", json=invalid_payload)
    
    # Verify that FastAPI and Pydantic correctly catch the error and return 422 Unprocessable Entity
    assert response.status_code == 422

async def test_root_endpoint():
    """Test for the GET / endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Ollama API Server"
    assert "version" in data
    assert "environment" in data
    assert "docs" in data
    assert "endpoints" in data
    assert isinstance(data["endpoints"], dict)

async def test_list_models():
    """Test for the GET /models endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.get("/models")
    
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert isinstance(data["models"], list)

async def test_generate_text_empty_prompt():
    """Test for POST /generate with an empty prompt"""
    transport = ASGITransport(app=app)
    payload = {
        "prompt": "",
        "max_tokens": 50
    }
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/generate", json=payload)
    
    # FastAPI's Pydantic validation for 'str' fields typically allows empty strings
    # unless explicitly forbidden (e.g., with min_length=1).
    # The current implementation of GenerateRequest(BaseModel) for 'prompt: str' allows empty string.
    # Ollama might return an empty response or an error for an empty prompt.
    # For now, we expect a 200 and a string response, as the API itself doesn't explicitly forbid empty prompts.
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)

async def test_generate_text_max_tokens_zero():
    """Test for POST /generate with max_tokens set to 0"""
    transport = ASGITransport(app=app)
    payload = {
        "prompt": "Short test.",
        "max_tokens": 0
    }
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    # Depending on Ollama's behavior with num_predict=0, the response might be empty.
    # We assert it's a string, and the API handled it without error.

@patch('api_server.requests.get')
async def test_health_check_ollama_unavailable(mock_requests_get):
    """Test GET /health when Ollama is unavailable."""
    mock_requests_get.side_effect = requests.exceptions.ConnectionError
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.get("/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama service unavailable"

@patch('api_server.requests.get')
async def test_list_models_ollama_unavailable(mock_requests_get):
    """Test GET /models when Ollama is unavailable."""
    mock_requests_get.side_effect = requests.exceptions.ConnectionError
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.get("/models")
    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama service unavailable"

@patch('api_server.httpx.AsyncClient') # Patch the AsyncClient class
async def test_generate_ollama_connection_error(mock_async_client_class):
    """Test POST /generate when Ollama connection fails."""
    mock_instance = AsyncMock()
    mock_async_client_class.return_value.__aenter__.return_value = mock_instance
    mock_instance.post.side_effect = httpx.ConnectError("Connection refused")

    transport = ASGITransport(app=app)
    payload = {"prompt": "Test prompt", "max_tokens": 50}
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/generate", json=payload)
    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama service unavailable"

@patch('api_server.httpx.AsyncClient') # Patch the AsyncClient class
async def test_generate_ollama_non_200_response(mock_async_client_class):
    """Test POST /generate when Ollama returns a non-200 status."""
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = '{"error": "Ollama internal error"}'
    mock_response.json.return_value = {"error": "Ollama internal error"} # Mock the json() method

    mock_instance = AsyncMock()
    mock_async_client_class.return_value.__aenter__.return_value = mock_instance
    mock_instance.post.return_value = mock_response

    transport = ASGITransport(app=app)
    payload = {"prompt": "Test prompt", "max_tokens": 50}
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/generate", json=payload)
    assert response.status_code == 500
    
    print(f"Raw Response Text from FastAPI: {response.text}") # Debug print
    
    response_json = response.json() # Get the response JSON once
    assert "detail" in response_json # Assert that 'detail' key exists
    assert response_json["detail"] == "Ollama Error: Ollama internal error"