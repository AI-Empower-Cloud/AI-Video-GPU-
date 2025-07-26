# 🔧 Azure Setup Guide - Using Your $1,000 Credits Strategically

## 🎯 **Complete Step-by-Step Guide**

**Your Goal**: Deploy an AI video platform on Azure while maximizing learning and minimizing waste of your $1,000 credits.

---

## 📋 **Phase 1: Initial Setup (30 minutes)**

### **Step 1: Verify Your Azure Credits**
1. **Login to Azure Portal**: https://portal.azure.com
2. **Check your credits**: 
   - Go to "Subscriptions"
   - Click on your subscription
   - View "Credits" section
   - Confirm you have $1,000 available

### **Step 2: Install Azure CLI (If needed)**
```bash
# On Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# On macOS
brew install azure-cli

# On Windows
# Download from: https://aka.ms/installazurecliwindows
```

### **Step 3: Login to Azure CLI**
```bash
# Login to your Azure account
az login

# Verify your subscription
az account show

# Set your subscription (if you have multiple)
az account set --subscription "your-subscription-id"
```

---

## 🚀 **Phase 2: Deploy Your AI Video Platform (45 minutes)**

### **Step 1: Make the Deployment Script Executable**
```bash
# Navigate to your project directory
cd /workspaces/AI-Video-GPU-

# Make the deployment script executable
chmod +x azure_deploy_ai_video.sh
```

### **Step 2: Run the Automated Deployment**
```bash
# Deploy your complete AI video platform
./azure_deploy_ai_video.sh
```

**What this script does:**
- ✅ **Creates resource group** for organized management
- ✅ **Sets up GPU virtual machine** (Standard_NC6 - 1 GPU)
- ✅ **Configures storage account** for videos and models
- ✅ **Installs AI/ML dependencies** (PyTorch, CUDA, FFmpeg)
- ✅ **Deploys video generation code** with web interface
- ✅ **Sets up automatic startup** services

### **Step 3: Monitor the Deployment**
The script will show real-time progress:
```
🚀 AZURE AI VIDEO PLATFORM DEPLOYMENT
=====================================
[INFO] Starting Azure AI Video Platform deployment...
[INFO] Checking prerequisites...
[SUCCESS] Prerequisites check completed
[INFO] Creating resource group: ai-video-platform-rg
[SUCCESS] Resource group created
[INFO] Creating storage account...
[SUCCESS] Storage account and container created
[INFO] Creating GPU virtual machine: ai-video-gpu-vm
[WARNING] This will use ~$1-3/hour of your Azure credits
[SUCCESS] GPU virtual machine created
```

---

## 💰 **Phase 3: Cost Management Setup (15 minutes)**

### **Step 1: Set Up Budget Alerts**
```bash
# Create a budget to monitor your spending
az consumption budget create \
    --budget-name "ai-video-platform-budget" \
    --amount 800 \
    --time-grain Monthly \
    --start-date $(date +%Y-%m-01) \
    --end-date 2025-12-31 \
    --resource-group ai-video-platform-rg
```

### **Step 2: Enable Cost Alerts**
1. **Go to Azure Portal** → "Cost Management + Billing"
2. **Click "Budgets"** → Create new budget
3. **Set alerts at**:
   - 50% of budget ($400)
   - 75% of budget ($600)
   - 90% of budget ($720)

### **Step 3: Monitor Daily Costs**
```bash
# Check your current spending
az consumption usage list \
    --start-date $(date -d "30 days ago" +%Y-%m-%d) \
    --end-date $(date +%Y-%m-%d) \
    --output table
```

---

## 🎬 **Phase 4: Test Your AI Video Platform (30 minutes)**

### **Step 1: Access Your Web Interface**
After deployment completes, you'll see:
```
🎉 Azure AI Video Platform Deployment Complete!
===============================================

🌐 Access Points:
   Web Interface: http://[YOUR-VM-IP]
   SSH Access: ssh azureuser@[YOUR-VM-IP]
   Status API: http://[YOUR-VM-IP]/status
```

### **Step 2: Generate Your First AI Video**
1. **Open web interface** in your browser
2. **Enter custom text**: "AI Empower GPU Cloud Demo"
3. **Select duration**: Start with 10 seconds
4. **Click "Generate Video"**
5. **Download and review** your first Azure-generated video

### **Step 3: Test via SSH (Advanced)**
```bash
# SSH into your VM
ssh azureuser@[YOUR-VM-IP]

# Activate the Python environment
source ~/ai_video_env/bin/activate

# Generate a video directly
cd ~/ai_video_platform
python ai_video_generator.py --text "My Azure AI Video" --duration 15
```

---

## 📊 **Phase 5: Performance Monitoring (Ongoing)**

### **Daily Monitoring Routine**

#### **Check GPU Utilization**
```bash
# SSH into your VM and check GPU usage
ssh azureuser@[YOUR-VM-IP]
nvidia-smi
```

#### **Monitor Costs**
```bash
# Check daily spending
az consumption usage list --output table --top 10
```

