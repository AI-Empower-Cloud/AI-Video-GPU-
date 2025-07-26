#!/bin/bash

# Google Cloud GPU Setup for 4K Video Processing
# Run this after signing up for Google Cloud $300 free credits

echo "🎬 Setting up Google Cloud GPU Infrastructure for 4K Video Processing"
echo "===================================================================="

# Configuration
PROJECT_ID="ai-video-gpu-$(date +%s)"
REGION="us-central1"
ZONE="us-central1-a"
GPU_ZONE="us-central1-b"  # Better GPU availability

echo "📋 Google Cloud Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   GPU Zone: $GPU_ZONE"
echo ""

# 1. Create new project
echo "📁 Creating Google Cloud project..."
gcloud projects create $PROJECT_ID --name="AI Video GPU Platform"
gcloud config set project $PROJECT_ID

# 2. Enable required APIs for video processing
echo "🔧 Enabling video processing APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable ml.googleapis.com
gcloud services enable videointelligence.googleapis.com
gcloud services enable vision.googleapis.com
gcloud services enable translate.googleapis.com

# 3. Create VPC for video processing
echo "🌐 Creating VPC network..."
gcloud compute networks create ai-video-gpu-vpc --subnet-mode=custom

# 4. Create subnet with larger IP range for video processing
echo "🏗️ Creating subnet..."
gcloud compute networks subnets create ai-video-gpu-subnet \
    --network=ai-video-gpu-vpc \
    --range=10.1.0.0/16 \
    --region=$REGION

# 5. Create firewall rules for video services
echo "🔒 Creating firewall rules..."
gcloud compute firewall-rules create ai-video-allow-ssh \
    --network=ai-video-gpu-vpc \
    --allow=tcp:22 \
    --source-ranges=0.0.0.0/0

gcloud compute firewall-rules create ai-video-allow-http \
    --network=ai-video-gpu-vpc \
    --allow=tcp:80,tcp:443,tcp:8080,tcp:5000 \
    --source-ranges=0.0.0.0/0

gcloud compute firewall-rules create ai-video-allow-streaming \
    --network=ai-video-gpu-vpc \
    --allow=tcp:1935,tcp:8000-8999 \
    --source-ranges=0.0.0.0/0

# 6. Create Cloud Storage buckets for video processing
echo "📦 Creating video storage buckets..."
gsutil mb -l $REGION gs://${PROJECT_ID}-raw-videos
gsutil mb -l $REGION gs://${PROJECT_ID}-processed-videos
gsutil mb -l $REGION gs://${PROJECT_ID}-ai-models
gsutil mb -l $REGION gs://${PROJECT_ID}-thumbnails
gsutil mb -l $REGION gs://${PROJECT_ID}-temp-processing

# Set public access for processed videos
gsutil iam ch allUsers:objectViewer gs://${PROJECT_ID}-processed-videos
gsutil iam ch allUsers:objectViewer gs://${PROJECT_ID}-thumbnails

# 7. Create GPU instance template for video processing
echo "🎯 Creating GPU instance template for 4K video processing..."
gcloud compute instance-templates create ai-video-gpu-template \
    --machine-type=n1-standard-8 \
    --accelerator=count=1,type=nvidia-tesla-t4 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB \
    --boot-disk-type=pd-ssd \
    --local-ssd=interface=nvme \
    --network=ai-video-gpu-vpc \
    --subnet=ai-video-gpu-subnet \
    --maintenance-policy=TERMINATE \
    --restart-on-failure \
    --preemptible \
    --tags=ai-video-gpu \
    --metadata=startup-script='#!/bin/bash
    # Install NVIDIA drivers
    curl -O https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
    sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda-repo-ubuntu2004-12-2-local_12.2.0-535.54.03-1_amd64.deb
    sudo dpkg -i cuda-repo-ubuntu2004-12-2-local_12.2.0-535.54.03-1_amd64.deb
    sudo cp /var/cuda-repo-ubuntu2004-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/
    sudo apt-get update
    sudo apt-get -y install cuda
    
    # Install FFmpeg with GPU support
    sudo apt update
    sudo apt install -y ffmpeg
    
    # Install Python and video processing libraries
    sudo apt install -y python3-pip python3-dev
    pip3 install opencv-python-headless moviepy torch torchvision transformers
    
    # Install Google Cloud SDK
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
    '

