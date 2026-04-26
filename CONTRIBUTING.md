# Contributing to Ollama Mistral 7B

Thank you for your interest in contributing! We welcome contributions from everyone.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/ollama-mistral.git
cd ollama-mistral
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name develop
```

### 3. Set Up Development Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/macOS
pip install -r requirements-api.txt
```

### 4. Make Changes

Follow the coding standards below.

### 5. Test Locally

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=api_server tests/
```

### 6. Run Linting

```bash
flake8 api_server.py --max-line-length=127
```

## Commit Guidelines

Use conventional commits for clear commit messages:

```bash
git commit -m "type(scope): description"
```

### Types
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style (formatting, missing semicolons, etc.)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Adding or updating tests
- `chore:` Build process, dependencies, etc.
- `ci:` CI/CD configuration changes

### Examples
```bash
git commit -m "feat(api): Add streaming response support"
git commit -m "fix(docker): Resolve GPU memory leak in Ollama container"
git commit -m "docs: Update README with new API examples"
git commit -m "test: Add integration tests for error handling"
```

## Pull Request Process

1. **Ensure all tests pass** — Run `pytest -v` locally
2. **Update documentation** — Update README or relevant docs
3. **Follow commit conventions** — Use clear, descriptive commit messages
4. **Create PR against `develop`** — Never PR directly to `main`
5. **Request review** — Reference related issues (e.g., "Closes #123")
6. **Address feedback** — Respond to reviewer comments promptly

## PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Feature (new functionality)
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring

## Related Issues
Closes #123

## Testing
- [ ] All tests pass locally
- [ ] New tests added (if applicable)

## Checklist
- [ ] Code follows style guide
- [ ] No hardcoded secrets
- [ ] Comments added for complex logic
- [ ] README updated (if needed)
```

## Coding Standards

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation
- Maximum line length: 127 characters
- Use type hints where possible

### Example
```python
from typing import Optional

async def generate_text(
    prompt: str,
    max_tokens: int = 50
) -> dict[str, str]:
    """Generate text using Ollama model.
    
    Args:
        prompt: Input text prompt
        max_tokens: Maximum tokens to generate
        
    Returns:
        Dictionary with 'response' and 'model' keys
    """
    # Implementation
    return {"response": "", "model": "mistral"}
```

### Docker Best Practices
- Use multi-stage builds for smaller images
- Pin base image versions
- Run containers as non-root users
- Use `.dockerignore` to exclude unnecessary files

### Testing
- Aim for >80% code coverage
- Write unit tests for all functions
- Use mocking for external dependencies
- Test error cases and edge cases

```python
import pytest

def test_generate_text_valid_prompt():
    """Test text generation with valid prompt."""
    response = requests.post('/generate', json={'prompt': 'Hello'})
    assert response.status_code == 200
    assert 'response' in response.json()

def test_generate_text_invalid_prompt():
    """Test text generation with invalid prompt."""
    response = requests.post('/generate', json={})
    assert response.status_code == 422  # Unprocessable Entity
```

## Security

- Never commit secrets, API keys, or tokens
- Use `.env` files for sensitive data (already in `.gitignore`)
- Review SECURITY.md for security guidelines
- Report vulnerabilities privately (see SECURITY.md)

## Documentation

- Update README for user-facing changes
- Add docstrings to all functions
- Update CI_CD_SETUP.md for workflow changes
- Keep examples current and tested

## Branch Protection Rules

The `main` branch is protected:
- ✓ Requires PR review before merge
- ✓ Requires status checks to pass (CI/CD)
- ✓ Requires branches to be up to date

## Workflow

```
1. Create feature branch from develop
   ↓
2. Make changes & commit
   ↓
3. Push and create PR to develop
   ↓
4. GitHub Actions runs automatically
   ├─ Linting
   ├─ Unit tests
   ├─ Integration tests
   ├─ Docker build
   ↓
5. Code review & approval
   ↓
6. Merge to develop
   ↓
7. Create release PR: develop → main
   ↓
8. Merge to main (triggers CD)
```

## Reporting Issues

### Bug Reports
- Use the bug report template
- Include steps to reproduce
- Attach error logs
- Specify your environment

### Feature Requests
- Use the feature request template
- Explain the use case
- Discuss alternative solutions
- Consider backwards compatibility

## Getting Help

- Check existing issues and discussions
- Review documentation in README.md
- Read through CI_CD_SETUP.md for workflow details
- Email the maintainer for security issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in the project README and commit history.

Thank you for contributing! 🎉
