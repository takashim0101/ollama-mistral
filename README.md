# Ollama + Mistral 7B Local LLM Stack

A complete local LLM inference stack with GPU acceleration, Web UI, and REST API. Deploy, scale, and manage AI models entirely on your machine—no cloud dependencies, no API costs.

## Features

- **Ollama** - Mistral 7B model (4.4GB) with NVIDIA GPU acceleration
- **Open WebUI** - Browser-based chat interface
- **FastAPI Server** - Production-ready REST API with automatic documentation
- **GitHub Actions CI/CD** - Automated testing, building, and deployment
- **Production-Ready** - `.env` management, health checks, logging
- **Fully Private** - Runs completely offline, no data leaves your machine
- **Cost-Free** - Docker + Ollama + FastAPI = 100% free

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

### Development

Edit `.env`:
```env
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=mistral
WEBUI_PORT=3000
API_PORT=8000
APP_ENV=development
```

### Production

Edit `.env.production`:
```env
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=mistral
WEBUI_PORT=3000
API_PORT=8000
APP_ENV=production
WEBUI_SECRET_KEY=your-strong-secret-key
```

Deploy:
```bash
docker compose -f docker-compose.prod.yml up -d
```

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
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Ollama container
├── Dockerfile.api               # API server container
├── docker-compose.yml           # Development compose
├── docker-compose.prod.yml      # Production compose
├── api_server.py                # FastAPI application
├── test_ollama.py               # Test script
├── requirements-api.txt         # Python dependencies
├── .github/workflows/           # GitHub Actions CI/CD
│   ├── ci.yml
│   ├── cd.yml
│   ├── deploy.yml
│   └── security.yml
├── CI_CD_SETUP.md               # CI/CD documentation
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
- ✓ Health checks on all containers
- ✓ Logging configured (JSON format)
- ✓ Non-root user capable
- ✓ GitHub Actions security scanning

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
3. Commit changes
4. Push and create a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: https://github.com/takashim0101/ollama-mistral/issues
- **Discussions**: https://github.com/takashim0101/ollama-mistral/discussions

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