#### **Check System Status**
```bash
# Visit your status endpoint
curl http://[YOUR-VM-IP]/status
```

### **Weekly Optimization Tasks**

#### **Stop VM When Not in Use**
```bash
# Stop VM to save costs (storage costs continue, but compute stops)
az vm stop --resource-group ai-video-platform-rg --name ai-video-gpu-vm

# Start VM when needed
az vm start --resource-group ai-video-platform-rg --name ai-video-gpu-vm
```

#### **Review and Clean Up Storage**
```bash
# List videos in storage
az storage blob list \
    --container-name videos \
    --account-name [YOUR-STORAGE-ACCOUNT] \
    --output table

# Delete old videos to save costs
az storage blob delete \
    --container-name videos \
    --name old-video.mp4 \
    --account-name [YOUR-STORAGE-ACCOUNT]
```

---

## 🎯 **Cost Optimization Strategies**

### **VM Cost Management**
| **Action** | **Savings** | **When to Use** |
|------------|-------------|-----------------|
| **Stop VM when idle** | ~$1-3/hour saved | After each video generation session |
| **Use Spot instances** | 60-90% discount | For batch processing jobs |
| **Schedule auto-shutdown** | Prevents overnight costs | Set for 6 PM daily |

### **Storage Optimization**
- **Delete old videos**: Save ~$0.02/GB/month
- **Use cool storage**: For long-term video archives
- **Compress videos**: Reduce storage costs by 50-80%

### **Smart Usage Patterns**
```bash
# Efficient workflow
1. Start VM: az vm start --name ai-video-gpu-vm
2. Generate multiple videos in one session
3. Download all videos locally
4. Stop VM: az vm stop --name ai-video-gpu-vm
5. Clean up storage periodically
```

---

## 🚨 **Troubleshooting Common Issues**

### **Issue: VM won't start**
```bash
# Check VM status
az vm get-instance-view --resource-group ai-video-platform-rg --name ai-video-gpu-vm

# Restart VM
az vm restart --resource-group ai-video-platform-rg --name ai-video-gpu-vm
```

### **Issue: Web interface not accessible**
```bash
# Check if service is running
ssh azureuser@[YOUR-VM-IP]
sudo systemctl status ai-video-web.service

# Restart service if needed
sudo systemctl restart ai-video-web.service
```

### **Issue: GPU not detected**
```bash
# SSH into VM and check NVIDIA drivers
ssh azureuser@[YOUR-VM-IP]
nvidia-smi

# If not working, reinstall drivers
sudo apt update
sudo apt install --reinstall nvidia-driver-470
sudo reboot
```

---

## 📈 **Success Metrics Tracking**

### **Weekly Progress Report**
Create a simple tracking spreadsheet:

| **Week** | **Credits Used** | **Videos Generated** | **Cost per Video** | **Technical Learnings** |
|----------|------------------|---------------------|-------------------|-------------------------|
| Week 1 | $50 | 10 videos | $5.00 | GPU setup, basic generation |
| Week 2 | $75 | 20 videos | $3.75 | Optimization, batch processing |
| Week 3 | $60 | 25 videos | $2.40 | Advanced features, storage mgmt |

### **Application Preparation Data**
Document your Azure usage for the $25,000 application:
- **Total compute hours**: X hours of GPU usage
- **Videos generated**: X professional-quality videos
- **Cost efficiency**: Achieved $X per video (industry standard: $10-50)
- **Technical innovations**: GPU optimization, batch processing
- **Growth projection**: From $60/month to $2,000+/month with users

---

## 🎉 **Next Steps After Setup**

### **Week 1: Foundation**
- ✅ Deploy platform successfully
- ✅ Generate 10+ demo videos
- ✅ Set up cost monitoring
- ✅ Document performance metrics

### **Week 2: Optimization**
- 📈 Optimize video generation pipeline
- 📊 Implement batch processing
- 💰 Reduce cost per video by 30%+
- 📝 Document technical improvements

### **Week 3: Scaling Preparation**
- 🚀 Test with different video types
- 📋 Prepare $25,000 Azure application
- 💼 Create professional demo portfolio
- 📈 Project future infrastructure needs

---

## 💡 **Pro Tips for Success**

### **Budget Management**
- **Set daily spending limits**: $30-50/day maximum
- **Use scheduled shutdown**: Automatically stop VMs at night
- **Monitor storage growth**: Delete temporary files regularly
- **Batch operations**: Generate multiple videos per session

### **Technical Excellence**
- **Document everything**: Screenshot your successes
- **Version control**: Save your best video generation scripts
- **Performance tuning**: Optimize for speed and quality
- **Security practices**: Use SSH keys, limit access

### **Application Preparation**
- **Usage documentation**: Track all Azure services used
- **Cost optimization**: Show responsible credit usage
- **Innovation evidence**: Document technical improvements
- **Growth projections**: Realistic scaling plans based on actual data

---

**🚀 Ready to deploy your AI video platform on Azure and make strategic use of your $1,000 credits!**

*This guide transforms your credits into a professional AI platform that will strengthen your case for $25,000+ in additional funding.*
