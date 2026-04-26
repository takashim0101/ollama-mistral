# Branch Protection Rules Configuration

To set up branch protection and ensure professional code quality, follow these steps:

## GitHub Branch Protection Setup

### Step 1: Navigate to Repository Settings

1. Go to your repository on GitHub
2. Click **Settings** (gear icon)
3. Click **Branches** in the left sidebar
4. Click **Add rule** under "Branch protection rules"

### Step 2: Protect Main Branch

**Pattern to protect:** `main`

**Enable the following:**

#### ✓ Require a pull request before merging
- [x] Require approvals
  - Number of approvals required: **1**
- [x] Dismiss stale pull request approvals when new commits are pushed
- [x] Require review from code owners
- [x] Require approval of the most recent reviewable push

#### ✓ Require status checks to pass before merging
- [x] Require branches to be up to date before merging
- [x] Status checks that must pass:
  - `lint` (from CI workflow)
  - `build` (from CI workflow)
  - `test` (from CI workflow)

#### ✓ Require branches to be up to date before merging
- [x] Checked

#### ✓ Require conversation resolution before merging
- [x] Checked

#### ✓ Include administrators
- [x] Include administrators
  - This ensures even admins must follow the rules

### Step 3: Protect Develop Branch (Optional but Recommended)

**Pattern to protect:** `develop`

**Enable:**
- [x] Require a pull request before merging
- [x] Require approvals (1)
- [x] Require status checks to pass
  - Same checks as main

### Step 4: Create CODEOWNERS File

The `.github/CODEOWNERS` file has already been created. It specifies:
- Who must review PRs for specific files
- Automatically requests reviews from code owners

**Location:** `.github/CODEOWNERS`

**Effect:**
- When someone opens a PR, code owners are automatically requested as reviewers
- PR cannot be merged without their approval

### Step 5: Configure GitHub Secrets (for CI/CD)

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**

**Required secrets:**

```
DOCKER_USERNAME = your_docker_username
DOCKER_PASSWORD = your_docker_access_token
```

**Optional for deployment:**

```
DEPLOY_HOST = your-production-server.com
DEPLOY_USER = deploy_user
DEPLOY_KEY = (SSH private key content)
DEPLOY_PATH = /home/deploy_user/ollama-mistral
SLACK_WEBHOOK_URL = https://hooks.slack.com/services/...
```

## Verification

### Check Branch Protection Rules

```bash
# You can verify rules are applied via GitHub API
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/ollama-mistral/branches/main/protection
```

### Test the Protection

Try merging a PR without:
1. ✗ Approval → Should be blocked
2. ✗ Passing status checks → Should be blocked
3. ✗ Updated with main → Should be blocked

All should fail, confirming protection is active.

## Professional Workflow

With branch protection enabled:

```
1. Developer creates feature branch
   ↓
2. Developer pushes and opens PR
   ↓
3. GitHub Actions CI runs automatically
   - Lint ✓
   - Build ✓
   - Test ✓
   ↓
4. CODEOWNERS automatically requested as reviewers
   ↓
5. Code owner reviews and approves
   ↓
6. PR can be merged (all checks passed)
   ↓
7. CD workflow triggers automatically
   - Build Docker image
   - Push to registry
   - Deploy to production
```

## Best Practices

| Practice | Benefit |
|----------|---------|
| Require PR reviews | Code quality & knowledge sharing |
| Require status checks | Prevent broken code from merging |
| Require up-to-date branches | Ensure compatibility with latest main |
| Include administrators | Consistent enforcement for everyone |
| Use CODEOWNERS | Automatic accountability |
| Require conversation resolution | Ensure all comments are addressed |

## Dismissing and Recreating Protection

If you need to modify rules:

1. Click **Edit** on the protection rule
2. Make changes
3. Click **Save changes**

To delete:

1. Click **Edit**
2. Scroll to bottom and click **Delete**
3. Confirm deletion

## Documentation References

- [About branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [CODEOWNERS documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub Actions required checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-to-pass-before-merging)
