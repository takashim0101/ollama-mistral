"""
Ollama API Server - FastAPI REST API for Ollama Mistral 7B LLM Inference

This module provides a production-ready REST API wrapper around Ollama,
enabling text generation through HTTP endpoints with proper error handling,
logging, configuration management, caching, and monitoring.

Author: Takashim0101
Version: 1.1.0
License: CC BY-NC-SA 4.0
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import logging
import httpx
import json
from functools import lru_cache
# Added RetryError to the imports
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from prometheus_client import Counter, Histogram, generate_latest
import time

# Load environment variables from .env file
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Ollama API Server",
    description="REST API for Ollama Mistral 7B with caching and monitoring",
    version="1.1.0"
)

# Configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
APP_ENV = os.getenv('APP_ENV', 'development')

# ============================================================================
# Caching Configuration
# ============================================================================

CACHE_SIZE = int(os.getenv('CACHE_SIZE', 100))
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'


@lru_cache(maxsize=CACHE_SIZE)
def get_cached_generation(prompt: str, max_tokens: int) -> str:
    """Cache placeholder."""
    return "__CACHE_MISS__"


def cache_key(prompt: str, max_tokens: int) -> tuple:
    return (prompt, max_tokens)

# ============================================================================
# Prometheus Metrics
# ============================================================================


request_count = Counter(
    'ollama_api_requests_total', 'Total API requests', [
        'endpoint', 'status', 'method'])
request_duration = Histogram(
    'ollama_api_request_duration_seconds', 'API duration', [
        'endpoint', 'status'])
cache_hits = Counter(
    'ollama_api_cache_hits_total',
    'Total cache hits',
    ['endpoint'])
cache_misses = Counter(
    'ollama_api_cache_misses_total',
    'Total cache misses',
    ['endpoint'])
ollama_requests = Counter(
    'ollama_inference_requests_total',
    'Total Ollama requests',
    ['status'])
ollama_duration = Histogram(
    'ollama_inference_duration_seconds',
    'Ollama latency',
    ['status'],
    buckets=(
        0.5,
        1,
        2,
        5,
        10,
        30,
        60,
        300))
ollama_tokens_generated = Histogram(
    'ollama_tokens_generated', 'Tokens generated', buckets=(
        10, 50, 100, 200, 500, 1000))
errors_total = Counter(
    'ollama_api_errors_total', 'Total errors', [
        'error_type', 'endpoint'])

# ============================================================================
# Pydantic Models
# ============================================================================


class GenerateRequest(BaseModel):
    prompt: str
    stream: bool = False
    max_tokens: int = 50


class GenerateResponse(BaseModel):
    response: str
    model: str
    cached: bool = False

# ============================================================================
# Retry Configuration
# ============================================================================


OLLAMA_HEALTH_TIMEOUT = int(os.getenv('OLLAMA_HEALTH_TIMEOUT', 5))
OLLAMA_GENERATE_TIMEOUT = int(os.getenv('OLLAMA_GENERATE_TIMEOUT', 600))
RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', 3))
RETRY_BACKOFF_FACTOR = float(os.getenv('RETRY_BACKOFF_FACTOR', 2))


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS),
       wait=wait_exponential(multiplier=1,
                             min=1,
                             max=10,
                             exp_base=RETRY_BACKOFF_FACTOR))
async def call_ollama_with_retry(client, url, payload, timeout):
    logger.debug("Attempting to call Ollama...")
    return await client.post(url, json=payload, timeout=timeout)

# ============================================================================
# Endpoints
# ============================================================================


@app.get("/health")
async def health_check() -> dict:
    try:
        response = requests.get(
            f'{OLLAMA_HOST}/api/tags',
            timeout=OLLAMA_HEALTH_TIMEOUT)
        response.raise_for_status()
        request_count.labels(
            endpoint='/health',
            status='success',
            method='GET').inc()
        return {
            "status": "healthy",
            "environment": APP_ENV,
            "ollama_host": OLLAMA_HOST,
            "model": OLLAMA_MODEL}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        errors_total.labels(
            error_type='health_check_failed',
            endpoint='/health').inc()
        request_count.labels(
            endpoint='/health',
            status='error',
            method='GET').inc()
        raise HTTPException(
            status_code=503,
            detail="Ollama service unavailable")


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    try:
        if CACHE_ENABLED:
            cached_result = get_cached_generation(
                request.prompt, request.max_tokens)
            if cached_result != "__CACHE_MISS__":
                logger.info(f"Cache hit for prompt: {request.prompt[:40]}...")
                cache_hits.labels(endpoint='/generate').inc()
                return GenerateResponse(
                    response=cached_result,
                    model=OLLAMA_MODEL,
                    cached=True)
            else:
                cache_misses.labels(endpoint='/generate').inc()

        logger.info(f"Generating for prompt: {request.prompt[:40]}...")

        ollama_payload = {
            "model": OLLAMA_MODEL,
            "prompt": request.prompt,
            "stream": False,
            "options": {"num_predict": request.max_tokens}
        }

        start_time = time.time()

        async with httpx.AsyncClient() as client:
            try:
                # Breakdown the long line into multiple lines
                response = await call_ollama_with_retry(
                    client,
                    f'{OLLAMA_HOST}/api/generate',
                    ollama_payload,
                    OLLAMA_GENERATE_TIMEOUT
                )
            # FIX: Catch both ConnectError and RetryError to return 503
            except (httpx.ConnectError, RetryError) as e:
                logger.error(
                    f"Failed to connect to Ollama after multiple retries: {e}")
                errors_total.labels(
                    error_type='connection_error',
                    endpoint='/generate').inc()
                ollama_requests.labels(status='connect_error').inc()
                request_count.labels(
                    endpoint='/generate',
                    status='error',
                    method='POST').inc()
                raise HTTPException(
                    status_code=503,
                    detail="Ollama service unavailable")

            except httpx.TimeoutException:
                logger.error("Inference timed out")
                errors_total.labels(
                    error_type='timeout',
                    endpoint='/generate').inc()
                ollama_requests.labels(status='timeout').inc()
                request_count.labels(
                    endpoint='/generate',
                    status='timeout',
                    method='POST').inc()
                raise HTTPException(status_code=504, detail="Request timeout")

            # Metrics and Response Extraction
            elapsed = time.time() - start_time
            ollama_duration.labels(status='success').observe(elapsed)

            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code}")
                errors_total.labels(
                    error_type='ollama_error',
                    endpoint='/generate').inc()
                ollama_requests.labels(status='error').inc()
                try:
                    error_msg = json.loads(
                        response.text).get(
                        'error', response.text)
                except Exception:
                    error_msg = response.text
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama Error: {error_msg}")

            data = response.json()
            generated_text = data.get('response', '')

            ollama_requests.labels(status='success').inc()
            request_count.labels(
                endpoint='/generate',
                status='success',
                method='POST').inc()
            ollama_tokens_generated.observe(len(generated_text.split()))

            return GenerateResponse(
                response=generated_text,
                model=OLLAMA_MODEL,
                cached=False)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        errors_total.labels(
            error_type='unexpected',
            endpoint='/generate').inc()
        request_count.labels(
            endpoint='/generate',
            status='error',
            method='POST').inc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/models")
async def list_models() -> dict:
    try:
        response = requests.get(
            f'{OLLAMA_HOST}/api/tags',
            timeout=OLLAMA_HEALTH_TIMEOUT)
        response.raise_for_status()
        request_count.labels(
            endpoint='/models',
            status='success',
            method='GET').inc()
        return response.json()
    except Exception as e:
        logger.error(f"Models fetch failed: {e}")
        errors_total.labels(
            error_type='models_fetch_failed',
            endpoint='/models').inc()
        request_count.labels(
            endpoint='/models',
            status='error',
            method='GET').inc()
        raise HTTPException(
            status_code=503,
            detail="Ollama service unavailable")


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/")
async def root() -> dict:
    request_count.labels(endpoint='/', status='success', method='GET').inc()
    return {
        "service": "Ollama API Server",
        "version": "1.1.0",
        "environment": APP_ENV,
        "docs": "/docs",
        "metrics": "/metrics",
        "endpoints": {
            "health": "/health",
            "generate": "/generate (POST)",
            "models": "/models"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, host=os.getenv(
            'API_HOST', '0.0.0.0'), port=int(
            os.getenv(
                'API_PORT', 8000)))
