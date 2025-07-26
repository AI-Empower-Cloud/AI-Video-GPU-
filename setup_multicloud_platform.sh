#!/bin/bash

# 🌐 AI Video GPU - Multi-Cloud Platform Setup
# Comprehensive 4-cloud strategy for optimal performance and cost

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                 🌐 AI VIDEO GPU - MULTI-CLOUD PLATFORM SETUP                ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_strategy_table() {
    echo -e "${PURPLE}📊 MULTI-CLOUD STRATEGY OVERVIEW${NC}"
    echo "=================================================================================="
    echo ""
    echo "| Cloud            | Best Used For                                              | Key Strengths                                 | Suggested Role                     |"
    echo "| ---------------- | ---------------------------------------------------------- | --------------------------------------------- | ---------------------------------- |"
    echo "| **GCP**          | AI/ML, Deep Learning, Vertex AI                           | TensorFlow, TPUs, AI APIs, BigQuery          | GPU training, AI services          |"
    echo "| **AWS**          | High-performance compute, scalable storage, global reach  | EC2 GPU instances, Lambda, S3, SageMaker     | Hosting, compute, storage          |"
    echo "| **Azure**        | Enterprise apps, Dev tools, hybrid workloads              | Windows, GitHub Codespaces, Azure DevOps     | AI Dev Environments, Azure Dev Box |"
    echo "| **Oracle Cloud** | Cheap GPU burst compute (limited free tier), enterprise DB| Free tier Arm instances, strong enterprise DB| Backup compute, persistent DB      |"
    echo ""
    echo "=================================================================================="
    echo ""
}

print_detailed_roles() {
    echo -e "${GREEN}🧠 GCP (Google Cloud Platform) – Your AI Brain${NC}"
    echo "Use for:"
    echo "• Training AI/ML models with TPUs or NVIDIA A100s"
    echo "• Voice synthesis, translation (via Google AI APIs)"
    echo "• BigQuery for analytics and logs"
    echo "• Best Tools: Vertex AI, TensorFlow, Colab Pro+, Google Kubernetes Engine"
    echo "• Example: Run Gen-2 / SVD / AnimateDiff model training here"
    echo "• Startup Credits: Up to \$200K"
    echo ""
    
    echo -e "${BLUE}⚡ AWS – High-Performance Compute & Storage${NC}"
    echo "Use for:"
    echo "• EC2 GPU instances for video rendering (p3, p4, g4dn)"
    echo "• S3 for massive video storage and CDN delivery"
    echo "• Lambda for serverless video processing"
    echo "• Best Tools: EC2, S3, Lambda, SageMaker, ECS"
    echo "• Example: Host video inference API and store rendered videos"
    echo "• Startup Credits: Up to \$100K with AWS Activate"
    echo ""
    
    echo -e "${CYAN}🛠️ Azure – Developer & Hybrid Power${NC}"
    echo "Use for:"
    echo "• Dev environment like GitHub Codespaces or Azure Dev Box"
    echo "• Container orchestration with Azure Kubernetes Service (AKS)"
    echo "• CI/CD pipelines for your AI Studio web apps"
    echo "• Best Tools: Azure DevOps, Dev Box, AKS, App Service"
    echo "• Example: Run your app frontend development, testing, and previews"
    echo "• Startup Credits: Up to \$150K with investor referral"
    echo ""
    
    echo -e "${YELLOW}💰 Oracle Cloud – Cost-Effective Compute / DB${NC}"
    echo "Use for:"
    echo "• Backup compute (if GPU quota approved)"
    echo "• Hosting Oracle or MySQL DB backend"
    echo "• Cost-effective experimentation (Always Free tier includes VMs, DB)"
    echo "• Best Tools: OCI VMs, Autonomous DB, Oracle Functions"
    echo "• Example: Deploy a test microservice or backend DB here"
    echo "• Free Tier: 2 VMs + Block Storage + 10GB DB (always free)"
    echo ""
}

print_architecture_flow() {
    echo -e "${PURPLE}🏗️ Multi-Cloud Architecture Flow${NC}"
    echo "=================================================================================="
    echo ""
    echo "Example: AI GPU Studio Multi-Cloud Flow"
    echo ""
    echo "[ GCP ]"
    echo "Train AI models (TPU/GPU)"
    echo "↓"
    echo "Export model"
    echo "↓"
    echo "[ AWS ]"
    echo "Host inference API + store videos (S3)"
    echo "↓"
    echo "Serve to frontend"
    echo "↓"
    echo "[ Azure ]"
    echo "Build web app in Azure Dev Box or GitHub Codespaces"
    echo "↓"
    echo "Deploy container to Azure App Service or AWS Lambda"
    echo "↓"
    echo "[ Oracle Cloud ]"
    echo "Backup services or host secondary DB / API monitor"
    echo ""
    echo "=================================================================================="
    echo ""
}

