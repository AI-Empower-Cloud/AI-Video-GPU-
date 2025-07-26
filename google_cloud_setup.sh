#!/bin/bash

# Google Cloud AI GPU Platform Setup - No Verification Required
# Run this after signing up for Google Cloud free tier

echo "🚀 Setting up AI GPU Cloud Platform on Google Cloud"
echo "=================================================="

# Set project variables
PROJECT_ID="ai-gpu-cloud-$(date +%s)"
REGION="us-central1"
ZONE="us-central1-a"

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Zone: $ZONE"
echo ""

# 1. Create new project
echo "📁 Creating Google Cloud project..."
gcloud projects create $PROJECT_ID --name="AI GPU Cloud Platform"
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable ml.googleapis.com

# 3. Create VPC network
echo "🌐 Creating VPC network..."
gcloud compute networks create ai-gpu-vpc --subnet-mode=custom

# 4. Create subnet
echo "🏗️ Creating subnet..."
gcloud compute networks subnets create ai-gpu-subnet \
    --network=ai-gpu-vpc \
    --range=10.0.0.0/24 \
    --region=$REGION

# 5. Create firewall rules
echo "🔒 Creating firewall rules..."
gcloud compute firewall-rules create ai-gpu-allow-ssh \
    --network=ai-gpu-vpc \
    --allow=tcp:22 \
    --source-ranges=0.0.0.0/0

gcloud compute firewall-rules create ai-gpu-allow-http \
    --network=ai-gpu-vpc \
    --allow=tcp:80,tcp:443,tcp:8080 \
    --source-ranges=0.0.0.0/0

# 6. Create Cloud Storage buckets
echo "📦 Creating storage buckets..."
gsutil mb -l $REGION gs://${PROJECT_ID}-models
gsutil mb -l $REGION gs://${PROJECT_ID}-datasets
gsutil mb -l $REGION gs://${PROJECT_ID}-logs

# 7. Create GPU instance template (for later use)
echo "🎯 Creating GPU instance template..."
gcloud compute instance-templates create ai-gpu-template \
    --machine-type=n1-standard-4 \
    --accelerator=count=1,type=nvidia-tesla-t4 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-ssd \
    --network=ai-gpu-vpc \
    --subnet=ai-gpu-subnet \
    --maintenance-policy=TERMINATE \
    --restart-on-failure \
    --tags=ai-gpu-instance

# 8. Create Kubernetes cluster (CPU-only for now)
echo "⚙️ Creating Kubernetes cluster..."
gcloud container clusters create ai-gpu-cluster \
    --zone=$ZONE \
    --machine-type=e2-medium \
    --num-nodes=2 \
    --network=ai-gpu-vpc \
    --subnetwork=ai-gpu-subnet \
    --enable-autorepair \
    --enable-autoupgrade

echo ""
echo "🎉 AI GPU Cloud Platform setup complete on Google Cloud!"
echo "======================================================="
echo "📋 Resources created:"
echo "   Project: $PROJECT_ID"
echo "   VPC: ai-gpu-vpc"
echo "   Subnet: ai-gpu-subnet" 
echo "   Storage: ${PROJECT_ID}-models, -datasets, -logs"
echo "   Kubernetes: ai-gpu-cluster"
echo "   GPU Template: ai-gpu-template"
echo ""
echo "💡 Next steps:"
echo "   1. Access Google Cloud Console"
echo "   2. Launch GPU instances using the template"
echo "   3. Deploy your AI applications"
echo "   4. Scale with Kubernetes"
echo ""
echo "🚀 Your AI GPU Cloud is ready on Google Cloud!"
echo "💰 Using $300 in free credits - no payment required!"
