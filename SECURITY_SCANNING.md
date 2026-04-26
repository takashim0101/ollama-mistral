# Security Scanning Guide
# License: CC BY-NC-SA 4.0

This document provides detailed information about the automated security scanning integrated into the CI/CD pipeline.

## Overview

The project implements comprehensive security scanning across multiple layers:

```
Every Push/PR
    ↓
┌─────────────────────────────────────────────────┐
│  1. Dependency Scanning (Safety + pip-audit)   │
│     └─ Checks requirements-api.txt              │
├─────────────────────────────────────────────────┤
│  2. Container Scanning (Trivy)                  │
│     └─ Scans Docker image + filesystem          │
├─────────────────────────────────────────────────┤
│  3. Secret Detection (TruffleHog)               │
│     └─ Scans entire git history                 │
├─────────────────────────────────────────────────┤
│  4. Code Security (Bandit)                      │
│     └─ Checks Python code for vulnerabilities   │
└─────────────────────────────────────────────────┘
    ↓
All checks must PASS before merge
    ↓
Results visible in GitHub Security tab
```

## 1. Dependency Scanning

### Tools

**Safety**
- Checks against SafetyDB (NVD, CVE databases)
- Fails build on HIGH/CRITICAL vulnerabilities
- Command: `safety check --json`

**pip-audit**
- Checks multiple vulnerability databases
- Provides detailed descriptions
- Command: `pip-audit --desc`

### Running Locally

```bash
# Install tools
pip install safety pip-audit

# Run Safety check
safety check

# Run pip-audit with descriptions
pip-audit --desc

# Both should show no vulnerabilities
```

### Interpreting Results

```
Safety output:
  insecure-package==1.0.0 (2022-01-01)
    └─ CVE-XXXX-XXXXX: Description of vulnerability
    └─ Severity: HIGH
    └─ Affected: <1.1.0

Action: Update to version 1.1.0 or higher
```

### Update Process

```bash
# Update vulnerable package
pip install --upgrade insecure-package

# Verify fix
safety check
pip-audit

# Commit and push
git add requirements-api.txt
git commit -m "fix(deps): Update vulnerable dependency"
git push
```

## 2. Container Scanning

### Trivy

Comprehensive vulnerability scanner for containers:

**Scans**
- OS packages (apt, apk, etc.)
- Application dependencies
- Misconfigurations in Dockerfile
- Secrets in images

**Severity Levels**
- CRITICAL - Immediate action required
- HIGH - Address soon
- MEDIUM - Monitor and plan
- LOW - Keep track
- UNKNOWN - Insufficient information

### Running Locally

```bash
# Install Trivy
# macOS: brew install trivy
# Linux: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan Docker image
trivy image docker.io/takam0101/ollama-api:latest

# Scan filesystem
trivy fs .

# Generate SARIF report
trivy image -f sarif -o trivy-results.sarif docker.io/takam0101/ollama-api:latest
```

### Interpreting Results

```
Database Checks:
  Library Name: python-requests
  Library Version: 2.31.0
  Vulnerability ID: CVE-XXXX-XXXXX
  Severity: MEDIUM
  Description: Vulnerability in requests library
  Fix Version: 2.32.0
```

## 3. Secret Detection

### TruffleHog

Detects accidentally committed secrets:

**Detects**
- AWS keys
- GitHub tokens
- Private keys
- API keys
- Database credentials
- Slack webhooks

### Running Locally

```bash
# Install TruffleHog
pip install trufflesecurity-trufflehog

# Scan entire repo history
trufflehog git file:// --only-verified --fail

# Scan specific commit range
trufflehog git file:// --since-commit HEAD~10 --only-verified

# Scan filesystem
trufflehog filesystem .
```

### Prevention

1. **Pre-commit hook** (recommended)
   ```bash
   pip install detect-secrets
   detect-secrets scan > .secrets.baseline
   git add .secrets.baseline
   ```

2. **Git config**
   ```bash
   git config --global core.hooksPath .githooks
   ```

3. **Use GitHub's secret detection**
   - Go to Settings → Code security and analysis
   - Enable "Secret scanning"

### If Secret Leaked

1. **Immediately regenerate** the secret/token/key
2. **Audit usage logs** for abuse
3. **Rotate** across all systems
4. **Force push** to remove from history (if in public repo):
   ```bash
   git filter-branch --index-filter \
     'git rm --cached --ignore-unmatch path/to/secret' \
     HEAD
   git push origin HEAD --force
   ```
5. **Notify security team** of the incident

## 4. Code Security Scanning

### Bandit

Scans Python code for security issues:

**Detects**
- Hardcoded credentials
- SQL injection risks
- Insecure deserialization (pickle)
- Weak cryptography
- Process injection risks
- Insecure random number generation