setup_gcp_immediate() {
    echo -e "${GREEN}🚀 Setting up GCP (Immediate Setup Available)${NC}"
    echo ""
    echo "1. Enable required APIs:"
    echo "   gcloud services enable compute.googleapis.com"
    echo "   gcloud services enable container.googleapis.com"
    echo "   gcloud services enable aiplatform.googleapis.com"
    echo ""
    echo "2. Create GPU-enabled instance:"
    echo "   gcloud compute instances create ai-video-gpu-gcp \\"
    echo "     --zone=us-central1-a \\"
    echo "     --machine-type=n1-standard-8 \\"
    echo "     --accelerator=type=nvidia-tesla-t4,count=1 \\"
    echo "     --image-family=ubuntu-2004-lts \\"
    echo "     --image-project=ubuntu-os-cloud \\"
    echo "     --boot-disk-size=100GB"
    echo ""
    echo "3. Set up Vertex AI for model training"
    echo "4. Configure BigQuery for analytics"
    echo ""
}

setup_azure_current() {
    echo -e "${CYAN}✅ Azure Setup (Currently Active)${NC}"
    echo ""
    echo "Status: ✅ Ready to deploy"
    echo "• Service Principal: Created"
    echo "• GitHub Actions: Configured" 
    echo "• Credentials: Available in github-azure-credentials.json"
    echo ""
    echo "Next steps:"
    echo "1. Add AZURE_CREDENTIALS to GitHub secrets"
    echo "2. Run GitHub Actions workflow"
    echo "3. Scale to additional regions as needed"
    echo ""
}

setup_aws_pending() {
    echo -e "${YELLOW}⏳ AWS Setup (Verification Pending)${NC}"
    echo ""
    echo "Status: Waiting for account verification"
    echo "While waiting, prepare:"
    echo ""
    echo "1. AWS CLI configuration (when verified):"
    echo "   aws configure"
    echo ""
    echo "2. Create IAM role for EC2 GPU instances"
    echo "3. Request GPU instance limits (p3.2xlarge, g4dn.xlarge)"
    echo "4. Set up S3 buckets for video storage"
    echo ""
    echo "Estimated verification time: 24-48 hours"
    echo ""
}

setup_oracle_pending() {
    echo -e "${RED}⏳ Oracle Cloud Setup (Verification Pending)${NC}"
    echo ""
    echo "Status: Waiting for account verification"
    echo "While waiting, prepare:"
    echo ""
    echo "1. OCI CLI setup (when verified):"
    echo "   bash -c \"\$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)\""
    echo ""
    echo "2. Request GPU quota (if needed for compute-intensive workloads)"
    echo "3. Set up Always Free tier resources"
    echo "4. Configure Autonomous Database"
    echo ""
    echo "Estimated verification time: 2-5 business days"
    echo ""
}

create_multicloud_config() {
    echo -e "${BLUE}📝 Creating multi-cloud configuration files...${NC}"
    
    # Create multi-cloud environment template
    cat > multicloud.env.template << 'EOF'
# Multi-Cloud Configuration Template
# Copy to multicloud.env and fill in your values

# GCP Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GCP_REGION=us-central1
GCP_ZONE=us-central1-a

# AWS Configuration (when verified)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# Azure Configuration (already set up)
AZURE_SUBSCRIPTION_ID=f958627c-f1a5-4316-9781-cb22f955ebd7
AZURE_TENANT_ID=dde73cd2-abc4-4390-87a2-682dd539a6e2
AZURE_CLIENT_ID=faa79ce1-77f1-4d2b-9849-7c86e514cd75
AZURE_CLIENT_SECRET=UR28Q~t4Vj7woU5bWmLilU-FJ6Po4rPi44DPzbPh

# Oracle Cloud Configuration (when verified)
OCI_USER_ID=your-user-ocid
OCI_FINGERPRINT=your-key-fingerprint
OCI_TENANCY=your-tenancy-ocid
OCI_REGION=us-ashburn-1
OCI_KEY_FILE=/path/to/oci-private-key.pem

# Multi-Cloud Strategy Settings
PRIMARY_CLOUD=azure
BACKUP_CLOUD=gcp
STORAGE_CLOUD=aws
DATABASE_CLOUD=oracle

# Load Balancing
ENABLE_MULTI_CLOUD_LB=true
FAILOVER_ENABLED=true
COST_OPTIMIZATION=true
EOF

    # Create deployment scripts for each cloud
    create_cloud_deployment_scripts
    
    echo "✅ Multi-cloud configuration files created"
}

