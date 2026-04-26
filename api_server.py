"""
Ollama API Server - FastAPI REST API for Ollama Mistral 7B LLM Inference

This module provides a production-ready REST API wrapper around Ollama,
enabling text generation through HTTP endpoints with proper error handling,
logging, and configuration management.

Features:
    - Health check endpoint for service availability monitoring
    - Text generation endpoint with configurable parameters
    - Model listing endpoint
    - Comprehensive error handling and logging
    - Support for async/await for high concurrency
    - Environment-based configuration for dev/prod separation

Author: Takashim0101
Version: 1.0.0
License: MIT
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import logging
import httpx
import json

# Load environment variables from .env file
load_dotenv()

# Configure logging with level from environment variable
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Ollama API Server",
    description="REST API for Ollama Mistral 7B",
    version="1.0.0"
)

# Load configuration from environment variables
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
APP_ENV = os.getenv('APP_ENV', 'development')


class GenerateRequest(BaseModel):
    """Request model for text generation endpoint.

    Attributes:
        prompt: Input text prompt for the model to generate from
        stream: Whether to stream the response (default: False)
        max_tokens: Maximum number of tokens to generate (default: 50)
    """
    prompt: str
    stream: bool = False
    max_tokens: int = 50


class GenerateResponse(BaseModel):
    """Response model for text generation endpoint.

    Attributes:
        response: Generated text from the model
        model: Name of the model used for generation
    """
    response: str
    model: str


# Load timeout configurations from environment
OLLAMA_HEALTH_TIMEOUT = int(os.getenv('OLLAMA_HEALTH_TIMEOUT', 5))
OLLAMA_GENERATE_TIMEOUT = int(os.getenv('OLLAMA_GENERATE_TIMEOUT', 600))


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint to verify Ollama service availability.

    This endpoint verifies that the Ollama service is running and accessible.
    Used by orchestration systems to determine service health.

    Returns:
        dict: Health status including environment and model information

    Raises:
        HTTPException: 503 Service Unavailable if Ollama cannot be reached

    Example:
        >>> GET /health
        >>> {
        >>>     "status": "healthy",
        >>>     "environment": "development",
        >>>     "ollama_host": "ollama",
        >>>     "model": "mistral"
        >>> }
    """
    try:
        response = requests.get(
            f'{OLLAMA_HOST}/api/tags',
            timeout=OLLAMA_HEALTH_TIMEOUT
        )
        response.raise_for_status()
        return {
            "status": "healthy",
            "environment": APP_ENV,
            "ollama_host": OLLAMA_HOST,
            "model": OLLAMA_MODEL
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Ollama service unavailable"
        )


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate text using Ollama Mistral 7B model.

    This endpoint accepts a text prompt and returns generated text
    from the model. Supports configurable generation parameters
    including maximum token count.

    Args:
        request: GenerateRequest containing prompt and parameters

    Returns:
        GenerateResponse: Generated text and model name

    Raises:
        HTTPException: 503 if Ollama service is unreachable
        HTTPException: 504 if generation request times out
        HTTPException: 500 if Ollama returns an error response
        HTTPException: 422 if request validation fails

    Example:
        >>> POST /generate
        >>> {"prompt": "What is Docker?", "max_tokens": 100}
        >>> {
        >>>     "response": "Docker is a containerization platform...",
        >>>     "model": "mistral"
        >>> }
    """
    try:
        prompt_log = request.prompt[:40]
        logger.info(f"Generating response for prompt: {prompt_log}...")

        # Construct payload with Ollama API requirements
        # Map max_tokens to Ollama's num_predict
        ollama_payload = {
            "model": OLLAMA_MODEL,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "num_predict": request.max_tokens
            }
        }

        # Send async request to Ollama inference endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{OLLAMA_HOST}/api/generate',
                json=ollama_payload,
                timeout=OLLAMA_GENERATE_TIMEOUT
            )

            # Handle non-200 responses from Ollama
            if response.status_code != 200:
                logger.error(
                    f"Ollama returned non-200 status: "
                    f"{response.status_code} - {response.text}"
                )
                # Parse error message from JSON or fallback to text
                try:
                    error_data = json.loads(response.text)
                    error_msg = error_data.get('error', response.text)
                except Exception:
                    error_msg = response.text
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama Error: {error_msg}"
                )

            # Extract generated text from response
            data = response.json()

            return GenerateResponse(
                response=data.get('response', ''),
                model=OLLAMA_MODEL
            )

    except httpx.ConnectError:
        logger.error(f"Cannot connect to Ollama at {OLLAMA_HOST}")
        raise HTTPException(
            status_code=503,
            detail="Ollama service unavailable"
        )
    except httpx.TimeoutException:
        logger.error("Request timeout - inference took too long")
        raise HTTPException(
            status_code=504,
            detail="Request timeout - inference took too long"
        )
    except HTTPException:
        # Re-raise HTTP exceptions (avoid double-wrapping)
        raise
    except Exception as e:
        # Catch unexpected exceptions and log them
        logger.error(f"Generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


@app.get("/models")
async def list_models() -> dict:
    """List available models in Ollama.

    Retrieves the list of models currently available in the
    Ollama instance.

    Returns:
        dict: Response from Ollama containing available models

    Raises:
        HTTPException: 503 Service Unavailable if Ollama cannot be reached

    Example:
        >>> GET /models
        >>> {
        >>>     "models": [
        >>>         {"name": "mistral:latest", "size": "4.4GB"},
        >>>         {"name": "llama2:latest", "size": "3.8GB"}
        >>>     ]
        >>> }
    """
    try:
        response = requests.get(
            f'{OLLAMA_HOST}/api/tags',
            timeout=OLLAMA_HEALTH_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        raise HTTPException(
            status_code=503,
            detail="Ollama service unavailable"
        )


@app.get("/")
async def root() -> dict:
    """Root endpoint returning service information.

    Provides an overview of available endpoints and service configuration.
    Useful for API clients to discover available endpoints.

    Returns:
        dict: Service info including version, environment, endpoints

    Example:
        >>> GET /
        >>> {
        >>>     "service": "Ollama API Server",
        >>>     "version": "1.0.0",
        >>>     "environment": "development",
        >>>     "docs": "/docs",
        >>>     "endpoints": {
        >>>         "health": "/health",
        >>>         "generate": "/generate (POST)",
        >>>         "models": "/models"
        >>>     }
        >>> }
    """
    return {
        "service": "Ollama API Server",
        "version": "1.0.0",
        "environment": APP_ENV,
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "generate": "/generate (POST)",
            "models": "/models"
        }
    }


if __name__ == "__main__":
    import uvicorn

    # Load server configuration from environment variables
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))

    # Start Uvicorn ASGI server
    uvicorn.run(app, host=API_HOST, port=API_PORT) 
       