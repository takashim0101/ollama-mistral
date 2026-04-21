from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
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

class GenerateResponse(BaseModel):
    response: str
    model: str

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    try:
        response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=5)
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

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    テキスト生成エンドポイント
    
    Example:
    ```json
    {
        "prompt": "What is Docker?"
    }
    ```
    """
    try:
        logger.info(f"Generating response for prompt: {request.prompt[:50]}...")
        
        response = requests.post(
            f'{OLLAMA_HOST}/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': request.prompt,
                'stream': request.stream
            },
            timeout=600
        )
        response.raise_for_status()
        
        result = response.json()
        
        return GenerateResponse(
            response=result.get('response', ''),
            model=OLLAMA_MODEL
        )
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Ollama at {OLLAMA_HOST}")
        raise HTTPException(status_code=503, detail="Ollama service unavailable")
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        raise HTTPException(status_code=504, detail="Request timeout - inference took too long")
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """利用可能なモデル一覧"""
    try:
        response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        raise HTTPException(status_code=503, detail="Ollama service unavailable")

@app.get("/")
async def root():
    """ルートエンドポイント"""
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