# 8. Create high-memory instance template for large video files
echo "💾 Creating high-memory instance template..."
gcloud compute instance-templates create ai-video-highmem-template \
    --machine-type=n1-highmem-8 \
    --accelerator=count=1,type=nvidia-tesla-v100 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=200GB \
    --boot-disk-type=pd-ssd \
    --local-ssd=interface=nvme,size=375 \
    --network=ai-video-gpu-vpc \
    --subnet=ai-video-gpu-subnet \
    --maintenance-policy=TERMINATE \
    --restart-on-failure \
    --preemptible \
    --tags=ai-video-highmem

# 9. Create managed instance group for auto-scaling
echo "⚙️ Creating managed instance group..."
gcloud compute instance-groups managed create ai-video-gpu-group \
    --template=ai-video-gpu-template \
    --size=0 \
    --zone=$GPU_ZONE

# Set up auto-scaling based on CPU usage
gcloud compute instance-groups managed set-autoscaling ai-video-gpu-group \
    --zone=$GPU_ZONE \
    --min-num-replicas=0 \
    --max-num-replicas=5 \
    --target-cpu-utilization=0.7 \
    --cool-down-period=300

# 10. Create load balancer for video services
echo "⚖️ Creating load balancer..."
gcloud compute health-checks create http ai-video-health-check \
    --port=8080 \
    --request-path=/health

gcloud compute backend-services create ai-video-backend \
    --health-checks=ai-video-health-check \
    --global

gcloud compute backend-services add-backend ai-video-backend \
    --instance-group=ai-video-gpu-group \
    --instance-group-zone=$GPU_ZONE \
    --global

# 11. Create Cloud Function for video processing triggers
echo "⚡ Setting up Cloud Functions..."
mkdir -p /tmp/video-trigger-function
cat > /tmp/video-trigger-function/main.py << 'EOF'
import functions_framework
from google.cloud import compute_v1
import json

@functions_framework.cloud_event
def trigger_video_processing(cloud_event):
    """Triggered when a video is uploaded to trigger GPU processing"""
    
    # Get file info from Cloud Storage event
    file_data = cloud_event.data
    bucket_name = file_data['bucket']
    file_name = file_data['name']
    
    if file_name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        # Scale up GPU instances for video processing
        compute_client = compute_v1.InstanceGroupManagersClient()
        
        operation = compute_client.resize(
            request={
                "project": "PROJECT_ID",
                "zone": "GPU_ZONE", 
                "instance_group_manager": "ai-video-gpu-group",
                "size": 2  # Scale to 2 instances
            }
        )
        
        print(f"Scaling GPU instances for video: {file_name}")
    
    return 'OK'
EOF

cat > /tmp/video-trigger-function/requirements.txt << 'EOF'
functions-framework==3.*
google-cloud-compute==1.*
EOF

# Deploy the function
gcloud functions deploy trigger-video-processing \
    --runtime=python39 \
    --trigger-bucket=${PROJECT_ID}-raw-videos \
    --source=/tmp/video-trigger-function \
    --entry-point=trigger_video_processing

echo ""
echo "🎉 Google Cloud GPU Setup Complete for 4K Video Processing!"
echo "=========================================================="
echo "📋 Resources created:"
echo "   Project: $PROJECT_ID"
echo "   VPC: ai-video-gpu-vpc"
echo "   GPU Template: T4 & V100 instances"
echo "   Storage: 5x video processing buckets"
echo "   Auto-scaling: 0-5 GPU instances"
echo "   Load Balancer: Global distribution"
echo "   Cloud Function: Auto-scaling trigger"
echo ""
echo "💰 Cost optimization:"
echo "   Preemptible instances: 60-90% cheaper"
echo "   Auto-scaling: Pay only when processing"
echo "   Local SSD: Fast temporary storage"
echo ""
echo "🎬 Perfect for:"
echo "   4K video rendering and processing"
echo "   AI video generation and effects"
echo "   Real-time video streaming"
echo "   Batch video processing"
echo ""
echo "🚀 Your Google Cloud GPU infrastructure is ready!"
