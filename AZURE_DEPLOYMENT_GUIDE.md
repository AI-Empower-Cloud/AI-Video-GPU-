# 🚀 AI GPU Studio - Azure Manual Deployment Guide

## 📋 Prerequisites

### 1. Azure Account Setup
- Azure subscription with credits/billing
- Resource quota for GPU VMs (if needed)
- Container Registry access

### 2. GitHub Repository Setup
- Repository with all code pushed
- GitHub Actions enabled
- Azure credentials configured

## 🔧 Step-by-Step Deployment

### **Method 1: Automated GitHub Actions Deployment**

#### Step 1: Configure Azure Credentials
```bash
# Create service principal
az ad sp create-for-rbac \
  --name "ai-gpu-studio-sp" \
  --role contributor \
  --scopes /subscriptions/{subscription-id} \
  --sdk-auth
```

#### Step 2: Add GitHub Secrets
Go to GitHub Repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AZURE_CREDENTIALS`: Output from step 1
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID

#### Step 3: Trigger Deployment
```bash
# Push to main branch triggers automatic deployment
git push origin main

# Or manually trigger via GitHub Actions UI
# Go to Actions → Deploy to Azure → Run workflow
```

### **Method 2: Manual Azure Deployment**

#### Step 1: Run Azure Setup Script
```bash
# Make script executable
chmod +x azure_deploy_ai_video.sh

# Run deployment
./azure_deploy_ai_video.sh
```

#### Step 2: Deploy Frontend
```bash
# Build frontend
cd frontend
npm install
npm run build

# Create Azure Static Web App
az staticwebapp create \
  --name ai-gpu-studio-frontend \
  --resource-group ai-gpu-studio-rg \
  --source https://github.com/AI-Empower-Cloud/AI-Video-GPU- \
  --location "Central US" \
  --branch main \
  --app-location "frontend" \
  --output-location "out"
```

#### Step 3: Deploy Backend APIs
```bash
# Create container registry
az acr create \
  --resource-group ai-gpu-studio-rg \
  --name aigpustudio \
  --sku Basic

# Build and push backend
docker build -t aigpustudio.azurecr.io/backend:latest .
az acr login --name aigpustudio
docker push aigpustudio.azurecr.io/backend:latest

# Create container instance
az container create \
  --resource-group ai-gpu-studio-rg \
  --name ai-gpu-backend \
  --image aigpustudio.azurecr.io/backend:latest \
  --cpu 2 \
  --memory 4 \
  --port 8000 \
  --ip-address public
```

## 🌐 **Deployment Architectures**

### **Option A: Azure Static Web Apps + Container Instances**
```
Frontend (Static Web App) → Backend (Container Instances) → Storage/Database
```
**Cost**: ~$50-100/month
**Best for**: Small to medium traffic

### **Option B: Azure App Service + SQL Database**
```
Full Stack App Service → Azure SQL → Blob Storage
```
**Cost**: ~$100-200/month  
**Best for**: Medium to high traffic

### **Option C: Azure Kubernetes Service (AKS)**
```
AKS Cluster → Multiple Microservices → Managed Databases
```
**Cost**: ~$200-500/month
**Best for**: Enterprise scale

## 📊 **Expected Azure Resources**

| Resource | Type | Purpose | Cost/Month |
|----------|------|---------|------------|
| **Static Web App** | Frontend | Website hosting | $0-9 |
| **Container Instances** | Backend | API services | $30-80 |
| **Storage Account** | Data | File/video storage | $20-50 |
| **SQL Database** | Data | User/project data | $20-100 |
| **CDN** | Performance | Global delivery | $10-30 |
| **Application Insights** | Monitoring | Analytics | $5-20 |
| **Total** | - | Complete platform | **$85-289** |

## 🚀 **Post-Deployment Steps**

### 1. Configure Custom Domain
```bash
# Add custom domain to Static Web App
az staticwebapp hostname set \
  --name ai-gpu-studio-frontend \
  --hostname your-domain.com
```

### 2. Set up SSL Certificate
```bash
# SSL is automatic with Azure Static Web Apps
# For custom domains, use:
az staticwebapp hostname bind \
  --name ai-gpu-studio-frontend \
  --hostname your-domain.com
```

### 3. Configure Environment Variables
```bash
# Set production environment variables
az webapp config appsettings set \
  --resource-group ai-gpu-studio-rg \
  --name ai-gpu-studio \
  --settings \
    NODE_ENV=production \
    DATABASE_URL="your-connection-string" \
    STORAGE_ACCOUNT_URL="your-storage-url"
```

## 🔍 **Monitoring & Troubleshooting**

### Check Deployment Status
```bash
# View resource group
az group show --name ai-gpu-studio-rg --output table

# Check web app status
az webapp show --name ai-gpu-studio --resource-group ai-gpu-studio-rg

# View logs
az webapp log tail --name ai-gpu-studio --resource-group ai-gpu-studio-rg
```

### Common Issues & Solutions

#### Issue: Build Fails
```bash
# Check build logs in GitHub Actions
# Fix: Ensure all dependencies in package.json/requirements.txt

# Local debug:
cd frontend && npm run build
python -m pytest tests/
```

#### Issue: Site Not Loading
```bash
# Check app service logs
az webapp log download --resource-group ai-gpu-studio-rg --name ai-gpu-studio

# Fix: Verify environment variables and port configuration
```

#### Issue: Database Connection
```bash
# Test connection string
az sql db show-connection-string --server your-server --name your-db

# Fix: Update connection string in app settings
```

## 🎯 **Access Your Deployed Website**

After successful deployment:

### Frontend URL
```
https://ai-gpu-studio-frontend.azurestaticapps.net
# Or your custom domain: https://your-domain.com
```

### Backend API URL  
```
https://ai-gpu-studio.azurewebsites.net
# Or container instance public IP
```

### Admin Panel
```
https://ai-gpu-studio-frontend.azurestaticapps.net/admin
```

## 📈 **Scaling Options**

### Horizontal Scaling
```bash
# Scale out app service
az appservice plan update \
  --name ai-gpu-studio-plan \
  --resource-group ai-gpu-studio-rg \
  --number-of-workers 3
```

### Vertical Scaling
```bash
# Scale up to higher tier
az appservice plan update \
  --name ai-gpu-studio-plan \
  --resource-group ai-gpu-studio-rg \
  --sku P2V3
```

## 🎉 **Deployment Complete!**

Your AI GPU Studio website is now live on Azure with:
- ✅ Scalable frontend hosting
- ✅ Containerized backend APIs  
- ✅ Secure database storage
- ✅ Global CDN delivery
- ✅ SSL certificates
- ✅ Monitoring & analytics
- ✅ CI/CD pipeline

**Total setup time**: 15-30 minutes
**Monthly cost**: $85-289 depending on usage
**Uptime**: 99.9% SLA with Azure
