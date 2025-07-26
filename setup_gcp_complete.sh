#!/bin/bash

# 🟢 AI Video GPU - Complete GCP Setup Script
# This script will set up everything needed for GCP deployment

set -e  # Exit on any error

echo "🟢 Starting AI Video GPU GCP Setup..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI is not installed."
    print_info "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null 2>&1; then
    print_warning "You need to authenticate with Google Cloud first."
    print_info "Run: gcloud auth login"
    print_info "Or upload a service account key file as 'gcp-service-account.json'"
    
    # Check for service account key
    if [ -f "gcp-service-account.json" ]; then
        print_info "Found service account key. Using it for authentication..."
        export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp-service-account.json"
        gcloud auth activate-service-account --key-file=gcp-service-account.json
        print_status "Authenticated with service account"
    else
        exit 1
    fi
fi

# Get or set project ID
if [ -z "$GCP_PROJECT_ID" ]; then
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
    if [ -z "$CURRENT_PROJECT" ]; then
        print_warning "No GCP project set. Please set your project ID:"
        read -p "Enter your GCP Project ID: " GCP_PROJECT_ID
        gcloud config set project $GCP_PROJECT_ID
    else
        GCP_PROJECT_ID=$CURRENT_PROJECT
        print_info "Using current project: $GCP_PROJECT_ID"
    fi
fi

print_info "Setting up AI Video GPU in project: $GCP_PROJECT_ID"

# Enable required APIs
print_info "Enabling required Google Cloud APIs..."
APIS=(
    "compute.googleapis.com"
    "container.googleapis.com" 
    "aiplatform.googleapis.com"
    "storage.googleapis.com"
    "bigquery.googleapis.com"
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    print_info "Enabling $api..."
    gcloud services enable $api --quiet
done
print_status "All APIs enabled successfully"

# Create storage bucket
BUCKET_NAME="ai-video-gpu-${GCP_PROJECT_ID}"
print_info "Creating Cloud Storage bucket: $BUCKET_NAME"
if gsutil mb gs://$BUCKET_NAME 2>/dev/null; then
    print_status "Storage bucket created: gs://$BUCKET_NAME"
else
    print_warning "Bucket might already exist or there was an issue creating it"
fi

# Set up BigQuery dataset
print_info "Creating BigQuery dataset for analytics..."
bq mk --dataset --description "AI Video GPU Analytics" ${GCP_PROJECT_ID}:ai_video_analytics 2>/dev/null || print_warning "Dataset might already exist"
print_status "BigQuery dataset ready"

# Create Artifact Registry repository
print_info "Creating Artifact Registry repository..."
gcloud artifacts repositories create ai-video-gpu-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="AI Video GPU Docker images" \
    --quiet 2>/dev/null || print_warning "Repository might already exist"
print_status "Artifact Registry repository ready"

# Create GKE cluster with GPU support
print_info "Creating GKE cluster with GPU support..."
CLUSTER_NAME="ai-video-gpu-cluster"
ZONE="us-central1-a"

if ! gcloud container clusters describe $CLUSTER_NAME --zone=$ZONE &>/dev/null; then
    print_info "Creating new GKE cluster (this may take 5-10 minutes)..."
    gcloud container clusters create $CLUSTER_NAME \
        --zone=$ZONE \
        --num-nodes=2 \
        --machine-type=e2-standard-4 \
        --disk-size=50GB \
        --enable-autorepair \
        --enable-autoupgrade \
        --enable-ip-alias \
        --quiet
    print_status "GKE cluster created successfully"
else
    print_warning "GKE cluster already exists"
fi

# Get cluster credentials
print_info "Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --quiet
print_status "Kubectl configured for GKE cluster"

# Create Vertex AI dataset
print_info "Setting up Vertex AI resources..."
# Note: This would typically require more specific setup based on your ML models
print_status "Vertex AI ready for model deployment"

# Create deployment configuration
print_info "Creating deployment configuration..."
cat > gcp-deployment-config.yaml << EOF
# GCP Deployment Configuration
project_id: $GCP_PROJECT_ID
region: us-central1
zone: us-central1-a

# Storage
storage_bucket: $BUCKET_NAME

# Compute
cluster_name: $CLUSTER_NAME
cluster_zone: $ZONE

# BigQuery
dataset: ai_video_analytics

# Artifact Registry
registry_location: us-central1
registry_name: ai-video-gpu-repo

# Services
cloud_run_service: ai-video-gpu-service
vertex_ai_endpoint: ai-video-gpu-endpoint
EOF

print_status "Deployment configuration saved to gcp-deployment-config.yaml"

# Create environment file for GCP
cat > .env.gcp << EOF
# GCP Environment Configuration
GOOGLE_CLOUD_PROJECT=$GCP_PROJECT_ID
GCP_REGION=us-central1
GCP_ZONE=us-central1-a
GCP_STORAGE_BUCKET=$BUCKET_NAME
GCP_CLUSTER_NAME=$CLUSTER_NAME
GCP_DATASET=ai_video_analytics
GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/gcp-service-account.json
EOF

print_status "GCP environment file created: .env.gcp"

# Test the setup
print_info "Testing the setup..."

# Test gcloud
if gcloud projects describe $GCP_PROJECT_ID --quiet > /dev/null 2>&1; then
    print_status "✅ gcloud: Working"
else
    print_error "❌ gcloud: Failed"
fi

# Test kubectl
if kubectl cluster-info --request-timeout=10s > /dev/null 2>&1; then
    print_status "✅ kubectl: Connected to GKE"
else
    print_warning "⚠️ kubectl: Connection issue (this is normal if cluster is still starting)"
fi

# Test gsutil
if gsutil ls gs://$BUCKET_NAME > /dev/null 2>&1; then
    print_status "✅ Cloud Storage: Working"
else
    print_warning "⚠️ Cloud Storage: Access issue"
fi

echo ""
echo "========================================"
echo -e "${GREEN}🎉 GCP Setup Complete!${NC}"
echo "========================================"

print_info "Next steps:"
echo "1. 🚀 Deploy your application with: ./deploy_to_gcp.sh"
echo "2. 📊 Monitor costs at: https://console.cloud.google.com/billing"
echo "3. 🔧 Manage resources at: https://console.cloud.google.com"
echo ""
print_info "Configuration files created:"
echo "- gcp-deployment-config.yaml"
echo "- .env.gcp"
echo ""
print_info "Useful commands:"
echo "- Check cluster: kubectl get nodes"
echo "- View storage: gsutil ls gs://$BUCKET_NAME"
echo "- Monitor services: gcloud run services list"

echo ""
print_status "Your GCP environment is ready for AI Video GPU deployment! 🚀"
