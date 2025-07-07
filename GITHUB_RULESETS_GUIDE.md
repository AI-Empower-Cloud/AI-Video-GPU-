# GitHub Rulesets Configuration Guide

## 🎯 Recommended Rulesets for AI Video GPU Repository

### 1. **Main Branch Protection Ruleset**

**Ruleset Name**: `main-branch-protection`
**Target**: `main` branch
**Enforcement**: Active

#### Rules to Enable:
- ✅ **Restrict deletions**
- ✅ **Restrict force pushes**
- ✅ **Require pull request before merging**
  - Required reviewers: 2
  - Dismiss stale reviews when new commits are pushed
  - Require review from code owners
  - Require approval of most recent push
- ✅ **Require status checks to pass**
  - Require branches to be up to date
  - Required status checks:
    - `test (3.8)`
    - `test (3.9)`
    - `test (3.10)`
    - `test (3.11)`
    - `quality`
    - `wasabi-tests`
- ✅ **Require signed commits**
- ✅ **Require linear history**

### 2. **Development Branch Protection Ruleset**

**Ruleset Name**: `develop-branch-protection`
**Target**: `develop` branch
**Enforcement**: Active

#### Rules to Enable:
- ✅ **Restrict deletions**
- ✅ **Restrict force pushes**
- ✅ **Require pull request before merging**
  - Required reviewers: 1
  - Dismiss stale reviews when new commits are pushed
  - Require review from code owners
- ✅ **Require status checks to pass**
  - Required status checks:
    - `test (3.8)`
    - `test (3.9)`
    - `test (3.10)`
    - `test (3.11)`
    - `quality`

### 3. **Tag Protection Ruleset**

**Ruleset Name**: `tag-protection`
**Target**: `v*` (version tags)
**Enforcement**: Active

#### Rules to Enable:
- ✅ **Restrict deletions**
- ✅ **Restrict updates**

## 📋 Step-by-Step Setup

### Step 1: Access Repository Settings
1. Go to your GitHub repository
2. Click **Settings** tab
3. In the left sidebar, click **Rules** → **Rulesets**

### Step 2: Create Main Branch Ruleset
1. Click **New ruleset**
2. Select **Branch ruleset**
3. Name: `main-branch-protection`
4. Enforcement: **Active**
5. Target: Include by pattern `main`
6. Configure rules as listed above
7. Click **Create**

### Step 3: Create Development Branch Ruleset
1. Click **New ruleset**
2. Select **Branch ruleset**
3. Name: `develop-branch-protection`
4. Enforcement: **Active**
5. Target: Include by pattern `develop`
6. Configure rules as listed above
7. Click **Create**

### Step 4: Create Tag Protection Ruleset
1. Click **New ruleset**
2. Select **Tag ruleset**
3. Name: `tag-protection`
4. Enforcement: **Active**
5. Target: Include by pattern `v*`
6. Configure rules as listed above
7. Click **Create**

## 🔐 Additional Security Settings

### Repository Security Settings
Go to **Settings** → **Security & analysis** and enable:
- ✅ **Dependency graph**
- ✅ **Dependabot alerts**
- ✅ **Dependabot security updates**
- ✅ **Dependabot version updates**
- ✅ **Secret scanning**
- ✅ **Secret scanning push protection**

### Branch Protection vs Rulesets
- **Rulesets** are the modern approach (recommended)
- **Branch protection rules** are the legacy approach
- Choose one or the other, not both

## 🎯 Benefits of Rulesets

### For AI Video GPU Repository:
- **Code Quality**: Ensures all code is reviewed and tested
- **Security**: Prevents unauthorized changes to main branches
- **Compliance**: Maintains audit trail with signed commits
- **Reliability**: Requires all tests to pass before merging
- **Collaboration**: Enforces proper code review process

### Specific to Your CI/CD:
- **Python Tests**: All Python versions must pass
- **Code Quality**: Linting and formatting checks required
- **Wasabi Integration**: Storage integration tests must pass
- **Docker Builds**: Container builds must succeed

## 🚀 Quick Setup Commands

If you prefer using GitHub CLI:

```bash
# Install GitHub CLI if not already installed
# gh auth login

# Create main branch protection
gh api repos/YOUR_USERNAME/AI-Video-GPU-/rulesets \
  --method POST \
  --field name='main-branch-protection' \
  --field enforcement='active' \
  --field target='branch' \
  --field conditions='{"ref_name":{"include":["main"]}}' \
  --field rules='[{"type":"deletion"},{"type":"force_push"},{"type":"required_status_checks","parameters":{"required_status_checks":["test (3.8)","test (3.9)","test (3.10)","test (3.11)","quality"]}}]'
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## 🔧 Troubleshooting

### Common Issues:
1. **Status checks not appearing**: Make sure your GitHub Actions have run at least once
2. **Rules not enforcing**: Check that enforcement is set to "Active"
3. **Bypass not working**: Ensure bypass permissions are correctly configured

### Testing Your Rulesets:
1. Create a test branch
2. Make a small change
3. Try to push directly to main (should fail)
4. Create a PR (should require reviews and status checks)

---

**✅ Your AI Video GPU repository will now have enterprise-grade protection with modern GitHub rulesets!**
