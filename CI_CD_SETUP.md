# GitHub Actions CI/CD Setup Guide

## CI/CD Pipeline

### 1. CI - Build and Test (`ci.yml`)
- Runs on commit/PR
- Installs Python dependencies
- Linting (flake8)
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

## Workflow Execution Flow

```
1. Commit push
   ↓
2. GitHub Actions CI runs
   - Tests ✓
   - Build ✓
   ↓
3. CD workflow runs
   - Builds Docker image
   - Pushes to ghcr.io ✓
   ↓
4. Deploy workflow runs
   - SSH into production server
   - git pull
   - docker compose update
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
docker compose up -d --wait
curl http://localhost:8000/health
```

### If CD fails
- Check if Secrets are configured correctly
- Check if Docker Hub credentials are correct

### If Deploy fails
- Check if SSH key is configured correctly
- Check if the production server is running
- Check if `DEPLOY_PATH` exists

## Production Environment Checklist

- [ ] Generate SSH key pair
- [ ] Configure GitHub Secrets
- [ ] Confirm SSH access to the production server
- [ ] Docker Compose is installed on production
- [ ] Copy `.env.production` to the production server
- [ ] Configure firewall (port exposure)

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker setup-buildx-action](https://github.com/docker/setup-buildx-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)