# 🎯 Manual GitHub Setup Guide (2-Person Team)

Since automated setup has permission restrictions, here's the **exact manual steps** to configure your GitHub repository:

## 🔐 Step 1: Set Up GitHub Secrets

1. **Go to your repository**: https://github.com/AI-Empower-Cloud/AI-Video-GPU-
2. **Click Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"** for each of these:

```
Secret Name: WASABI_ACCESS_KEY
Value: 5W346VTEQ11HLJLF177I

Secret Name: WASABI_SECRET_KEY
Value: RezjHz3kqkdYU6VEODpgcQud4lR5D9gRPCFkVeMA

Secret Name: WASABI_ENDPOINT_URL
Value: https://s3.wasabisys.com

Secret Name: WASABI_REGION
Value: us-east-1

Secret Name: WASABI_MODELS_BUCKET
Value: ai-video-gpu-models

Secret Name: WASABI_OUTPUTS_BUCKET
Value: ai-video-gpu-outputs

Secret Name: WASABI_UPLOADS_BUCKET
Value: ai-video-gpu-uploads

Secret Name: WASABI_BACKUPS_BUCKET
Value: ai-video-gpu-backups

Secret Name: WASABI_TEMP_BUCKET
Value: ai-video-gpu-temp
```

## 🛡️ Step 2: Create Branch Protection Rulesets

1. **Go to**: https://github.com/AI-Empower-Cloud/AI-Video-GPU-/settings/rules
2. **Click "New ruleset"** → **"Branch ruleset"**

### **Main Branch Ruleset:**
- **Ruleset name**: `main-branch-protection`
- **Enforcement status**: Active
- **Target branches**: Include by pattern → `main`

**Enable these rules:**
- ✅ **Restrict deletions**
- ✅ **Restrict force pushes**
- ✅ **Require a pull request before merging**
  - Required number of reviewers: **1**
  - Dismiss stale reviews when new commits are pushed: ✅
  - Require review from code owners: ✅
- ✅ **Require status checks to pass before merging**
  - Require branches to be up to date before merging: ✅
  - **Add these status checks** (click "Add status check" for each):
    - `test (3.8)`
    - `test (3.9)`
    - `test (3.10)`
    - `test (3.11)`
    - `quality`
    - `wasabi-tests`
- ✅ **Require linear history**

**Click "Create"**

### **Develop Branch Ruleset:**
1. **Click "New ruleset"** → **"Branch ruleset"** again
- **Ruleset name**: `develop-branch-protection`
- **Enforcement status**: Active
- **Target branches**: Include by pattern → `develop`

**Enable these rules:**
- ✅ **Restrict deletions**
- ✅ **Restrict force pushes**
- ✅ **Require a pull request before merging**
  - Required number of reviewers: **1**
  - Dismiss stale reviews when new commits are pushed: ✅
- ✅ **Require status checks to pass before merging**
  - **Add these status checks**:
    - `test (3.8)`
    - `test (3.9)`
    - `test (3.10)`
    - `test (3.11)`
    - `quality`

**Click "Create"**

## 👥 Step 3: Add Robo3 as Collaborator

1. **Go to**: https://github.com/AI-Empower-Cloud/AI-Video-GPU-/settings/access
2. **Click "Add people"**
3. **Search for**: `Robo3` (or their actual GitHub username)
4. **Select permission level**: **Admin**
5. **Click "Add Robo3 to this repository"**

## 📝 Step 4: Update CODEOWNERS File

The CODEOWNERS file has been automatically updated with your username. Just verify it looks correct.

## 🧪 Step 5: Test the Setup

1. **Create a test branch**:
   ```bash
   git checkout -b test/verify-rules
   echo "Test file" > test-file.txt
   git add test-file.txt
   git commit -m "Test: Verify branch protection rules"
   git push origin test/verify-rules
   ```

2. **Create a Pull Request**:
   - Go to your repository on GitHub
   - Click "Compare & pull request"
   - Target: `develop` branch
   - Create the PR

3. **Verify Protection Works**:
   - ✅ PR should show "Review required"
   - ✅ Status checks should appear when GitHub Actions run
   - ✅ Merge should be blocked until review + tests pass

## ✅ Completion Checklist

- [ ] All 9 GitHub secrets added
- [ ] Main branch ruleset created
- [ ] Develop branch ruleset created
- [ ] Robo3 added as collaborator
- [ ] Test PR created and rules verified

## 🚀 You're Done!

Once you complete these steps, your repository will have:
- ✅ **Enterprise-grade branch protection**
- ✅ **Automated testing requirements**
- ✅ **Code review workflow**
- ✅ **Secure Wasabi integration**
- ✅ **2-person team collaboration setup**

**Total setup time: ~10-15 minutes**