### Running Locally

```bash
# Install Bandit
pip install bandit

# Scan single file
bandit api_server.py

# Scan directory
bandit -r api_server.py tests/

# Generate JSON report
bandit -r api_server.py -f json -o bandit-report.json

# Scan with all tests enabled
bandit -r api_server.py -ll  # Show LOW severity and above
```

### Common Issues & Fixes

**Issue: Hardcoded password**
```python
# BAD
password = "secret123"

# GOOD
import os
password = os.getenv('DB_PASSWORD')
```

**Issue: SQL injection**
```python
# BAD
query = f"SELECT * FROM users WHERE id={user_id}"

# GOOD
cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
```

**Issue: Insecure deserialization**
```python
# BAD
import pickle
data = pickle.loads(user_input)

# GOOD
import json
data = json.loads(user_input)
```

## 5. Security Dashboard

### GitHub Security Tab

View all security scanning results:

1. Go to repository → **Security** tab
2. Click **Code scanning**
3. See all security issues

### Understanding SARIF Reports

SARIF (Static Analysis Results Format) contains:
- Tool name (Trivy, Bandit, etc.)
- Rule ID (CVE, CWE number)
- Severity level
- Location in code
- Remediation steps

### Setting Up Alerts

1. Go to **Settings → Code security and analysis**
2. Enable:
   - Dependabot alerts
   - Dependabot security updates
   - Secret scanning
   - Code scanning (via Actions)
3. Configure notification preferences

## 6. Continuous Monitoring

### Weekly Scheduled Scan

The security workflow runs weekly (Sundays at midnight UTC):

```yaml
schedule:
  - cron: '0 0 * * 0'  # Weekly
```

This catches newly discovered vulnerabilities even without code changes.

### Enabling Automated Fixes

1. Go to **Settings → Code security and analysis**
2. Under Dependabot:
   - Enable "Dependabot alerts"
   - Enable "Dependabot security updates"
3. Create PR rules:
   - Auto-merge patch updates: Yes
   - Auto-merge minor updates: Optional
   - Schedule: Daily

## 7. Incident Response

### If CI Fails Due to Security

```bash
# Step 1: Check which tool failed
# Look at GitHub Actions logs

# Step 2: Run locally to understand issue
safety check
pip-audit --desc
trivy fs .
bandit -r api_server.py

# Step 3: Fix the issue
# - Update dependency, or
# - Fix code security issue, or
# - Remove accidentally committed secret

# Step 4: Commit and push
git add .
git commit -m "fix(security): Resolve XXX vulnerability"
git push

# Step 5: Monitor CI to confirm all checks pass
```

### Escalation Path

1. **Low/Medium vulnerabilities**: File issue, plan fix
2. **High vulnerabilities**: Fix immediately, deploy patch
3. **Critical vulnerabilities**: Drop everything, fix now
4. **Leaked secrets**: Rotate immediately, investigate

## 8. Best Practices

### For Developers

- ✓ Run `safety check` before pushing
- ✓ Run `bandit -r .` on your code
- ✓ Never hardcode credentials
- ✓ Use environment variables for secrets
- ✓ Keep dependencies updated
- ✓ Review security warnings carefully
- ✓ Ask questions about CVEs you don't understand

### For DevOps/Security Teams

- ✓ Monitor GitHub Security dashboard daily
- ✓ Review SARIF reports weekly
- ✓ Update vulnerability databases (automatic in tools)
- ✓ Establish SLA for vulnerability fixes
- ✓ Document security decisions
- ✓ Perform quarterly security audits

### For CI/CD

- ✓ Fail pipeline on CRITICAL/HIGH vulnerabilities
- ✓ Report results to GitHub Security tab
- ✓ Archive SARIF reports for compliance
- ✓ Monitor scan execution time
- ✓ Alert team on repeated failures

## 9. Compliance

### Standards Covered

- **OWASP Top 10** - Web app security
- **CWE Top 25** - Most dangerous weaknesses
- **CVE** - Known vulnerabilities
- **NIST Cybersecurity Framework** - Risk management

### Audit Trail

All scanning activities are logged:
- GitHub Actions execution logs
- SARIF reports in GitHub Security
- Dependency update history
- Commit messages

### Reporting

Generate security report:

```bash
# Show all security findings
gh api repos/:owner/:repo/code-scanning/alerts

# Export for compliance audit
gh api repos/:owner/:repo/code-scanning/alerts \
  --paginate > security-audit.json
```

## 10. Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Safety](https://safetycli.com/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [TruffleHog](https://github.com/trufflesecurity/trufflehog)
- [Bandit](https://bandit.readthedocs.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

Last updated: 2026-04-26
Version: 1.0.0
