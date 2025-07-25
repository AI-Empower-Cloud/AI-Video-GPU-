# 🚀 GitHub Actions Deployment Guide

## ✅ Successfully Enabled Automated Deployment!

I've modified the GitHub Actions workflow to:

1. ✅ **Enable deployment from `website-plan` branch**
2. ✅ **Add GPU/CPU deployment option**
3. ✅ **Configure automatic triggering**

## 📋 How To Start the Deployment:

### Method 1: Automatic Trigger (Already Working)
Any push to the `website-plan` branch (like the one we just did) will automatically trigger deployment.

### Method 2: Manual Trigger in GitHub UI
1. Go to your GitHub repository: https://github.com/AI-Empower-Cloud/AI-Video-GPU-
2. Click on "Actions" tab
3. Click on "Deploy to Azure" workflow
4. Click "Run workflow" button
5. Select options:
   - Branch: `website-plan`
   - Environment: `production`
   - Deploy with GPU support: `false` (until quota approved)
6. Click "Run workflow"

## 🎯 What Will Deploy:

The workflow will automatically:
1. Build frontend and backend
2. Create Azure resources (with CPU instead of GPU)
3. Deploy containers
4. Configure networking
5. Setup monitoring

## 🎛️ Options Available:

### Deploy Environments:
- `production`: Main environment
- `staging`: Testing environment

### GPU Support:
- `false`: Use CPU-only (works immediately)
- `true`: Use GPU (requires quota approval)

## 🔄 Upgrade to GPU Later:

When GPU quota is approved, you can:
1. Go to GitHub Actions
2. Run workflow manually with `use_gpu: true`

## 📊 Monitor Deployment:

To see deployment progress:
1. Go to "Actions" tab
2. Click on the running workflow
3. Watch real-time logs

## 🛑 If There Are Issues:

If deployment fails:
1. Check logs in GitHub Actions
2. Azure Resource Group may need manual cleanup
3. Run CPU-only deployment first

## 🎉 Next Steps:

1. Submit GPU quota request via Azure Portal
2. Monitor GitHub Actions for deployment status
3. When quota approved, trigger GPU deployment
