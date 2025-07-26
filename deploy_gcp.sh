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
