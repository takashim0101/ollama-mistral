# DevSecOps Policy

This document outlines the security practices and policies for the Ollama Mistral 7B project.

## Security Overview

This project implements a comprehensive DevSecOps strategy covering:
- Dependency scanning and vulnerability management
- Container image scanning
- Secret detection
- Code quality and security linting
- Production deployment approval process
- Incident response procedures

## 1. Dependency Security

### Scanning Tools

**Safety** - High-level vulnerability scanning
- Checks Python packages against known vulnerability databases
- Runs on every push to main/develop
- Fails pipeline if vulnerabilities are found
- Command: `safety check`

**pip-audit** - Detailed auditing tool
- Provides detailed descriptions of vulnerabilities
- Checks multiple vulnerability databases
- Integrated into CI/CD pipeline
- Command: `pip-audit --desc`

### Practices

- ✓ All dependencies pinned to exact versions in `requirements-api.txt`
- ✓ Regular updates (at least monthly)
- ✓ Security alerts enabled on GitHub
- ✓ Automatic dependency updates via Dependabot (recommended)

### Update Process

```bash
# 1. Update requirements locally
pip install --upgrade pip
pip install -r requirements-api.txt --upgrade

# 2. Run security checks
safety check
pip-audit --desc

# 3. Run tests
pytest -v

# 4. Commit and push
git commit -m "chore(deps): Update dependencies with security patches"
git push
```

## 2. Container Security

### Image Scanning

**Trivy** - Comprehensive vulnerability scanner
- Scans for:
  - OS package vulnerabilities
  - Application vulnerabilities
  - Misconfigurations
  - Secrets in images
- Severity levels: CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN
- Results uploaded to GitHub Security tab (SARIF format)

### Dockerfile Best Practices

✓ **Non-root user execution**
```dockerfile
RUN useradd -m appuser
USER appuser
```

✓ **Multi-stage builds** (if applicable)
- Reduces final image size
- Minimizes attack surface

✓ **Health checks**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1
```

✓ **Pinned base image versions**
```dockerfile
FROM python:3.12.2-slim  # NOT: FROM python:3.12
```

✓ **No hardcoded secrets**
- Use environment variables only
- Never include API keys or tokens in Dockerfile

## 3. Secret Detection

### TruffleHog

Detects accidentally committed secrets including:
- API keys and tokens
- Private keys
- Database credentials
- AWS keys
- Slack webhooks

**Configuration**
- Scans entire git history
- Verified results only (reduces false positives)
- Fails build if secrets detected
- Runs on every push and PR

### Best Practices

1. **Never commit secrets** - Use `.env` files
2. **Pre-commit hooks** - Consider using `git-secrets`:
   ```bash
   git secrets --install
   git secrets --register-aws
   ```
3. **Rotate exposed credentials** - If secrets leak:
   1. Regenerate immediately
   2. Audit usage logs
   3. Update all systems
   4. Notify security team

## 4. Code Quality & Security

### Flake8 - Code Quality
- Enforces PEP 8 style guide
- Catches syntax errors
- Max line length: 127 characters
- Complexity checks

### Bandit - Security Linting
Detects common security issues:
- Hardcoded credentials
- SQL injection risks
- Insecure random number generation
- Pickle usage vulnerabilities
- Command injection risks

### Running Locally

```bash
# Code quality
flake8 api_server.py tests/

# Security linting
bandit -r api_server.py tests/
```

## 5. Production Deployment

### Approval Process

All production deployments require:
1. ✓ All CI checks passing (lint, build, test, security)
2. ✓ Manual approval from authorized reviewer
3. ✓ Pre-deployment security verification
4. ✓ Signed commits (recommended)

### Workflow

1. **Staging Deployment** - Automatic (no approval required)
   ```bash
   gh workflow run deploy.yml -f environment=staging -f version=main
   ```

2. **Production Deployment** - Requires approval
   ```bash
   gh workflow run deploy.yml -f environment=production -f version=v1.0.0
   ```

### Deployment Checklist

- [ ] All tests passing
- [ ] Security scans clean
- [ ] Dependencies updated
- [ ] Changelog updated
- [ ] Version tag created
- [ ] Approval obtained
- [ ] Rollback plan documented

## 6. Monitoring & Incident Response

### Continuous Monitoring

After deployment:
1. Monitor application logs for errors
2. Check health endpoints
3. Review security alerts
4. Monitor resource usage

### Incident Response

If a security issue is discovered:
1. Immediately report (see SECURITY.md)
2. Assess impact and severity
3. Develop fix
4. Test thoroughly
5. Deploy patch
6. Post-mortem analysis

## 7. Compliance

### Standards

- **OWASP Top 10** - Web application security risks
- **CWE Top 25** - Most dangerous software weaknesses
- **PEP 8** - Python style guide
- **Docker Best Practices** - Container security

### Audit Trail

All deployments include:
- Who deployed (GitHub Actions logs)
- What was deployed (image SHA)
- When it was deployed (timestamp)
- Why (commit message and PR reference)

## 8. Security Team Responsibilities

### Regular Tasks

- **Monthly**: Review and update dependencies
- **Quarterly**: Security assessment and gap analysis
- **Annually**: Penetration testing (recommended)

### Approval Team

Current authorized approvers:
- @takashim0101 (Project Lead)

To add approvers:
1. Update `.github/CODEOWNERS` - production environment
2. Update GitHub environment settings

## 9. Third-Party Security

### GitHub Actions

- All actions pinned to major version (e.g., `@v3`)
- Regularly reviewed for security updates
- Limited permissions per job

### Secret Management

Secrets stored in GitHub:
- `DOCKER_USERNAME` - Docker Hub credentials
- `DOCKER_PASSWORD` - Docker access token
- `DEPLOY_KEY` - SSH private key
- `DEPLOY_HOST` - Production server
- `SNYK_TOKEN` - Snyk API token (optional)

Rotate secrets:
- Quarterly for long-term credentials
- Immediately if compromised

## 10. References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Docker Benchmark](https://www.cisecurity.org/cis-benchmarks/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)

---

Last updated: 2026-04-26
Version: 1.0.0
