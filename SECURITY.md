# Security Policy
# License: CC BY-NC-SA 4.0

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please do **NOT** open a public GitHub issue. Instead, please report it responsibly by sending an email to the maintainers.

### How to Report

1. **Email**: Send a detailed report to the project maintainer
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce (if applicable)
   - Potential impact
   - Suggested fix (if available)

3. **Response Time**: We aim to respond within 48 hours

## Security Considerations

### Development Environment
- Never commit `.env` files with real secrets
- Use `.env.example` as a template
- All environment variables are excluded via `.gitignore`

### Production Environment
- All containers run with non-root users when possible
- Docker images are regularly updated
- Use strong, randomly generated secrets for `WEBUI_SECRET_KEY`
- Enable HTTPS/TLS in production deployments
- Configure firewall rules appropriately

### API Security
- All endpoints validate input
- Error messages don't expose sensitive details
- Logging is configured to exclude sensitive data
- Health checks verify service availability

### CI/CD Security
- GitHub Secrets are used for sensitive credentials
- Docker images are scanned for vulnerabilities (Trivy)
- Dependencies are checked for known vulnerabilities (Trufflesecurity)
- All workflows require authentication

## Dependencies

This project uses:
- **FastAPI** - Web framework
- **Ollama** - LLM inference engine
- **Docker** - Containerization
- **pytest** - Testing framework
- **httpx** - HTTP client

All dependencies are pinned in `requirements-api.txt` to prevent supply chain attacks.

## Best Practices

### For Contributors
- Keep dependencies up to date: `pip install --upgrade-all`
- Run local tests before pushing: `pytest -v`
- Review security scanning results in GitHub Actions
- Never hardcode secrets in code

### For Deployments
- Use strong, unique secrets for each environment
- Regularly rotate API keys and tokens
- Monitor container logs for suspicious activity
- Keep Docker and base images updated
- Use read-only file systems where possible

## Security Scanning

This project has automated security checks:

1. **Dependency Scanning** - Detects known vulnerabilities in dependencies
2. **Container Scanning** - Scans Docker images with Trivy
3. **Secret Detection** - Detects accidentally committed secrets
4. **Code Analysis** - Runs flake8 for code quality

These checks run on every push and pull request to `main` and `develop` branches.

## Version History

| Version | Date | Security Update |
|---------|------|-----------------|
| 1.0.0 | 2026-04-26 | Initial release |

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
