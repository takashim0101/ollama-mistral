# Git Workflow Guide

## Branch Strategy (Git Flow)

```
main (production)
  ↑
  └── develop (staging)
       ↑
       └── feature/* (feature development)
            ├── feature/initial-setup
            ├── feature/add-monitoring
            └── feature/kubernetes-support
```

## Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature develop
```

### 2. Make Changes

```bash
git add .
git commit -m "feat: Add new feature"
```

### 3. Push Feature Branch

```bash
git push -u origin feature/my-feature
```

### 4. Create Pull Request (feature → develop)

```bash
gh pr create --base develop --head feature/my-feature \
  --title "feat: Add new feature" \
  --body "Description of changes"
```

### 5. Review & Merge to Develop

GitHub Actions runs tests automatically.

```bash
gh pr merge <PR_NUMBER> --merge --auto
```

### 6. Create Release PR (develop → main)

```bash
gh pr create --base main --head develop \
  --title "release: v1.0.0" \
  --body "Release notes"
```

### 7. Merge to Main

Once approved:

```bash
gh pr merge <PR_NUMBER> --merge --auto
```

## Commands Reference

### List Branches

```bash
git branch -a
```

### Switch Branch

```bash
git checkout develop
git checkout feature/my-feature
```

### Create & Push Branch

```bash
git checkout -b feature/new-feature
git push -u origin feature/new-feature
```

### View PRs

```bash
gh pr list
gh pr view <PR_NUMBER>
```

### Create PR

```bash
gh pr create --base develop --head feature/my-feature
```

### Merge PR

```bash
gh pr merge <PR_NUMBER> --merge
```

### Delete Branch

```bash
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

## Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation
- **style**: Code style (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvement
- **test**: Test addition/modification
- **chore**: Build, dependencies, etc.
- **ci**: CI/CD configuration

### Examples

```
feat(api): Add text generation endpoint
fix(docker): Resolve GPU memory leak
docs: Update README with examples
```

## Best Practices

1. **Commit Often**: Small, logical commits
2. **Descriptive Messages**: Clear commit messages
3. **Branch Protection**: Require PR reviews on `main` and `develop`
4. **CI/CD**: Run tests on all PRs
5. **Code Review**: Review PRs before merge
6. **Delete Branches**: Clean up after merge

## Useful Links

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow Model](https://nvie.com/posts/a-successful-git-branching-model/)
