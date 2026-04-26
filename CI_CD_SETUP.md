# GitHub Actions CI/CD Setup Guide

## CI/CD Pipeline

### 1. CI - Build and Test (`ci.yml`)
- Runs on commit/PR
- Installs Python dependencies
- Linting (flake8)
- Runs pytest (unit tests + integration tests)
- Builds Docker image
- Starts with Docker Compose
- Tests API endpoints

**Triggers:**
- Push to `main` branch
- Push to `develop` branch
- PR creation

### 2. CD - Build and Push (`cd.yml`)
- Builds Docker image
- Pushes to GitHub Container Registry (ghcr.io)
- Pushes to Docker Hub (optional)

**Triggers:**
- Push to `main` branch
- On tag creation (e.g., v1.0.0)

### 3. Deploy - Production (`deploy.yml`)
- Deploys to production server after CD completes
- Connects to production machine via SSH
- Starts with Docker Compose
- Sends Slack notification

**Triggers:**
- On completion of CD workflow

## Setup Steps

### Step 1: Create a GitHub Repository

```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/ollama-mistral.git
git branch -M main
git add .
git commit -m "Initial commit: Ollama + Mistral 7B setup"
git push -u origin main
```

### Step 2: Configure GitHub Secrets

In your repository's `Settings → Secrets and variables → Actions`, add the following:

#### Docker Hub (Optional)
```
DOCKER_USERNAME = your_docker_username
DOCKER_PASSWORD = your_docker_token
```

#### For Production Deployment
```
DEPLOY_HOST = your-server-ip-or-domain.com
DEPLOY_USER = deploy_user
DEPLOY_KEY = (SSH private key)
DEPLOY_PATH = /home/deploy_user/ollama-mistral
```

#### Slack Notification (Optional)
```
SLACK_WEBHOOK_URL = https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 3: Generate SSH Key Pair (for Production Deployment)

```bash
ssh-keygen -t ed25519 -f deploy_key -N ""
```

- `deploy_key` — Register as `DEPLOY_KEY` in GitHub Secrets
- `deploy_key.pub` — Add to `~/.ssh/authorized_keys` on the production server

### Step 4: Prepare the Production Server

```bash
# On the production server
mkdir -p /home/deploy_user/ollama-mistral
cd /home/deploy_user/ollama-mistral

# Check if Docker and Docker Compose are installed
docker --version
docker compose --version

# Initialize Git repository
git clone https://github.com/YOUR_USERNAME/ollama-mistral.git .
cp .env.production .env
```

## Testing in CI/CD

The CI pipeline automatically runs all tests:

```bash
pytest -v
```

This includes:
- **11 unit tests** from `tests/test_api.py` — Always run, use mocking
- **1 integration test** from `tests/test_ollama_integration.py` — Skipped if Ollama unavailable

If you want to skip integration tests in CI (recommended for faster builds), update your CI workflow:

```yaml
- name: Run tests
  run: pytest tests/test_api.py -v
```

## Workflow Execution Flow

```
1. Commit push
   ↓
2. GitHub Actions CI runs
   - Installs dependencies
   - Runs linting (flake8)
   - Runs pytest (unit + integration tests)
   - Build ✓
   ↓
3. CD workflow runs
   - Builds Docker image
   - Pushes to ghcr.io ✓
   ↓
4. Deploy workflow runs
   - SSH into production server
   - git pull
   - docker compose pull && docker compose up -d
   - Restart containers ✓
   ↓
5. Slack notification (deployment complete)
```

## Checking GitHub Actions Status

In your repository's `Actions` tab, you will see:

- ✓ CI pipeline execution status
- ✓ Test results
- ✓ Build status
- ✓ Deployment history

## Troubleshooting

### If CI fails
```bash
# Test locally
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements-api.txt
pytest -v
```

### If tests timeout
- Unit tests should complete in <10s
- Integration tests may timeout if Ollama isn't running
- Check that Ollama container is healthy in the CI environment

### If CD fails
- Check if Secrets are configured correctly
- Check if Docker Hub credentials are correct
- Verify Docker image builds locally: `docker build -f Dockerfile.api -t ollama-api .`

### If Deploy fails
- Check if SSH key is configured correctly
- Check if the production server is running
- Check if `DEPLOY_PATH` exists and is accessible
- Verify SSH connectivity: `ssh -i deploy_key deploy_user@DEPLOY_HOST`

## Production Environment Checklist

- [ ] Generate SSH key pair
- [ ] Configure GitHub Secrets
- [ ] Confirm SSH access to the production server
- [ ] Docker Compose is installed on production
- [ ] Copy `.env.production` to the production server
- [ ] Configure firewall (port exposure)
- [ ] Verify Docker Hub credentials (if pushing there)
- [ ] Test CI/CD pipeline with a dummy commit

## Docker Image Versioning

For better image management, tag your builds:

```yaml
# In cd.yml workflow
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    tags: |
      docker.io/YOUR_USERNAME/ollama-api:latest
      docker.io/YOUR_USERNAME/ollama-api:${{ github.sha }}
      docker.io/YOUR_USERNAME/ollama-api:${{ github.ref_name }}
```

This allows you to:
- Always have a `latest` tag
- Track specific commits with SHA tags
- Use version tags (v1.0.0)

## Production Deployment Approval

### Deployment with Approval Gate

Production deployments require manual approval via GitHub Environments:

```bash
# Trigger production deployment
gh workflow run deploy.yml \
  -f environment=production \
  -f version=v1.0.0
```

The workflow will:
1. **Pre-deployment checks** - Verify all tests pass and security scans are clean
2. **Request approval** - GitHub notifies reviewers
3. **Await approval** - Blocks until manually approved
4. **Deploy** - Pushes image and deploys to production
5. **Verify** - Runs health checks

### Staging Deployment (Automatic)

Staging deployments require no approval:

```bash
gh workflow run deploy.yml \
  -f environment=staging \
  -f version=main
```

Deploys immediately after pre-deployment checks pass.

### Environment Configuration

Configure approval reviewers in GitHub:

1. Go to **Settings → Environments → production-approval**
2. Under "Deployment branches", select which branches can deploy
3. Under "Deployment protection rules**, add required reviewers
4. Set timeout (default: 30 days)

## Security Integration

The deployment workflow integrates with security scanning:

- ✓ Fails if dependency vulnerabilities found (Safety + pip-audit)
- ✓ Fails if container vulnerabilities found (Trivy)
- ✓ Fails if secrets detected in codebase (TruffleHog)
- ✓ Fails if code security issues found (Bandit)
- ✓ Requires signed commits (recommended)

All security scans must pass before approval is even requested.

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Docker setup-buildx-action](https://github.com/docker/setup-buildx-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Hub](https://docs.docker.com/docker-hub/)
- [DEVSECOPS.md](./DEVSECOPS.md) - Detailed security policy

