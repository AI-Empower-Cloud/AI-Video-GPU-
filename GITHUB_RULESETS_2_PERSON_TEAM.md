# GitHub Rulesets for 2-Person Team (You + Robo3)

## 🎯 Simplified Rulesets Configuration

Since you only have 2 team members, here's a more practical setup:

### 1. **Main Branch Protection Ruleset**

**Ruleset Name**: `main-branch-protection`
**Target**: `main` branch
**Enforcement**: Active

#### Recommended Rules:
- ✅ **Restrict deletions** - Prevents accidental deletion
- ✅ **Restrict force pushes** - Prevents force pushing
- ✅ **Require pull request before merging**
  - **Required reviewers**: 1 (just need the other person to review)
  - **Dismiss stale reviews**: ✅
  - **Require review from code owners**: ✅ (optional)
- ✅ **Require status checks to pass**
  - **Require branches to be up to date**: ✅
  - **Required status checks**:
    - `test (3.8)`
    - `test (3.9)`
    - `test (3.10)`
    - `test (3.11)`
    - `quality`
    - `wasabi-tests`
- ✅ **Require linear history** (keeps git history clean)

#### **Optional** (for stricter security):
- ❓ **Require signed commits** (if you want extra security)

### 2. **Development Branch Protection Ruleset**

**Ruleset Name**: `develop-branch-protection`
**Target**: `develop` branch
**Enforcement**: Active

#### Recommended Rules:
- ✅ **Restrict deletions**
- ✅ **Restrict force pushes**
- ✅ **Require pull request before merging**
  - **Required reviewers**: 1
- ✅ **Require status checks to pass**
  - Required status checks: `test (3.8)`, `test (3.9)`, `test (3.10)`, `test (3.11)`, `quality`

### 3. **CODEOWNERS File Update**

Create/update `.github/CODEOWNERS` to assign both of you as reviewers:

```
# Global code owners - both team members review everything
* @YOUR_USERNAME @Robo3

# Specific areas (optional)
/src/cloud/ @YOUR_USERNAME
/frontend/ @Robo3
/docs/ @YOUR_USERNAME @Robo3
```

## 📋 Step-by-Step Setup for 2-Person Team

### Step 1: Create Main Branch Ruleset
1. Go to GitHub repo → **Settings** → **Rules** → **Rulesets**
2. Click **New ruleset** → **Branch ruleset**
3. **Name**: `main-branch-protection`
4. **Enforcement**: Active
5. **Target**: Include by pattern `main`
6. **Enable these rules**:
   - Restrict deletions ✅
   - Restrict force pushes ✅
   - Require pull request before merging ✅
     - Required reviewers: **1** (not 2)
     - Dismiss stale reviews ✅
   - Require status checks to pass ✅
     - Add: `test (3.8)`, `test (3.9)`, `test (3.10)`, `test (3.11)`, `quality`, `wasabi-tests`
   - Require linear history ✅
7. Click **Create**

### Step 2: Create Development Branch Ruleset
1. Click **New ruleset** → **Branch ruleset**
2. **Name**: `develop-branch-protection`
3. **Enforcement**: Active
4. **Target**: Include by pattern `develop`
5. **Enable these rules**:
   - Restrict deletions ✅
   - Restrict force pushes ✅
   - Require pull request before merging ✅
     - Required reviewers: **1**
   - Require status checks to pass ✅
     - Add: `test (3.8)`, `test (3.9)`, `test (3.10)`, `test (3.11)`, `quality`
6. Click **Create**

### Step 3: Update Team Access
1. Go to **Settings** → **Manage access**
2. Make sure both you and Robo3 have **Admin** or **Maintain** access
3. This allows both to approve PRs and manage the repository

## 🚀 Workflow for 2-Person Team

### Daily Development:
1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Make changes**: Code, test, commit
3. **Push branch**: `git push origin feature/new-feature`
4. **Create PR**: Target `develop` branch
5. **Review**: The other person reviews and approves
6. **Merge**: PR gets merged automatically after approval + tests pass

### Release Process:
1. **Create release PR**: `develop` → `main`
2. **Review**: Both review the release changes
3. **Merge**: After approval, merge to main
4. **Tag**: Create version tag `v1.0.0`

## 🔧 Alternative: Bypass Rules When Needed

Since you're a 2-person team, you might want to add bypass permissions:

### Bypass Configuration:
1. In your ruleset, scroll to **Bypass list**
2. Add **Repository admins** (allows you to bypass rules in emergencies)
3. Add specific users: yourself and Robo3

This allows you to push directly in emergencies while still maintaining good practices.

## 🎯 Benefits for Your Team

### Code Quality:
- ✅ All tests must pass before merging
- ✅ Code review ensures knowledge sharing
- ✅ Clean git history with linear commits

### Flexibility:
- ✅ Only 1 reviewer needed (practical for 2-person team)
- ✅ Can bypass rules in emergencies
- ✅ Both have equal access and responsibilities

### Automation:
- ✅ GitHub Actions automatically test everything
- ✅ Wasabi integration tests run automatically
- ✅ Code quality checks enforced

## 💡 Pro Tips for 2-Person Team

### Communication:
- Use PR descriptions to explain changes
- Add comments in code for complex logic
- Use GitHub Issues to track tasks

### Review Process:
- Review each other's PRs promptly
- Use "Request changes" for important fixes
- Approve when everything looks good

### Emergency Situations:
- Use bypass permissions if needed
- Always create a follow-up PR for review
- Document emergency changes in commit messages

---

**✅ Perfect setup for you and Robo3 to collaborate efficiently while maintaining code quality!**

---

# Wasabi Configuration

For your AI video processing, use these Wasabi settings:

```
WASABI_ACCESS_KEY = 5W346VTEQ11HLJLF177I
WASABI_SECRET_KEY = RezjHz3kqkdYU6VEODpgcQud4lR5D9gRPCFkVeMA
WASABI_ENDPOINT_URL = https://s3.wasabisys.com
WASABI_REGION = us-east-1
WASABI_MODELS_BUCKET = ai-video-gpu-models
WASABI_OUTPUTS_BUCKET = ai-video-gpu-outputs
WASABI_UPLOADS_BUCKET = ai-video-gpu-uploads
WASABI_BACKUPS_BUCKET = ai-video-gpu-backups
WASABI_TEMP_BUCKET = ai-video-gpu-temp
```

Ensure these keys are kept secret. Use GitHub Secrets to store them securely for your workflows.