create_cloud_deployment_scripts() {
    # GCP Deployment Script
    cat > deploy_gcp.sh << 'EOF'
#!/bin/bash
# GCP Deployment Script

echo "🌐 Deploying to Google Cloud Platform..."

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Create GKE cluster for microservices
gcloud container clusters create ai-video-gcp \
  --zone=us-central1-a \
  --num-nodes=3 \
  --enable-autorepair \
  --enable-autoupgrade \
  --accelerator=type=nvidia-tesla-t4,count=1

# Deploy to GKE
kubectl apply -f k8s/gcp/

echo "✅ GCP deployment completed"
EOF

    # AWS Deployment Script (for when verified)
    cat > deploy_aws.sh << 'EOF'
#!/bin/bash
# AWS Deployment Script (use when account is verified)

echo "🌐 Deploying to Amazon Web Services..."

# Create ECS cluster
aws ecs create-cluster --cluster-name ai-video-aws

# Create S3 bucket for video storage
aws s3 mb s3://ai-video-gpu-storage-$(date +%s)

# Deploy Lambda functions
aws lambda create-function \
  --function-name ai-video-processor \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda-deployment.zip

echo "✅ AWS deployment completed"
EOF

    # Oracle Cloud Deployment Script (for when verified)
    cat > deploy_oracle.sh << 'EOF'
#!/bin/bash
# Oracle Cloud Deployment Script (use when account is verified)

echo "🌐 Deploying to Oracle Cloud..."

# Create compute instance
oci compute instance launch \
  --availability-domain <AD> \
  --compartment-id <COMPARTMENT_ID> \
  --image-id <IMAGE_ID> \
  --shape VM.Standard2.1 \
  --display-name ai-video-oracle

# Set up Autonomous Database
oci db autonomous-database create \
  --compartment-id <COMPARTMENT_ID> \
  --db-name AIVIDEODB \
  --display-name "AI Video Database"

echo "✅ Oracle Cloud deployment completed"
EOF

    chmod +x deploy_gcp.sh deploy_aws.sh deploy_oracle.sh
}

