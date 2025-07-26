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
