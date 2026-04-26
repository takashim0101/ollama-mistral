# Resilience & Error Handling Strategy

This document outlines how the Ollama Mistral 7B system handles errors, failures, and recovery scenarios.

## Error Handling Philosophy

**Principle**: Fail fast, log everything, recover gracefully.

### Error Categories

1. **Transient Errors** - Temporary, likely to recover
   - Network timeouts
   - Ollama service temporarily unavailable
   - Momentary overload

2. **Permanent Errors** - Unlikely to recover without intervention
   - Invalid requests
   - Model not found
   - Configuration errors

3. **Degradation** - System still works but at reduced capacity
   - Slow inference
   - High latency
   - Resource exhaustion

## Implementation Patterns

### 1. Request Timeouts

All external calls have explicit timeouts:

```python
# Health check - fast timeout (5 seconds)
response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=5)

# Text generation - longer timeout (600 seconds)
response = await client.post(
    f'{OLLAMA_HOST}/api/generate',
    json=ollama_payload,
    timeout=600
)
```

**Rationale**: Prevents hanging requests that block resources.

### 2. Retry Logic (Recommended Implementation)

```python
import asyncio
from functools import wraps

def retry_with_backoff(max_retries=3, backoff_factor=2):
    """Retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.ConnectError, httpx.TimeoutException) as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=3, backoff_factor=2)
async def call_ollama():
    async with httpx.AsyncClient() as client:
        return await client.post(...)
```

### 3. Circuit Breaker Pattern (Recommended Implementation)

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def _should_attempt_reset(self):
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
```

### 4. Error Response Formatting

All errors follow consistent structure:

```python
from http import HTTPStatus

class APIError(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

# Error responses always include:
# - status_code: HTTP status
# - detail: User-friendly message
# - error_code: Machine-readable code for client logic

{
    "status_code": 503,
    "detail": "Ollama service unavailable",
    "error_code": "OLLAMA_UNAVAILABLE",
    "timestamp": "2026-04-26T12:34:56Z",
    "request_id": "uuid-here"
}
```

## Specific Failure Scenarios

### Scenario 1: Ollama Service Down

**Detection**:
```python
try:
    response = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=5)
    response.raise_for_status()
except (requests.ConnectionError, requests.Timeout):
    logger.error(f"Cannot connect to Ollama at {OLLAMA_HOST}")
    raise HTTPException(status_code=503, detail="Ollama service unavailable")
```

**Recovery Strategy**:
1. Log error with timestamp
2. Return 503 Service Unavailable
3. Client implements retry logic
4. Alert operations team (if monitoring configured)

**Monitoring**: Health check endpoint runs every 30 seconds

### Scenario 2: Inference Timeout

**Detection**:
```python
try:
    response = await client.post(..., timeout=600)
except httpx.TimeoutException:
    logger.error("Request timeout - inference took too long")
    raise HTTPException(
        status_code=504,
        detail="Request timeout - inference took too long"
    )
```

**Recovery Strategy**:
1. Log timeout with request details
2. Return 504 Gateway Timeout
3. Client can retry with different parameters
4. Consider implementing queue/batch processing

**Prevention**:
- Monitor slow queries
- Set reasonable max_tokens limits
- Consider caching common prompts

### Scenario 3: Invalid Request

**Detection**:
```python
# Pydantic automatically validates
class GenerateRequest(BaseModel):
    prompt: str  # Required
    max_tokens: int = 50  # Typed

# If validation fails:
# FastAPI returns 422 Unprocessable Entity with details
```

**Recovery Strategy**:
1. Return 422 with validation errors
2. Include field names and expected types
3. Don't log full request (might contain sensitive data)
4. Client fixes request and retries

### Scenario 4: Malformed Ollama Response

**Detection**:
```python
try:
    error_data = json.loads(response.text)
    error_msg = error_data.get('error', response.text)
except json.JSONDecodeError:
    error_msg = response.text
```

**Recovery Strategy**:
1. Parse error gracefully
2. Extract meaningful message
3. Return sanitized error to user
4. Log raw response for debugging

## Monitoring & Alerting

### Recommended Metrics to Track

```python
# 1. Request latency
# 2. Error rate (by endpoint)
# 3. Ollama availability
# 4. Inference speed (tokens/second)
# 5. Queue depth (if implementing queuing)
# 6. Memory/CPU usage
# 7. Cache hit rate
```

### Health Check Endpoints

```bash
# System health
GET /health
→ Returns: {"status": "healthy", "timestamp": "..."}

# Deep health check (recommended to add)
GET /health/deep
→ Checks: Ollama connectivity, model availability, disk space

# Ready check (for orchestration)
GET /ready
→ Returns: 200 if service can accept traffic, 503 otherwise
```

### Logging Strategy

```python
import logging
from pythonjsonlogger import jsonlogger

# Use JSON logging for easy parsing
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Log levels:
# DEBUG: Detailed diagnostic information
# INFO: General operational information
# WARNING: Warning messages for concerning situations
# ERROR: Serious errors that may require investigation
# CRITICAL: Critical errors that may cause service failure
```

## Load Shedding & Backpressure

### Recommended Implementation

```python
from collections import deque
from asyncio import BoundedSemaphore

class RequestQueue:
    def __init__(self, max_queue_size=100, max_concurrent=5):
        self.queue = deque(maxlen=max_queue_size)
        self.semaphore = BoundedSemaphore(max_concurrent)

    async def process(self, request):
        if len(self.queue) >= self.queue.maxlen:
            raise HTTPException(
                status_code=429,
                detail="Server too busy, try again later"
            )
        
        async with self.semaphore:
            return await self._handle_request(request)
```

## Testing Error Scenarios

### Unit Tests for Error Handling

```python
@patch('api_server.httpx.AsyncClient')
async def test_ollama_timeout(mock_client):
    """Test handling of Ollama timeout."""
    mock_client.post.side_effect = httpx.TimeoutException()
    
    with pytest.raises(HTTPException) as exc:
        await generate(GenerateRequest(prompt="test"))
    
    assert exc.value.status_code == 504

@patch('api_server.httpx.AsyncClient')
async def test_ollama_connection_error(mock_client):
    """Test handling of Ollama connection error."""
    mock_client.post.side_effect = httpx.ConnectError()
    
    with pytest.raises(HTTPException) as exc:
        await generate(GenerateRequest(prompt="test"))
    
    assert exc.value.status_code == 503
```

## Disaster Recovery

### Backup Plans

1. **Model Fallback** - If primary model fails, use alternative
2. **Read-Only Mode** - Serve cached responses if Ollama down
3. **Graceful Degradation** - Reduce max_tokens to save memory
4. **Manual Override** - Admin can manually restart services

### Data Backup

```bash
# Backup model cache
docker cp ollama:/root/.ollama /backup/.ollama-$(date +%s)

# Backup configuration
git commit -am "Backup: Current configuration"

# Backup logs
docker logs ollama-container > logs/ollama-$(date +%Y%m%d).log
```

## References

- [Resilience4j Patterns](https://resilience4j.readme.io/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Google SRE Book - Handling Overload](https://sre.google/sre-book/handling-overload/)
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)

---

Last updated: 2026-04-26
Version: 1.0.0