create_cost_optimization_dashboard() {
    cat > multicloud_cost_dashboard.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Cloud Cost Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .cloud-card { border: 1px solid #ddd; margin: 10px; padding: 15px; border-radius: 8px; }
        .gcp { border-left: 4px solid #4285f4; }
        .aws { border-left: 4px solid #ff9900; }
        .azure { border-left: 4px solid #0078d4; }
        .oracle { border-left: 4px solid #f80000; }
        .status-ready { color: #28a745; }
        .status-pending { color: #ffc107; }
        .status-setup { color: #17a2b8; }
    </style>
</head>
<body>
    <h1>🌐 AI Video GPU - Multi-Cloud Cost Dashboard</h1>
    
    <div class="cloud-card gcp">
        <h3>🧠 Google Cloud Platform</h3>
        <p><strong>Status:</strong> <span class="status-setup">Ready for Setup</span></p>
        <p><strong>Monthly Estimate:</strong> $200-500 (with AI workloads)</p>
        <p><strong>Free Credits:</strong> Up to $200K for startups</p>
        <p><strong>Best for:</strong> AI/ML training, TPU workloads</p>
    </div>
    
    <div class="cloud-card azure">
        <h3>🛠️ Microsoft Azure</h3>
        <p><strong>Status:</strong> <span class="status-ready">Active & Ready</span></p>
        <p><strong>Monthly Estimate:</strong> $100-300 (dev environments)</p>
        <p><strong>Free Credits:</strong> Up to $150K with referral</p>
        <p><strong>Best for:</strong> Development, CI/CD, containers</p>
    </div>
    
    <div class="cloud-card aws">
        <h3>⚡ Amazon Web Services</h3>
        <p><strong>Status:</strong> <span class="status-pending">Verification Pending</span></p>
        <p><strong>Monthly Estimate:</strong> $300-800 (GPU instances + S3)</p>
        <p><strong>Free Credits:</strong> Up to $100K with AWS Activate</p>
        <p><strong>Best for:</strong> Production hosting, storage, compute</p>
    </div>
    
    <div class="cloud-card oracle">
        <h3>💰 Oracle Cloud</h3>
        <p><strong>Status:</strong> <span class="status-pending">Verification Pending</span></p>
        <p><strong>Monthly Estimate:</strong> $0-200 (with Always Free tier)</p>
        <p><strong>Free Tier:</strong> Always Free VMs + Database</p>
        <p><strong>Best for:</strong> Backup services, database hosting</p>
    </div>
    
    <h2>📊 Total Estimated Monthly Cost: $600-1800</h2>
    <p><em>With startup credits, you could run for 12-24 months before paying full price</em></p>
    
    <h2>🎯 Recommended Immediate Actions:</h2>
    <ol>
        <li><strong>Azure:</strong> Complete GitHub secrets setup and deploy</li>
        <li><strong>GCP:</strong> Create project and enable GPU quota</li>
        <li><strong>AWS:</strong> Wait for verification, then request GPU limits</li>
        <li><strong>Oracle:</strong> Wait for verification, set up Always Free resources</li>
    </ol>
</body>
</html>
EOF
    echo "✅ Cost dashboard created: multicloud_cost_dashboard.html"
}

create_management_tools() {
    echo -e "${BLUE}🛠️ Creating multi-cloud management tools...${NC}"
    
    # Multi-cloud status checker
    cat > check_multicloud_status.sh << 'EOF'
#!/bin/bash
# Multi-Cloud Status Checker

echo "🌐 Multi-Cloud Platform Status Check"
echo "=================================="

# Check Azure
echo "🔵 Azure:"
if az account show >/dev/null 2>&1; then
    echo "  ✅ CLI authenticated"
    echo "  📊 Subscription: $(az account show --query name -o tsv)"
else
    echo "  ❌ Not authenticated"
fi

# Check GCP
echo "🟢 Google Cloud:"
if gcloud auth list --filter=status:ACTIVE --format="value(account)" >/dev/null 2>&1; then
    echo "  ✅ CLI authenticated"
    echo "  📊 Project: $(gcloud config get-value project 2>/dev/null)"
else
    echo "  ❌ Not authenticated - run 'gcloud auth login'"
fi

# Check AWS
echo "🟠 AWS:"
if aws sts get-caller-identity >/dev/null 2>&1; then
    echo "  ✅ CLI authenticated"
    echo "  📊 Account: $(aws sts get-caller-identity --query Account --output text)"
else
    echo "  ❌ Not authenticated or account not verified"
fi

# Check Oracle Cloud
echo "🔴 Oracle Cloud:"
if oci iam user get --user-id $(oci iam user list --query 'data[0].id' --raw-output 2>/dev/null) >/dev/null 2>&1; then
    echo "  ✅ CLI authenticated"
else
    echo "  ❌ Not authenticated or account not verified"
fi
EOF
    chmod +x check_multicloud_status.sh
    
    echo "✅ Management tools created"
}

main() {
    print_header
    print_strategy_table
    print_detailed_roles
    print_architecture_flow
    
    echo -e "${GREEN}🚀 Current Setup Status:${NC}"
    echo ""
    setup_azure_current
    setup_gcp_immediate  
    setup_aws_pending
    setup_oracle_pending
    
    echo -e "${BLUE}📋 Creating multi-cloud configuration...${NC}"
    create_multicloud_config
    create_cost_optimization_dashboard
    create_management_tools
    
    echo ""
    echo -e "${GREEN}🎉 Multi-Cloud Platform Setup Complete!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "1. 🔵 Azure: Add AZURE_CREDENTIALS to GitHub and deploy"
    echo "2. 🟢 GCP: Run 'gcloud auth login' and './deploy_gcp.sh'"
    echo "3. 🟠 AWS: Wait for verification (24-48 hours)"
    echo "4. 🔴 Oracle: Wait for verification (2-5 days)"
    echo ""
    echo "📊 View cost dashboard: open multicloud_cost_dashboard.html"
    echo "🔍 Check status anytime: ./check_multicloud_status.sh"
    echo ""
    echo -e "${CYAN}🌐 Your multi-cloud AI Video GPU platform is ready to scale globally!${NC}"
}

# Run the main function
main
EOF
