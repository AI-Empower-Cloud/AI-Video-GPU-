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
