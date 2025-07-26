#!/bin/bash

# AI GPU Cloud Platform - Quick Setup Script
# Run this script to set up your AWS infrastructure quickly

echo "🚀 AI GPU Cloud Platform - Quick Setup"
echo "======================================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   pip install awscli"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run:"
    echo "   aws configure"
    exit 1
fi

echo "✅ AWS CLI and credentials verified"

# Set variables
PROJECT_NAME="ai-gpu-cloud"
REGION="us-east-1"
VPC_CIDR="10.0.0.0/16"

echo "📋 Configuration:"
echo "   Project: $PROJECT_NAME"
echo "   Region: $REGION"
echo "   VPC CIDR: $VPC_CIDR"
echo ""

# 1. Create VPC
echo "🌐 Creating VPC..."
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block $VPC_CIDR \
    --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${PROJECT_NAME}-vpc},{Key=Project,Value=${PROJECT_NAME}}]" \
    --query 'Vpc.VpcId' \
    --output text)

if [ $? -eq 0 ]; then
    echo "✅ VPC created: $VPC_ID"
else
    echo "❌ Failed to create VPC"
    exit 1
fi

# 2. Create Internet Gateway
echo "🌐 Creating Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${PROJECT_NAME}-igw}]" \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)

# Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id $IGW_ID \
    --vpc-id $VPC_ID

echo "✅ Internet Gateway created and attached: $IGW_ID"

# 3. Create Public Subnet
echo "🏗️ Creating public subnet..."
SUBNET_ID=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-public-subnet}]" \
    --query 'Subnet.SubnetId' \
    --output text)

echo "✅ Public subnet created: $SUBNET_ID"

# 4. Create Route Table
echo "🛣️ Creating route table..."
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT_NAME}-public-rt}]" \
    --query 'RouteTable.RouteTableId' \
    --output text)

# Add route to Internet Gateway
aws ec2 create-route \
    --route-table-id $ROUTE_TABLE_ID \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

# Associate route table with subnet
aws ec2 associate-route-table \
    --route-table-id $ROUTE_TABLE_ID \
    --subnet-id $SUBNET_ID

echo "✅ Route table created and configured: $ROUTE_TABLE_ID"

# 5. Create Security Groups
echo "🔒 Creating security groups..."

# Web Security Group
WEB_SG_ID=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-web-sg \
    --description "Security group for web servers" \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${PROJECT_NAME}-web-sg}]" \
    --query 'GroupId' \
    --output text)

# Add HTTP and HTTPS rules
aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $WEB_SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

echo "✅ Web security group created: $WEB_SG_ID"

# GPU Security Group
GPU_SG_ID=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-gpu-sg \
    --description "Security group for GPU instances" \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${PROJECT_NAME}-gpu-sg}]" \
    --query 'GroupId' \
    --output text)

# Add SSH and custom GPU ports
aws ec2 authorize-security-group-ingress \
    --group-id $GPU_SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $GPU_SG_ID \
    --protocol tcp \
    --port 8080 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $GPU_SG_ID \
    --protocol tcp \
    --port 8888 \
    --cidr 0.0.0.0/0

echo "✅ GPU security group created: $GPU_SG_ID"

# 6. Create S3 Buckets
echo "📦 Creating S3 buckets..."

BUCKETS=("models" "datasets" "logs" "backups")

for bucket_type in "${BUCKETS[@]}"; do
    BUCKET_NAME="${PROJECT_NAME}-${bucket_type}-$(date +%s)"
    aws s3 mb s3://$BUCKET_NAME --region $REGION
    
    # Add bucket tags
    aws s3api put-bucket-tagging \
        --bucket $BUCKET_NAME \
        --tagging "TagSet=[{Key=Project,Value=${PROJECT_NAME}},{Key=Purpose,Value=${bucket_type}}]"
    
    echo "✅ S3 bucket created: $BUCKET_NAME"
done

# 7. Create Key Pair (optional)
echo "🔑 Creating EC2 Key Pair..."
KEY_NAME="${PROJECT_NAME}-key"
aws ec2 create-key-pair \
    --key-name $KEY_NAME \
    --query 'KeyMaterial' \
    --output text > ${KEY_NAME}.pem

chmod 400 ${KEY_NAME}.pem
echo "✅ Key pair created: ${KEY_NAME}.pem"

# Summary
echo ""
echo "🎉 AI GPU Cloud Platform Setup Complete!"
echo "======================================="
echo "📋 Resources created:"
echo "   VPC ID: $VPC_ID"
echo "   Internet Gateway: $IGW_ID"
echo "   Subnet ID: $SUBNET_ID"
echo "   Route Table: $ROUTE_TABLE_ID"
echo "   Web Security Group: $WEB_SG_ID"
echo "   GPU Security Group: $GPU_SG_ID"
echo "   Key Pair: ${KEY_NAME}.pem"
echo ""
echo "💡 Next steps:"
echo "   1. Launch EC2 instances using the security groups"
echo "   2. Set up auto-scaling groups"
echo "   3. Configure load balancers"
echo "   4. Deploy your AI GPU Cloud application"
echo ""
echo "🚀 Your AI GPU Cloud infrastructure is ready!"
