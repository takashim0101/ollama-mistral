from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import logging
import httpx

load_dotenv()

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ollama API Server",
    description="REST API for Ollama Mistral 7B",
    version="1.0.0"
)

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
APP_ENV = os.getenv('APP_ENV', 'development')

class GenerateRequest(BaseModel):
    prompt: str
    stream: bool = False
    max_tokens: int = 50 # Default to 50 tokens if not provided

class GenerateResponse(BaseModel):
    response: str
    model: str

OLLAMA_HEALTH_TIMEOUT = int(os.getenv('OLLAMA_HEALTH_TIMEOUT', 5))

# ...

@app.get("/health")
async def health_check():
    """healthcheck"""
    try:
        response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=OLLAMA_HEALTH_TIMEOUT)
        response.raise_for_status()
        return {
            "status": "healthy",
            "environment": APP_ENV,
            "ollama_host": OLLAMA_HOST,
            "model": OLLAMA_MODEL
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Ollama service unavailable")

OLLAMA_GENERATE_TIMEOUT = int(os.getenv('OLLAMA_GENERATE_TIMEOUT', 600))

# ...

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    endpoint of generating text.
    
    Example:
    ```json
    {
        "prompt": "What is Docker?"
    }
    ```
    """
    try:
        logger.info(f"Generating response for prompt: {request.prompt[:50]}...")
        
        # Construct the exact payload Ollama expects
        ollama_payload = {
            "model": OLLAMA_MODEL,  # Required by Ollama
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "num_predict": request.max_tokens  # Mapping your max_tokens to Ollama's setting
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{OLLAMA_HOST}/api/generate', json=ollama_payload, timeout=OLLAMA_GENERATE_TIMEOUT)
            
            # If Ollama still throws an error, this will catch it
            if response.status_code != 200:
                logger.error(f"Ollama returned non-200 status: {response.status_code} - {response.text}")
                try:
                    import json
                    error_data = json.loads(response.text)
                    error_msg = error_data.get('error', response.text)
                except:
                    error_msg = response.text
                raise HTTPException(status_code=500, detail=f"Ollama Error: {error_msg}")
                
            data = response.json()
            
            return GenerateResponse(
                response=data.get('response', ''),
                model=OLLAMA_MODEL
            )
    except httpx.ConnectError:
        logger.error(f"Cannot connect to Ollama at {OLLAMA_HOST}")
        raise HTTPException(status_code=503, detail="Ollama service unavailable")
    except httpx.TimeoutException:
        logger.error("Request timeout")
        raise HTTPException(status_code=504, detail="Request timeout - inference took too long")
    except HTTPException: # Catch HTTPException specifically and re-raise it
        raise
    except Exception as e: # Catch any other unexpected exceptions
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/models")
async def list_models():
    """list of models"""
    try:
        response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=OLLAMA_HEALTH_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        raise HTTPException(status_code=503, detail="Ollama service unavailable")

@app.get("/")
async def root():
    """Route endpoints"""
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
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    uvicorn.run(app, host=API_HOST, port=API_PORT)