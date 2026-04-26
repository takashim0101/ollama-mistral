# Ollama + Mistral 7B Local LLM Stack

[![CI - Build and Test](https://github.com/takashim0101/ollama-mistral/actions/workflows/ci.yml/badge.svg)](https://github.com/takashim0101/ollama-mistral/actions/workflows/ci.yml)
[![CD - Build and Push to Registry](https://github.com/takashim0101/ollama-mistral/actions/workflows/cd.yml/badge.svg)](https://github.com/takashim0101/ollama-mistral/actions/workflows/cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

A complete local LLM inference stack with GPU acceleration, Web UI, and REST API. Deploy, scale, and manage AI models entirely on your machine�no cloud dependencies, no API costs.A complete local LLM inference stack with GPU acceleration, Web UI, and REST API. Deploy, scale, and manage AI models entirely on your machine—no cloud dependencies, no API costs.

## Features

- **Ollama** - Mistral 7B model (4.4GB) with NVIDIA GPU acceleration
- **Open WebUI** - Browser-based chat interface
- **FastAPI Server** - Production-ready REST API with automatic documentation
- **GitHub Actions CI/CD** - Automated testing, building, and deployment
- **Production-Ready** - `.env` management, health checks, logging
- **Fully Private** - Runs completely offline, no data leaves your machine
- **Cost-Free** - Docker + Ollama + FastAPI = 100% free
- **Docker Hub Ready** - Pre-built image available at `docker.io/takam0101/ollama-api`

## Architecture

```
┌─────────────────┐
│   User/Client   │
└────────┬────────┘
         │
    ┌────┴─────────────┬────────────┐
    │                  │            │
    ▼                  ▼            ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Web UI     │  │ API Docs   │  │ Direct API │
│ :3000      │  │ :8000/docs │  │ :8000      │
└────────┬───┘  └────────┬───┘  └────────┬───┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                    ┌────▼──────┐
                    │ FastAPI   │
                    │ :8000     │
                    └────┬──────┘
                         │
                    ┌────▼──────────┐
                    │ Ollama Server  │
                    │ :11434         │
                    └────┬──────────┘
                         │
                    ┌────▼────────┐
                    │ Mistral 7B  │
                    │ GPU: RTX4060│
                    └─────────────┘
```

## Prerequisites

- Docker Desktop with GPU support enabled
- NVIDIA GPU (RTX 4060 or higher recommended)
- Minimum 8GB VRAM
- 10GB free disk space

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/takashim0101/ollama-mistral.git
cd ollama-mistral
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/macOS
pip install -r requirements-api.txt
```

### 2. Start Services

```bash
docker compose up -d
```

### 3. Access

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Base**: http://localhost:8000

## Verification Steps

After starting the services, follow these steps to verify that everything is working as expected:

1.  **Access Web UI:** Open your browser and navigate to `http://localhost:3000`. You should see the Open WebUI chat interface.
2.  **Access API Docs:** Open your browser and navigate to `http://localhost:8000/docs`. You should see the FastAPI interactive API documentation (Swagger UI).
3.  **Check API Health:** Run the following `curl` command in your terminal:
    ```bash
    curl http://localhost:8000/health
    ```
    You should receive a JSON response similar to:
    ```json
    {
      "status": "healthy",
      "environment": "development",
      "ollama_host": "ollama",
      "model": "mistral"
    }
    ```
4.  **Test Text Generation API:** Run the following `curl` command to test the text generation endpoint:
    ```bash
    curl -X POST http://localhost:8000/generate \
      -H "Content-Type: application/json" \
      -d '{"prompt": "What is Docker?"}'
    ```
    You should receive a JSON response containing generated text.

If you encounter any issues, please refer to the `## Troubleshooting` section or open an issue on GitHub.

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "development",
  "ollama_host": "ollama",
  "model": "mistral"
}
```

### Generate Text

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Docker?"}'
```

### Python Example

```python
import requests

response = requests.post('http://localhost:8000/generate', 
    json={'prompt': 'Explain machine learning in simple terms'}
)
print(response.json()['response'])
```

### JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: 'Hello!' })
});
const data = await response.json();
console.log(data.response);
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/health` | Health check |
| POST | `/generate` | Generate text |
| GET | `/models` | List available models |

## Configuration

This project uses environment variables for configuration. A template file, `.env.example`, is provided to show which variables are needed.

To get started, you must create your own environment file by copying the template.

1.  **Create Your Configuration File**

    Copy the `.env.example` file to a new file.
    *   For local development, name it `.env`:
        ```bash
        cp .env.example .env
        ```
    *   For a production environment, you should name it `.env.production`:
        ```bash
        cp .env.example .env.production
        ```

2.  **Edit the Values**

    Open your new `.env` or `.env.production` file and customize the values as needed. For production, it is **critical** to set a strong, random `WEBUI_SECRET_KEY`.

    > **Security Note:** These `.env` files contain sensitive information and are already listed in `.gitignore`. **Never commit them to your repository.**

### Running with Your Configuration

*   **For Development:** Docker Compose will automatically find and use the `.env` file.
    ```bash
    docker compose up -d
    ```

*   **For Production:** You must explicitly specify both the production compose file and your production environment file.
    ```bash
    docker compose -f docker-compose.prod.yml --env-file .env.production up -d
    ```

## Testing

### Unit Tests

Run unit tests (no Ollama service required):

```bash
pytest tests/test_api.py -v
```

All 11 unit tests use mocking and can run independently.

### Integration Tests

Run integration tests (requires Ollama service running):

```bash
pytest tests/test_ollama_integration.py -v
```

If Ollama is not available, this test will be automatically skipped.

### Run All Tests

```bash
pytest -v
```

This runs 12 tests total:
- 11 unit tests (always runs)
- 1 integration test (skipped if Ollama unavailable)

## Docker Deployment

### Using Pre-built Image from Docker Hub

The API server image is available on Docker Hub:

```bash
docker pull docker.io/takam0101/ollama-api:latest
```

Run the container:

```bash
docker run -d \
  -e OLLAMA_HOST=http://ollama:11434 \
  -p 8000:8000 \
  --name ollama-api \
  docker.io/takam0101/ollama-api:latest
```

### Building Locally

Build the API server image:

```bash
docker build -f Dockerfile.api -t ollama-api:latest .
```

The `.dockerignore` file is configured to exclude:
- Test files (`tests/`, `test_*`)
- Virtual environment (`venv/`)
- Cache directories (`__pycache__/`, `.pytest_cache/`)
- Development files (`.env`, `.git/`, `.gitignore`)
- Documentation files

This keeps the production image minimal and efficient.

## CI/CD Pipeline

### GitHub Actions Workflows

1. **CI** (`.github/workflows/ci.yml`)
   - Runs on: Push to `main` or `develop`, Pull requests
   - Tests Python dependencies
   - Linting (flake8)
   - Builds Docker images
   - Tests API endpoints

2. **CD** (`.github/workflows/cd.yml`)
   - Builds and pushes Docker images to GitHub Container Registry
   - Triggered on: Push to `main`, tag creation

3. **Deploy** (`.github/workflows/deploy.yml`)
   - Deploys to production via SSH
   - Triggered on: CD completion
   - Requires: `DEPLOY_KEY`, `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_PATH` secrets

4. **Security** (`.github/workflows/security.yml`)
   - Scans for vulnerabilities (Trivy)
   - Detects secrets (Trufflesecurity)
   - Checks Python dependencies
   - Scheduled weekly

### Setup GitHub Actions

1. Go to **Settings → Secrets and variables → Actions**
2. Add secrets:
   ```
   DEPLOY_HOST=your-server-ip
   DEPLOY_USER=deploy_user
   DEPLOY_KEY=<SSH_PRIVATE_KEY>
   DEPLOY_PATH=/home/deploy_user/ollama-mistral
   ```

See `CI_CD_SETUP.md` for detailed instructions.

## File Structure

```
.
├── .env                         # Development environment variables
├── .env.production              # Production environment variables
├── .dockerignore                # Docker build exclusions
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Ollama container
├── Dockerfile.api               # API server container
├── docker-compose.yml           # Development compose
├── docker-compose.prod.yml      # Production compose
├── docker-compose.override.yml  # Local development overrides
├── api_server.py                # FastAPI application
├── requirements-api.txt         # Python dependencies
├── tests/
│   ├── conftest.py              # pytest configuration & fixtures
│   ├── test_api.py              # Unit tests (11 tests)
│   ├── test_ollama_integration.py # Integration test (requires Ollama)
│   └── __init__.py
├── .github/workflows/           # GitHub Actions CI/CD
│   ├── ci.yml
│   ├── cd.yml
│   ├── deploy.yml
│   └── security.yml
├── CI_CD_SETUP.md               # CI/CD documentation
├── GIT_WORKFLOW.md              # Git workflow guide
└── README.md                    # This file
```

## Performance

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | 6GB VRAM | 8GB+ VRAM |
| RAM | 8GB | 16GB |
| CPU | 4 cores | 8+ cores |
| Disk | 10GB | 20GB |
| Network | For model download only | Broadband |

### Inference Speed

On RTX 4060 (8GB):
- **First token**: ~500ms
- **Tokens/second**: ~10-15 tokens/sec
- **Batch size**: 1 (recommended)

## Troubleshooting

### Container Won't Start

```bash
docker compose logs ollama
docker compose logs api-server
docker compose logs web-ui
```

### GPU Not Recognized

```bash
docker run --rm --runtime=nvidia nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Out of Memory

Mistral 7B requires ~8GB VRAM. Check:
```bash
nvidia-smi
```

### API Timeout

Increase timeout in requests:
```python
requests.post('http://localhost:8000/generate',
    json={'prompt': 'Hello'},
    timeout=600  # 10 minutes
)
```

### Web UI Connection Refused

```bash
# Check if container is running
docker ps | grep ollama-webui

# Check logs
docker logs ollama-webui

# Restart
docker compose restart web-ui
```

### Tests Fail Due to Connection Error

If pytest hangs or shows connection errors:

1. Ensure Ollama service is running:
   ```bash
   docker compose up -d ollama
   ```

2. Unit tests should always pass (they use mocks):
   ```bash
   pytest tests/test_api.py -v
   ```

3. Integration test skips automatically if Ollama is unavailable:
   ```bash
   pytest tests/test_ollama_integration.py -v
   ```

## Production Deployment

### AWS EC2

```bash
# On EC2 instance with GPU (g4dn.xlarge or similar)
git clone https://github.com/takashim0101/ollama-mistral.git
cd ollama-mistral
docker compose -f docker-compose.prod.yml up -d
```

### Azure

Use ACI with GPU support or VM with NVIDIA GPU drivers.

### Self-Hosted

Deploy to any server with:
- Docker + Docker Compose
- NVIDIA GPU + CUDA drivers
- SSH access for CI/CD

## Security

- ✓ `.env` files excluded from Git (see `.gitignore`)
- ✓ `.dockerignore` excludes development files and tests from production images
- ✓ Health checks on all containers
- ✓ Logging configured (JSON format)
- ✓ Non-root user capable
- ✓ GitHub Actions security scanning
- ✓ Error handling for malformed Ollama responses

## Monitoring

### Logs

```bash
docker compose logs -f api-server
docker compose logs -f ollama
docker compose logs -f web-ui
```

### Health

```bash
curl http://localhost:8000/health
docker stats
```

## Contributing

Pull requests welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest -v`
4. Commit changes
5. Push and create a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: https://github.com/takashim0101/ollama-mistral/issues
- **Discussions**: https://github.com/takashim0101/ollama-mistral/discussions
- **Docker Hub**: https://hub.docker.com/r/takam0101/ollama-api

## References

- [Ollama](https://ollama.ai)
- [Open WebUI](https://github.com/open-webui/open-webui)
- [FastAPI](https://fastapi.tiangolo.com)
- [Docker](https://www.docker.com)
- [GitHub Actions](https://github.com/features/actions)

## Roadmap

- [ ] Support for additional models (Llama 2, Neural Chat)
- [ ] Multi-GPU support
- [ ] Model quantization optimization
- [ ] Kubernetes deployment templates
- [ ] Prometheus monitoring integration
- [ ] OpenTelemetry tracing
- [ ] RAG (Retrieval Augmented Generation) support

---

**Made with ❤️ for the open-source AI community**

